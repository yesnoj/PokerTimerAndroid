#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Finestra principale dell'applicazione Poker Timer con correzioni per floorman
"""

import os
import time
import threading

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QPushButton, QFrame, QGridLayout, QScrollArea,
                            QSpinBox, QCheckBox, QGroupBox, QMessageBox, QSplitter,
                            QSizePolicy, QRadioButton, QButtonGroup, QMenu, QMenuBar,
                            QDialog, QFormLayout, QDialogButtonBox)  # Assicurati che QDialog sia qui

from PyQt6.QtCore import Qt, QTimer, QSettings, pyqtSlot
from PyQt6.QtGui import QFont, QIcon, QAction

from .timer_card import TimerCard
from .notifications import NotificationManager
from server import PokerTimerServer
from .ngrok_integration import NgrokConfigDialog, NgrokService





class ServerSettingsDialog(QDialog):
    """Dialog per le impostazioni del server"""
    def __init__(self, parent=None, http_port=3000, discovery_port=8888, autostart=False):
        super().__init__(parent)
        
        self.setWindowTitle("Impostazioni Server")
        self.setMinimumWidth(400)
        
        # Layout principale
        layout = QVBoxLayout(self)
        
        # Utilizziamo un layout a griglia invece del form layout per un controllo migliore
        grid_layout = QGridLayout()
        grid_layout.setVerticalSpacing(20)  # Aumentiamo lo spazio verticale tra le righe
        grid_layout.setHorizontalSpacing(10)
        
        # Etichette con altezza fissa e allineate a destra
        http_label = QLabel("Porta HTTP:")
        http_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        http_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        grid_layout.addWidget(http_label, 0, 0)
        
        # HTTP Port con altezza fissa e allineato a destra
        self.http_port_spin = QSpinBox()
        self.http_port_spin.setRange(1024, 65535)
        self.http_port_spin.setValue(http_port)
        self.http_port_spin.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        self.http_port_spin.setMinimumWidth(100)
        self.http_port_spin.setFixedHeight(30)  # Altezza fissa per uniformità
        self.http_port_spin.setAlignment(Qt.AlignmentFlag.AlignRight)
        grid_layout.addWidget(self.http_port_spin, 0, 1)
        
        # Discovery Port con stile simile
        discovery_label = QLabel("Porta Discovery:")
        discovery_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        discovery_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        grid_layout.addWidget(discovery_label, 1, 0)
        
        self.udp_port_spin = QSpinBox()
        self.udp_port_spin.setRange(1024, 65535)
        self.udp_port_spin.setValue(discovery_port)
        self.udp_port_spin.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        self.udp_port_spin.setMinimumWidth(100)
        self.udp_port_spin.setFixedHeight(30)  # Altezza fissa per uniformità
        self.udp_port_spin.setAlignment(Qt.AlignmentFlag.AlignRight)
        grid_layout.addWidget(self.udp_port_spin, 1, 1)
        
        # Autostart checkbox
        self.autostart_check = QCheckBox("Avvia server automaticamente")
        self.autostart_check.setChecked(autostart)
        grid_layout.addWidget(self.autostart_check, 2, 0, 1, 2, Qt.AlignmentFlag.AlignCenter)
        
        # Aggiungiamo il layout griglia al layout principale
        layout.addLayout(grid_layout)
        
        # Aggiungiamo un po' di spazio prima dei bottoni
        layout.addSpacing(20)
        
        # Bottoni standard con stile personalizzato
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        # Personalizziamo i bottoni
        ok_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
        ok_button.setText("OK")
        ok_button.setStyleSheet("background-color: #2e7d32; color: white; padding: 6px 20px; font-weight: bold;")
        
        cancel_button = button_box.button(QDialogButtonBox.StandardButton.Cancel)
        cancel_button.setText("Cancel")
        cancel_button.setStyleSheet("background-color: #6c757d; color: white; padding: 6px 20px;")
        
        layout.addWidget(button_box)
    
    def get_settings(self):
        """Restituisce le impostazioni selezionate"""
        return {
            'http_port': self.http_port_spin.value(),
            'discovery_port': self.udp_port_spin.value(),
            'autostart': self.autostart_check.isChecked()
        }

class MainWindow(QMainWindow):
    """Finestra principale dell'applicazione Poker Timer con correzioni per floorman"""

    def __init__(self):
        super().__init__()
        
        # Impostazioni
        self.settings = QSettings("PokerTimer", "Monitor")
        
        # Configura la finestra
        self.setWindowTitle("Poker Timer Monitor")
        self.setMinimumSize(800, 600)
        
        # Server e dati
        self.http_port = self.settings.value("http_port", 3000, int)
        self.discovery_port = self.settings.value("discovery_port", 8888, int)
        self.show_offline = self.settings.value("show_filter", "only_online", str)
        
        self.server = PokerTimerServer(port=self.http_port, discovery_port=self.discovery_port)
        self.is_server_running = False
        
        # Dizionario per memorizzare i riferimenti alle card
        self.timer_cards = {}
        
        # Dizionario per memorizzare le chiamate floorman attive
        self.active_floorman_calls = {}
        
        # Gestore notifiche
        self.notification_manager = NotificationManager()
        
        # Configurazione ngrok
        self.ngrok_active = False
        self.ngrok_public_url = None
        self.setup_ngrok()
        
        # Connessione segnali del server
        self.server.timer_updated.connect(self.on_timer_updated)
        self.server.timer_connected.connect(self.on_timer_connected)
        self.server.seat_notification.connect(self.on_seat_notification)
        self.server.floorman_notification.connect(self.on_floorman_notification)
        self.server.bar_service_notification.connect(self.on_bar_service_notification)
        
        # Lock per evitare aggiornamenti concorrenti
        self.update_lock = threading.Lock()
        self.last_full_update = 0  # Timestamp dell'ultimo aggiornamento completo
        
        # Crea la barra dei menu
        self.create_menu_bar()
        
        # Widget centrale
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)
        
        # Pannello superiore (filtri e stato)
        top_panel = self.create_top_panel()
        main_layout.addWidget(top_panel)
        
        # Area di scorrimento per i timer
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setMinimumHeight(400)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setStyleSheet("background-color: #f5f5f5;")
        
        self.timer_container = QWidget()
        self.timer_container.setStyleSheet("background-color: #f5f5f5;")
        self.grid_layout = QGridLayout(self.timer_container)
        self.grid_layout.setSpacing(20)
        self.grid_layout.setContentsMargins(20, 20, 20, 20)
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        
        self.scroll_area.setWidget(self.timer_container)
        main_layout.addWidget(self.scroll_area)
        
        # Etichetta per quando non ci sono timer
        self.no_timers_label = QLabel("Nessun timer connesso")
        self.no_timers_label.setObjectName("no-timers-label")
        self.no_timers_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.no_timers_label.setStyleSheet("font-size: 16pt; color: #333333; font-weight: bold; padding: 20px;")
        self.grid_layout.addWidget(self.no_timers_label, 0, 0, 1, 3)
        
        # Timer per aggiornamenti periodici
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_timers_automatic)
        self.update_timer.start(5000)  # 5 secondi
        
        # Barra di stato
        self.statusBar().showMessage("Server Poker Timer pronto")
        self.statusBar().setFont(QFont("Arial", 12))
        
        # Posiziona la finestra al centro dello schermo
        self.center_window()
        
        # Correggiamo lo stile per i menu
        self.fix_menu_alignment()
        
        # Autostart del server se era attivo alla chiusura
        if self.settings.value("autostart_server", False, bool):
            self.start_server()
    
    def fix_menu_alignment(self):
        """Corregge l'allineamento delle voci di menu"""
        # Impostiamo lo stile per allineare i menu a sinistra
        style = """
        QMenu {
            text-align: left;
        }
        QMenu::item {
            text-align: left;
            padding-left: 15px;
            padding-right: 15px;
            padding-top: 5px;
            padding-bottom: 5px;
        }
        QMenuBar {
            text-align: left;
        }
        QMenuBar::item {
            text-align: left;
            padding-left: 10px;
            padding-right: 10px;
            padding-top: 2px;
        }
        """
        self.setStyleSheet(style)
    
    def create_menu_bar(self):
        """Crea la barra dei menu dell'applicazione"""
        menu_bar = self.menuBar()
        
        # Menu Server
        server_menu = menu_bar.addMenu("Server")
        
        # Azione Avvia/Ferma Server
        self.server_action = QAction("Avvia Server", self)
        self.server_action.triggered.connect(self.toggle_server)
        server_menu.addAction(self.server_action)
        
        server_menu.addSeparator()
        
        # Azione Impostazioni
        settings_action = QAction("Impostazioni Server", self)
        settings_action.triggered.connect(self.show_server_settings)
        server_menu.addAction(settings_action)
        
        # Aggiungi nuova azione per ngrok
        self.ngrok_action = QAction("Configura Accesso Esterno", self)
        self.ngrok_action.triggered.connect(self.show_ngrok_config)
        server_menu.addAction(self.ngrok_action)
        
        server_menu.addSeparator()
        
        # Aggiungi azione per generare QR code
        generate_qr_action = QAction("Genera QR Code", self)
        generate_qr_action.triggered.connect(self.show_qr_generator_dialog)
        server_menu.addAction(generate_qr_action)
        
        server_menu.addSeparator()
        
        # Azione Esci
        exit_action = QAction("Esci", self)
        exit_action.triggered.connect(self.close)
        server_menu.addAction(exit_action)
        
        # Menu Aiuto
        help_menu = menu_bar.addMenu("Aiuto")
        
        # Azione Informazioni
        about_action = QAction("Informazioni", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def show_ngrok_config(self):
        """Mostra il dialog di configurazione ngrok"""
        # Ottieni il token salvato dalle impostazioni, se esiste
        authtoken = self.settings.value("ngrok_authtoken", "", str)
        autostart = self.settings.value("ngrok_autostart", False, bool)
        
        # Crea e mostra il dialog
        dialog = NgrokConfigDialog(
            self,
            http_port=self.http_port,
            authtoken=authtoken
        )
        
        # Imposta lo stato di autostart
        dialog.autostart_check.setChecked(autostart)
        
        # Mostra il dialog in modalità modale
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Salva le impostazioni
            settings = dialog.get_settings()
            self.settings.setValue("ngrok_authtoken", settings['authtoken'])
            self.settings.setValue("ngrok_autostart", settings['autostart'])
            
            # Se il tunnel è attivo, memorizza il suo stato
            self.ngrok_active = settings['is_running']
            if self.ngrok_active:
                self.ngrok_public_url = settings['public_url']
                # Mostra info nella barra di stato
                self.statusBar().showMessage(f"Server locale accessibile da: {self.ngrok_public_url}")
            else:
                self.ngrok_public_url = None


    # Aggiungi questo metodo alla classe MainWindow
    def setup_ngrok(self):
        """Configura il servizio ngrok"""
        # Crea l'istanza del servizio
        self.ngrok_service = NgrokService(http_port=self.http_port)
        
        # Connetti i segnali
        self.ngrok_service.tunnel_started.connect(self.on_ngrok_tunnel_started)
        self.ngrok_service.tunnel_stopped.connect(self.on_ngrok_tunnel_stopped)
        self.ngrok_service.tunnel_error.connect(self.on_ngrok_tunnel_error)
        
        # Avvia automaticamente se configurato
        if self.settings.value("ngrok_autostart", False, bool):
            authtoken = self.settings.value("ngrok_authtoken", "", str)
            if authtoken:
                self.ngrok_service.start_tunnel(authtoken)


    # Aggiungi questi metodi alla classe MainWindow
    def on_ngrok_tunnel_started(self, public_url):
        """Gestisce l'evento di avvio del tunnel ngrok"""
        self.ngrok_active = True
        self.ngrok_public_url = public_url
        
        # Aggiorna la barra di stato
        self.statusBar().showMessage(f"Server locale accessibile da: {public_url}")
        
        # Aggiorna eventuali QR code generati con il nuovo URL
        # Se implementi un sistema di QR code, potrebbe essere necessario rigenerarli qui


    def on_ngrok_tunnel_stopped(self):
        """Gestisce l'evento di arresto del tunnel ngrok"""
        self.ngrok_active = False
        self.ngrok_public_url = None
        
        # Aggiorna la barra di stato
        if self.is_server_running:
            self.statusBar().showMessage(f"Server avviato su porta {self.http_port}, discovery su porta {self.discovery_port}")
        else:
            self.statusBar().showMessage("Server fermato")


    def on_ngrok_tunnel_error(self, error_message):
        """Gestisce gli errori del tunnel ngrok"""
        self.ngrok_active = False
        self.ngrok_public_url = None
        
        # Mostra l'errore nella barra di stato
        self.statusBar().showMessage(f"Errore ngrok: {error_message}")

    
    def show_server_settings(self):
        """Mostra la finestra di dialogo per le impostazioni del server"""
        dialog = ServerSettingsDialog(
            self,
            http_port=self.http_port,
            discovery_port=self.discovery_port,
            autostart=self.settings.value("autostart_server", False, bool)
        )
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            settings = dialog.get_settings()
            
            # Aggiorna le impostazioni
            self.http_port = settings['http_port']
            self.discovery_port = settings['discovery_port']
            
            # Salva le impostazioni
            self.settings.setValue("http_port", self.http_port)
            self.settings.setValue("discovery_port", self.discovery_port)
            self.settings.setValue("autostart_server", settings['autostart'])
            
            # Se il server è attivo, chiedi di riavviarlo
            if self.is_server_running:
                reply = QMessageBox.question(
                    self,
                    'Riavvio Server',
                    'Le impostazioni sono state modificate. Vuoi riavviare il server?',
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.Yes
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    self.stop_server()
                    self.start_server()
    
    def show_about(self):
        """Mostra la finestra di informazioni"""
        QMessageBox.about(
            self,
            "Informazioni",
            """<h1>Poker Timer Monitor</h1>
            <p>Applicazione per il monitoraggio dei timer da poker.</p>
            <p>Versione: 1.0</p>
            <p>© 2024 Poker Timer</p>"""
        )
    
    def center_window(self):
        """Centra la finestra sullo schermo"""
        frame_geometry = self.frameGeometry()
        screen_center = self.screen().availableGeometry().center()
        frame_geometry.moveCenter(screen_center)
        self.move(frame_geometry.topLeft())
    
    def create_top_panel(self):
        """Crea il pannello superiore con filtri e stato"""
        panel = QFrame()
        panel.setFrameStyle(QFrame.Shape.StyledPanel)
        panel.setStyleSheet("background-color: #f0f0f0; border-radius: 8px; padding: 15px; border: 2px solid #9e9e9e;")
        
        # Layout flessibile per adattarsi a schermi più piccoli
        layout = QHBoxLayout(panel)
        layout.setSpacing(20)
        
        # Gruppo filtro a sinistra
        filter_group = QGroupBox("Filtro")
        filter_group.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        filter_layout = QHBoxLayout(filter_group)
        
        # Radio button per i filtri
        self.filter_all_radio = QRadioButton("Mostra tutti")
        self.filter_online_radio = QRadioButton("Mostra Online")
        self.filter_offline_radio = QRadioButton("Mostra Offline")
        
        # Raggruppiamo i radio button
        self.filter_radio_group = QButtonGroup(self)
        self.filter_radio_group.addButton(self.filter_all_radio, 0)
        self.filter_radio_group.addButton(self.filter_online_radio, 1)
        self.filter_radio_group.addButton(self.filter_offline_radio, 2)
        
        # Impostazione dello stile
        radio_style = "font-size: 12pt;"
        self.filter_all_radio.setStyleSheet(radio_style)
        self.filter_online_radio.setStyleSheet(radio_style)
        self.filter_offline_radio.setStyleSheet(radio_style)
        
        # Impostiamo il valore di default
        if self.show_offline == "all":
            self.filter_all_radio.setChecked(True)
        elif self.show_offline == "only_offline":
            self.filter_offline_radio.setChecked(True)
        else:  # "only_online" o valore predefinito
            self.filter_online_radio.setChecked(True)
        
        # Connessione dei segnali
        self.filter_radio_group.buttonClicked.connect(self.on_filter_changed)
        
        # Aggiunta dei radio button al layout
        filter_layout.addWidget(self.filter_all_radio)
        filter_layout.addWidget(self.filter_online_radio)
        filter_layout.addWidget(self.filter_offline_radio)
        
        layout.addWidget(filter_group)
        
        # Stretch per spingere lo stato del server a destra
        layout.addStretch(1)
        
        # Informazioni sul server a destra
        info_layout = QVBoxLayout()
        
        self.status_label = QLabel("Server: Non attivo")
        self.status_label.setObjectName("status-label-inactive")
        self.status_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        info_layout.addWidget(self.status_label)
        
        self.timer_count = QLabel("Timer connessi: 0")
        self.timer_count.setFont(QFont("Arial", 14))
        info_layout.addWidget(self.timer_count)
        
        layout.addLayout(info_layout)
        
        return panel
    
    def on_filter_changed(self, button):
        """Gestisce il cambio del filtro dei timer"""
        if button == self.filter_all_radio:
            self.show_offline = "all"
        elif button == self.filter_offline_radio:
            self.show_offline = "only_offline"
        else:  # filter_online_radio
            self.show_offline = "only_online"
        
        # Salva l'impostazione
        self.settings.setValue("show_filter", self.show_offline)
        
        # Aggiorna la visualizzazione
        self.update_timers()
    
    def toggle_server(self):
        """Avvia o ferma il server"""
        if self.is_server_running:
            self.stop_server()
        else:
            self.start_server()
    
    def start_server(self):
        """Avvia il server"""
        try:
            # Crea una nuova istanza del server con le porte aggiornate
            self.server = PokerTimerServer(port=self.http_port, discovery_port=self.discovery_port)
            
            # Connetti i segnali
            self.server.timer_updated.connect(self.on_timer_updated)
            self.server.timer_connected.connect(self.on_timer_connected)
            self.server.seat_notification.connect(self.on_seat_notification)
            self.server.floorman_notification.connect(self.on_floorman_notification)
            self.server.bar_service_notification.connect(self.on_bar_service_notification)
            
            # Avvia il server
            self.server.start()
            
            # Aggiorna l'interfaccia
            self.is_server_running = True
            self.server_action.setText("Ferma Server")
            self.status_label.setText("Server: Attivo")
            self.status_label.setObjectName("status-label-active")
            
            # Aggiorna la barra di stato
            if self.ngrok_active and self.ngrok_public_url:
                self.statusBar().showMessage(f"Server avviato su porta {self.http_port} - Accessibile da: {self.ngrok_public_url}")
            else:
                self.statusBar().showMessage(f"Server avviato su porta {self.http_port}, discovery su porta {self.discovery_port}")
            
            # Avvia ngrok se autostart è configurato
            if self.settings.value("ngrok_autostart", False, bool) and not self.ngrok_active:
                authtoken = self.settings.value("ngrok_authtoken", "", str)
                if authtoken:
                    self.ngrok_service.start_tunnel(authtoken)
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Impossibile avviare il server: {str(e)}")

            
    def stop_server(self):
        """Ferma il server"""
        try:
            # Ferma il server
            self.server.stop()
            
            # Aggiorna l'interfaccia
            self.is_server_running = False
            self.server_action.setText("Avvia Server")
            self.status_label.setText("Server: Non attivo")
            self.status_label.setObjectName("status-label-inactive")
            
            # Aggiorna la barra di stato
            self.statusBar().showMessage("Server fermato")
            
            # Ferma ngrok se configurato per avviarsi solo con il server
            if self.ngrok_active and not self.settings.value("ngrok_keep_running", False, bool):
                self.ngrok_service.stop_tunnel()
            
            # Pulisci tutte le card e mostra "Nessun timer connesso"
            for device_id in list(self.timer_cards.keys()):
                card = self.timer_cards.pop(device_id)
                self.grid_layout.removeWidget(card)
                card.setParent(None)
                card.deleteLater()
            
            # Assicurati che l'etichetta "Nessun timer connesso" sia visibile
            if self.no_timers_label.parent() is None:
                self.grid_layout.addWidget(self.no_timers_label, 0, 0, 1, 3)
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore nella chiusura del server: {str(e)}")

    def update_timers_automatic(self):
        """Aggiorna solo i dati delle card esistenti senza ricostruire l'interfaccia"""
        if not self.is_server_running:
            return
            
        # Usa un lock per evitare aggiornamenti concorrenti
        if not self.update_lock.acquire(blocking=False):
            return  # Un altro aggiornamento è in corso, esci
            
        try:
            # Controlla se è necessario un aggiornamento completo
            current_time = time.time()
            if current_time - self.last_full_update > 30:  # Ogni 30 secondi fai un aggiornamento completo
                self.update_timers()
                self.last_full_update = current_time
                return
                
            # Ottieni i timer dal server
            timers = self.server.timers
            online_timers = []
            offline_timers = []
            
            # Aggiorna lo stato di connessione dei timer
            for timer_id, timer_data in timers.items():
                timer_data['is_online'] = self.server.is_timer_online(timer_data)
                if timer_data['is_online']:
                    online_timers.append(timer_id)
                else:
                    offline_timers.append(timer_id)
            
            # Aggiorna il contatore dei timer
            self.timer_count.setText(f"Timer connessi: {len(online_timers)} online, {len(offline_timers)} offline")
            
            # Aggiorna solo i dati delle card esistenti
            cards_to_update = list(self.timer_cards.keys())
            
            for device_id in cards_to_update:
                if device_id in timers:
                    timer_data = timers[device_id]
                    timer_data['is_online'] = self.server.is_timer_online(timer_data)
                    
                    # Aggiorna solo se ci sono modifiche significative
                    current_card_data = self.timer_cards[device_id].timer_data
                    if self._has_significant_changes(current_card_data, timer_data):
                        self.timer_cards[device_id].update_data(timer_data)
            
        except Exception as e:
            print(f"Errore in update_timers_automatic: {e}")
        finally:
            self.update_lock.release()

    def _has_significant_changes(self, old_data, new_data):
        """
        Controlla se ci sono modifiche significative tra i dati vecchi e nuovi
        Per evitare aggiornamenti inutili delle card
        """
        # Lista dei campi da confrontare per verificare modifiche significative
        fields_to_check = [
            'is_running', 
            'is_paused', 
            'table_number', 
            'battery_level', 
            'wifi_quality', 
            'buzzer', 
            'seat_info',
            't1_value',
            't2_value',
            'voltage',
            'last_update',
            'is_online',       # Aggiunto per verificare cambiamenti online/offline
            'is_t1_active',    # Aggiunto per verificare cambiamenti T1/T2
            'current_timer'    # Aggiunto per verificare cambiamenti nel timer attuale
        ]
        
        for field in fields_to_check:
            old_value = old_data.get(field)
            new_value = new_data.get(field)
            
            # Confronto speciale per seat_info
            if field == 'seat_info':
                old_seats = old_value.get('open_seats', []) if old_value else []
                new_seats = new_value.get('open_seats', []) if new_value else []
                if set(old_seats) != set(new_seats):
                    return True
                continue
            
            # Per tutti gli altri campi
            if old_value != new_value:
                return True
        
        return False
    
    def update_timers(self):
        """Aggiorna la visualizzazione dei timer in modo efficiente (ricostruzione completa)"""
        if not self.is_server_running:
            return
        
        # Usa un lock per evitare aggiornamenti concorrenti
        if not self.update_lock.acquire(blocking=False):
            return  # Un altro aggiornamento è in corso, esci
            
        try:
            # Ottieni i timer dal server
            timers = self.server.timers
            
            # Conta i timer online/offline
            online_timers = []
            offline_timers = []
            for timer_id, timer_data in timers.items():
                timer_data['is_online'] = self.server.is_timer_online(timer_data)
                if timer_data['is_online']:
                    online_timers.append(timer_id)
                else:
                    offline_timers.append(timer_id)
            
            # Aggiorna il contatore
            self.timer_count.setText(f"Timer connessi: {len(online_timers)} online, {len(offline_timers)} offline")
            
            # Filtra i timer in base al filtro selezionato
            filtered_timers = {}
            for device_id, timer_data in timers.items():
                if self.show_offline == "all":
                    # Mostra tutti i timer
                    filtered_timers[device_id] = timer_data
                elif self.show_offline == "only_online" and timer_data['is_online']:
                    # Mostra solo i timer online
                    filtered_timers[device_id] = timer_data
                elif self.show_offline == "only_offline" and not timer_data['is_online']:
                    # Mostra solo i timer offline
                    filtered_timers[device_id] = timer_data
            
            # Trova timer da rimuovere (non più presenti o filtrati)
            to_remove = []
            for device_id in self.timer_cards:
                if device_id not in filtered_timers:
                    to_remove.append(device_id)
            
            # Rimuovi card non più necessarie
            for device_id in to_remove:
                card = self.timer_cards.pop(device_id)
                self.grid_layout.removeWidget(card)
                card.setParent(None)
                card.deleteLater()
            
            # Se non ci sono timer da visualizzare, mostra il messaggio "Nessun timer connesso"
            if not filtered_timers:
                # Verifica se l'etichetta è già presente nel layout
                if self.no_timers_label.parent() is None:
                    self.grid_layout.addWidget(self.no_timers_label, 0, 0, 1, 3)  # Span su 3 colonne
                return
            else:
                # Assicurati che l'etichetta "Nessun timer connesso" sia nascosta se ci sono timer
                if self.no_timers_label.parent() is not None:
                    self.grid_layout.removeWidget(self.no_timers_label)
                    self.no_timers_label.setParent(None)
            
            # Ordina i timer per numero tavolo
            sorted_timers = sorted(filtered_timers.items(), 
                                key=lambda x: x[1].get('table_number', 999))
            
            # Calcola nuove posizioni
            max_cols = 3  # Numero di colonne nella griglia
            positions = {}
            row, col = 0, 0
            
            for device_id, _ in sorted_timers:
                positions[device_id] = (row, col)
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1
            
            # Aggiorna o crea le card
            for device_id, timer_data in sorted_timers:
                # Imposta la posizione iniziale della card
                row, col = positions[device_id]
                
                # MODIFICATO: Non controlliamo più le chiamate floorman e non attiviamo l'icona
                
                if device_id in self.timer_cards:
                    # Aggiorna i dati della card esistente
                    card = self.timer_cards[device_id]
                    card.update_data(timer_data)
                    
                    # Sposta la card nella nuova posizione se necessario
                    current_index = self.grid_layout.indexOf(card)
                    if current_index >= 0:
                        current_row, current_col, _, _ = self.grid_layout.getItemPosition(current_index)
                        if current_row != row or current_col != col:
                            self.grid_layout.removeWidget(card)
                            self.grid_layout.addWidget(card, row, col)
                else:
                    # Crea una nuova card direttamente nella posizione corretta
                    card = TimerCard(device_id, timer_data, self.server)
                    
                    # MODIFICATO: Non impostiamo più set_floorman_active anche se c'è una chiamata floorman
                    
                    self.grid_layout.addWidget(card, row, col)
                    self.timer_cards[device_id] = card
                    
            
            # Aggiorna il timestamp dell'ultimo aggiornamento completo
            self.last_full_update = time.time()
        finally:
            self.update_lock.release()
    

    @pyqtSlot(str)
    def on_timer_updated(self, device_id):
        """Gestisce il segnale di aggiornamento timer"""
        # Controlla se il timer esiste nei dati del server
        if device_id not in self.server.timers:
            return
            
        timer_data = self.server.timers[device_id]
        
        # MODIFICATO: Non controlliamo più lo stato floorman
        
        # Se c'è una card esistente, aggiornala
        if device_id in self.timer_cards:
            card = self.timer_cards[device_id]
            
            # Aggiorna i dati della card
            card.update_data(timer_data)
        else:
            # Se non esiste una card, forza un aggiornamento completo
            self.update_timers()
        
        # Aggiorna il contatore
        timers = self.server.timers
        online_timers = []
        offline_timers = []
        for timer_id, timer_data in timers.items():
            if self.server.is_timer_online(timer_data):
                online_timers.append(timer_id)
            else:
                offline_timers.append(timer_id)
        
        self.timer_count.setText(f"Timer connessi: {len(online_timers)} online, {len(offline_timers)} offline")
       
    @pyqtSlot(str)
    def on_timer_connected(self, device_id):
        """Gestisce il segnale di connessione nuovo timer"""
        # Aggiorna la vista quando si connette un nuovo timer
        self.update_timers()
        
        # Determina il tipo di timer
        device_type = None
        if device_id.startswith('android_'):
            device_type = "android"
        elif device_id.startswith('arduino_'):
            device_type = "hardware"
        
        # Mostra notifica per nuovo timer
        timer_data = self.server.timers.get(device_id, {})
        table_number = timer_data.get('table_number', 'N/A')
        self.notification_manager.show_notification(
            f"Nuovo Timer Connesso", 
            f"Il timer per il tavolo {table_number} si è connesso al server.",
            "info",
            device_type=device_type,
            play_sound=True
        )
    
    @pyqtSlot(str, list)
    def on_seat_notification(self, table_number, seats):
        """Gestisce il segnale di notifica posti liberi"""
        # Verifica se abbiamo ricevuto lo stesso segnale di recente
        # Usiamo attributi statici nella classe per tracciare gli ultimi segnali
        if not hasattr(self, '_last_seat_notification'):
            self._last_seat_notification = {}
        
        # Crea una chiave univoca per questo segnale (tavolo + lista posti ordinata)
        sorted_seats = sorted(seats)
        notification_key = f"{table_number}_{sorted_seats}"
        
        # Controlla se abbiamo già ricevuto questo segnale negli ultimi 2 secondi
        current_time = time.time()
        if notification_key in self._last_seat_notification:
            last_time = self._last_seat_notification[notification_key]
            if current_time - last_time < 2.0:  # Ignora se è passato meno di 2 secondi
                print(f"Ignorata notifica duplicata per il tavolo {table_number} - ricevuta entro 2 secondi")
                return
        
        # Memorizza questo segnale come l'ultimo ricevuto
        self._last_seat_notification[notification_key] = current_time
        
        # Formatta i posti liberi
        seats_str = ", ".join(map(str, seats))
        
        # Determina il tipo di dispositivo
        device_type = None
        for device_id, timer_data in self.server.timers.items():
            if str(timer_data.get('table_number', '')) == table_number:
                if device_id.startswith('android_'):
                    device_type = "android"
                elif device_id.startswith('arduino_'):
                    device_type = "hardware"
                break
        
        # Definisce il callback per il reset dei posti
        def reset_seats_callback():
            # Cerca il device_id corrispondente al tavolo
            device_id = None
            for d_id, timer_data in self.server.timers.items():
                if str(timer_data.get('table_number', '')) == table_number:
                    device_id = d_id
                    break
            
            # Se trovato, resetta i posti
            if device_id:
                self.server.reset_seat_info(device_id)
                print(f"Reset posti completato per il tavolo {table_number}")
        
        # METODO DIRETTO: se esiste già una notifica, la aggiorna; altrimenti ne crea una nuova
        has_existing_notification = False
        if hasattr(self.notification_manager, 'table_notifications'):
            has_existing_notification = table_number in self.notification_manager.table_notifications
        
        if has_existing_notification:
            # Aggiorna la notifica esistente
            self.notification_manager.update_notification(table_number, f"Seat Open: {seats_str}", seats)
            print(f"Notifica per tavolo {table_number} aggiornata con posti {seats_str}")
        else:
            # Crea una nuova notifica con suono ripetuto ogni minuto (play_repeat_sound=True)
            self.notification_manager.show_notification(
                f"Tavolo {table_number} - Seat Open",
                f"Posti disponibili: {seats_str}",
                "success",
                action_button="OK",
                action_callback=reset_seats_callback,
                play_sound=True,
                device_type=device_type,
                auto_close=False,
                table_number=table_number,
                play_repeat_sound=True  # Abilita la riproduzione periodica del suono
            )
            print(f"Nuova notifica creata per tavolo {table_number} con posti {seats_str}")
    

    @pyqtSlot(int)
    def on_floorman_notification(self, table_number):
        """Gestisce il segnale di chiamata floorman"""
        # Verifica se c'è già una chiamata attiva per questo tavolo
        if table_number in self.active_floorman_calls:
            print(f"Chiamata floorman già attiva per il tavolo {table_number}")
            return
        
        # IMPORTANTE: Mostra sempre la notifica toast
        self.notification_manager.show_notification(
            f"⚠️ Chiamata Floorman",
            f"Floorman richiesto al tavolo {table_number}",
            "warning",
            play_sound=True,
            duration=10000  # 10 secondi
        )
        
        # MODIFICATO: Non attiviamo più l'icona floorman sulla card
        # Teniamo traccia della chiamata attiva nel dizionario
        for device_id, timer_data in self.server.timers.items():
            if timer_data.get('table_number') == table_number:
                self.active_floorman_calls[table_number] = device_id
                break

    
    @pyqtSlot(int)
    def on_bar_service_notification(self, table_number):
        """Gestisce il segnale di richiesta servizio bar"""
        # Mostra notifica
        self.notification_manager.show_notification(
            f"Servizio Bar",
            f"Richiesta servizio bar dal tavolo {table_number}",
            "info",
            play_sound=True,
            duration=8000  # 8 secondi
        )
    
    def closeEvent(self, event):
        """Gestisce l'evento di chiusura della finestra"""
        # Salva le impostazioni
        self.settings.setValue("show_filter", self.show_offline)
        
        # Ferma ngrok se attivo
        if hasattr(self, 'ngrok_service') and self.ngrok_active:
            self.ngrok_service.stop_tunnel()
        
        # Se il server è attivo
        if self.is_server_running:
            reply = QMessageBox.question(
                self, 'Conferma Uscita',
                'Il server è ancora in esecuzione. Vuoi fermarlo e uscire?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.stop_server()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()


    def show_qr_generator_dialog(self):
        """Mostra il dialog del generatore QR"""
        # Ottieni l'indirizzo IP dell'host
        try:
            import socket
            host_name = socket.gethostname()
            server_ip = socket.gethostbyname(host_name)
        except Exception as e:
            # In caso di errore, usa localhost
            print(f"Errore nel rilevamento dell'IP: {e}")
            server_ip = "localhost"
        
        # Usa la porta configurata nel server
        server_port = self.http_port
        
        # Crea e mostra il dialog, passando l'URL ngrok se disponibile
        qr_dialog = QRCodeDialog(
            server_ip, 
            server_port, 
            self,
            ngrok_url=self.ngrok_public_url if self.ngrok_active else None
        )
        
        qr_dialog.exec()

# ----------------------------------------------------------------------------
# QR CODE GENERATOR - Generatore di codici QR per richieste bar
# ----------------------------------------------------------------------------

import os
import sys
import time
import tempfile
import logging
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QSpinBox, QFileDialog,
                           QProgressBar, QMessageBox, QGridLayout, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QSize
from PyQt6.QtGui import QPixmap, QImage

# Verifica se qrcode è installato, altrimenti suggerisce l'installazione
try:
    import qrcode
    from PIL import Image, ImageDraw, ImageFont
    HAS_QRCODE = True
except ImportError:
    print("Modulo 'qrcode' o 'pillow' non trovato. Installalo con 'pip install qrcode pillow'")
    HAS_QRCODE = False

class QRGeneratorThread(QThread):
    """Thread separato per la generazione dei codici QR senza bloccare l'UI"""
    progress_updated = pyqtSignal(int)
    qr_generated = pyqtSignal(int, QImage)  # Emette l'immagine QR generata
    finished_all = pyqtSignal()
    error_occurred = pyqtSignal(str)
    
    def __init__(self, server_ip, server_port, output_dir, num_tables, temp_dir=None, ngrok_url=None):
        super().__init__()
        self.server_ip = server_ip
        self.server_port = server_port
        self.output_dir = output_dir
        self.num_tables = num_tables
        self.temp_dir = temp_dir  # Directory temporanea per i QR visualizzati nella UI
        self.ngrok_url = ngrok_url  # URL pubblico fornito da ngrok
        self.abort = False
    
    def run(self):
        """Esegue la generazione dei codici QR"""
        try:
            # Crea la directory di output se non esiste
            if not os.path.exists(self.output_dir):
                os.makedirs(self.output_dir)
            
            # Se specificata, crea anche la directory temporanea
            if self.temp_dir and not os.path.exists(self.temp_dir):
                os.makedirs(self.temp_dir)
            
            # Per ogni tavolo, genera un codice QR
            for i, table_num in enumerate(range(1, self.num_tables + 1)):
                # Controlla se l'operazione è stata annullata
                if self.abort:
                    return
                
                # Genera l'URL per la richiesta bar
                # Se è disponibile un URL ngrok, usalo invece dell'IP locale
                if self.ngrok_url:
                    # Usa l'URL ngrok completo
                    base_url = self.ngrok_url
                    # Rimuovi eventuali slash finali
                    if base_url.endswith('/'):
                        base_url = base_url[:-1]
                    qr_url = f"{base_url}/qr/bar-request/{table_num}"
                else:
                    # Usa l'IP locale (funziona solo sulla stessa rete)
                    qr_url = f"http://{self.server_ip}:{self.server_port}/qr/bar-request/{table_num}"
                
                # Crea il codice QR
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_M,
                    box_size=10,
                    border=4,
                )
                qr.add_data(qr_url)
                qr.make(fit=True)
                
                # Crea un'immagine dal codice QR
                qr_img = qr.make_image(fill_color="black", back_color="white")
                
                # Converti in RGB per poter aggiungere testo colorato
                qr_img = qr_img.convert("RGB")
                
                # Aggiungi titolo e istruzioni sotto il QR code
                img_width, img_height = qr_img.size
                
                # Crea una nuova immagine più grande per contenere il QR code e il testo
                new_height = img_height + 150  # Spazio extra per il testo
                new_img = Image.new('RGB', (img_width, new_height), color='white')
                
                # Incolla il QR code
                new_img.paste(qr_img, (0, 0))
                
                # Aggiungi il testo
                draw = ImageDraw.Draw(new_img)
                
                # Prova a caricare un font, altrimenti usa il default
                try:
                    title_font = ImageFont.truetype("Arial Bold.ttf", 36)
                    text_font = ImageFont.truetype("Arial.ttf", 24)
                except IOError:
                    # Usa un font predefinito se Arial non è disponibile
                    title_font = ImageFont.load_default()
                    text_font = ImageFont.load_default()
                
                # Titolo
                title = f"SERVIZIO BAR - TAVOLO {table_num}"
                title_width = draw.textlength(title, font=title_font)
                title_position = ((img_width - title_width) // 2, img_height + 20)
                draw.text(title_position, title, font=title_font, fill=(0, 128, 0))  # Verde
                
                # Istruzioni
                instructions = "Inquadra con la fotocamera"
                instructions_width = draw.textlength(instructions, font=text_font)
                instructions_position = ((img_width - instructions_width) // 2, img_height + 70)
                draw.text(instructions_position, instructions, font=text_font, fill=(0, 0, 0))  # Nero
                
                instructions2 = "per ordinare al bar"
                instructions2_width = draw.textlength(instructions2, font=text_font)
                instructions2_position = ((img_width - instructions2_width) // 2, img_height + 100)
                draw.text(instructions2_position, instructions2, font=text_font, fill=(0, 0, 0))  # Nero
                
                # Se stiamo usando ngrok, aggiungi un'indicazione che funziona da qualsiasi rete
                if self.ngrok_url:
                    access_info = "Funziona da qualsiasi rete"
                    access_width = draw.textlength(access_info, font=text_font)
                    access_position = ((img_width - access_width) // 2, img_height + 130)
                    draw.text(access_position, access_info, font=text_font, fill=(0, 0, 255))  # Blu
                
                # Salva l'immagine finale
                output_path = os.path.join(self.output_dir, f"bar_qr_table_{table_num}.png")
                new_img.save(output_path)
                
                # Se richiesto, salva anche nella directory temporanea per la visualizzazione nella UI
                if self.temp_dir:
                    temp_path = os.path.join(self.temp_dir, f"qr_preview_{table_num}.png")
                    new_img.save(temp_path)
                    
                    # Converti l'immagine PIL in QImage per la visualizzazione
                    img_data = new_img.tobytes("raw", "RGB")
                    q_img = QImage(img_data, new_img.width, new_img.height, new_img.width * 3, QImage.Format.Format_RGB888)
                    
                    # Emetti il segnale con l'immagine generata
                    self.qr_generated.emit(table_num, q_img)
                
                # Aggiorna la barra di progresso
                progress = int((i + 1) / self.num_tables * 100)
                self.progress_updated.emit(progress)
                
                # Piccola pausa per permettere all'UI di aggiornarsi
                time.sleep(0.1)
            
            # Segnala che abbiamo finito
            self.finished_all.emit()
                
        except Exception as e:
            print(f"Errore nella generazione dei codici QR: {e}")
            self.error_occurred.emit(str(e))
class QRCodeDialog(QDialog):
    """Dialog per la generazione e visualizzazione dei codici QR"""
    
    def __init__(self, server_ip, server_port, parent=None, ngrok_url=None):
        super().__init__(parent)
        
        if not HAS_QRCODE:
            QMessageBox.critical(
                self,
                "Errore - Librerie mancanti",
                "Le librerie 'qrcode' e 'pillow' sono necessarie per questa funzionalità.\n\n"
                "Installale con il comando:\npip install qrcode pillow"
            )
            self.reject()
            return
            
        self.server_ip = server_ip
        self.server_port = server_port
        self.ngrok_url = ngrok_url  # URL pubblico fornito da ngrok
        self.temp_dir = tempfile.mkdtemp(prefix="poker_timer_qr_")
        
        self.setWindowTitle("Generatore Codici QR per Servizio Bar")
        self.setMinimumSize(900, 600)  # Dimensione ampia per visualizzare i QR
        
        # Layout principale
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Titolo
        title_label = QLabel("Generatore Codici QR per Servizio Bar")
        title_label.setStyleSheet("font-size: 18pt; font-weight: bold;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Informazioni sul server
        if self.ngrok_url:
            info_label = QLabel(f"Server: Locale ({server_ip}:{server_port}) - Accessibile globalmente via {self.ngrok_url}")
            # Aggiungi un messaggio informativo
            note_label = QLabel("I QR code utilizzeranno l'URL pubblico per consentire l'accesso da qualsiasi rete.")
            note_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
            main_layout.addWidget(note_label, alignment=Qt.AlignmentFlag.AlignCenter)
        else:
            info_label = QLabel(f"Server: {server_ip}:{server_port} (solo rete locale)")
            # Aggiungi un messaggio di avviso
            warning_label = QLabel("ATTENZIONE: I QR code funzioneranno solo sulla stessa rete WiFi del server.")
            warning_label.setStyleSheet("color: #f44336; font-weight: bold;")
            main_layout.addWidget(warning_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        info_label.setStyleSheet("font-size: 12pt;")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(info_label)
        
        # Sezione configurazione
        config_layout = QHBoxLayout()
        
        # Numero di tavoli
        table_layout = QHBoxLayout()
        table_label = QLabel("Numero di tavoli:")
        table_label.setStyleSheet("font-size: 12pt;")
        self.table_spinner = QSpinBox()
        self.table_spinner.setMinimum(1)
        self.table_spinner.setMaximum(100)
        self.table_spinner.setValue(10)
        self.table_spinner.setStyleSheet("font-size: 12pt;")
        table_layout.addWidget(table_label)
        table_layout.addWidget(self.table_spinner)
        
        config_layout.addLayout(table_layout)
        config_layout.addStretch()
        
        # Directory di output
        output_layout = QHBoxLayout()
        output_label = QLabel("Directory di output:")
        output_label.setStyleSheet("font-size: 12pt;")
        self.output_dir = os.path.join(os.path.expanduser("~"), "poker_timer_qr_codes")
        self.output_path = QLabel(self.output_dir)
        self.output_path.setStyleSheet("font-size: 12pt; padding: 3px; background-color: #f0f0f0; border-radius: 3px;")
        browse_button = QPushButton("Sfoglia...")
        browse_button.clicked.connect(self.browse_output_dir)
        output_layout.addWidget(output_label)
        output_layout.addWidget(self.output_path, 1)  # Stretch
        output_layout.addWidget(browse_button)
        
        main_layout.addLayout(config_layout)
        main_layout.addLayout(output_layout)
        
        # Bottoni per generare e aprire la cartella
        button_layout = QHBoxLayout()
        self.generate_button = QPushButton("Genera Codici QR")
        self.generate_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 14pt;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.generate_button.clicked.connect(self.generate_qr_codes)
        
        self.open_folder_button = QPushButton("Apri Cartella")
        self.open_folder_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 14pt;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.open_folder_button.clicked.connect(self.open_output_folder)
        self.open_folder_button.setEnabled(False)  # Disabilitato finché non generiamo
        
        button_layout.addWidget(self.generate_button)
        button_layout.addWidget(self.open_folder_button)
        
        main_layout.addLayout(button_layout)
        
        # Barra di progresso
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        # Area di visualizzazione QR preview
        preview_label = QLabel("Anteprima Codici QR:")
        preview_label.setStyleSheet("font-size: 14pt; font-weight: bold;")
        main_layout.addWidget(preview_label)
        
        # Container scrollabile per le anteprime
        self.scroll_area = QFrame()
        self.scroll_area.setStyleSheet("background-color: #f9f9f9; border-radius: 5px; padding: 10px;")
        self.scroll_layout = QGridLayout(self.scroll_area)
        
        main_layout.addWidget(self.scroll_area, 1)  # Stretch
        
        # Bottone Chiudi
        close_button = QPushButton("Chiudi")
        close_button.setStyleSheet("""
            QPushButton {
                padding: 8px 20px;
                font-size: 12pt;
            }
        """)
        close_button.clicked.connect(self.close)
        main_layout.addWidget(close_button, 0, Qt.AlignmentFlag.AlignRight)
        
        # Thread per la generazione
        self.qr_thread = None
    
    def browse_output_dir(self):
        """Apre un dialog per selezionare la directory di output"""
        directory = QFileDialog.getExistingDirectory(
            self, "Seleziona Directory di Output", self.output_dir,
            QFileDialog.Option.ShowDirsOnly | QFileDialog.Option.DontResolveSymlinks
        )
        
        if directory:
            self.output_dir = directory
            self.output_path.setText(directory)
    
    def generate_qr_codes(self):
        """Avvia la generazione dei codici QR"""
        num_tables = self.table_spinner.value()
        
        # Disabilita i controlli durante la generazione
        self.generate_button.setEnabled(False)
        self.table_spinner.setEnabled(False)
        
        # Mostra la barra di progresso
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        
        # Pulisci eventuali preview precedenti
        self.clear_preview_area()
        
        # Crea il thread per la generazione, passando l'URL ngrok se disponibile
        self.qr_thread = QRGeneratorThread(
            self.server_ip,
            self.server_port,
            self.output_dir,
            num_tables,
            self.temp_dir,
            ngrok_url=self.ngrok_url  # Passa l'URL pubblico al thread
        )
        
        # Connetti i segnali
        self.qr_thread.progress_updated.connect(self.update_progress)
        self.qr_thread.qr_generated.connect(self.display_qr_preview)
        self.qr_thread.finished_all.connect(self.generation_completed)
        self.qr_thread.error_occurred.connect(self.show_error)
        
        # Avvia il thread
        self.qr_thread.start()

    
    def update_progress(self, value):
        """Aggiorna la barra di progresso"""
        self.progress_bar.setValue(value)
    
    def display_qr_preview(self, table_num, qr_image):
        """Mostra l'anteprima di un codice QR generato"""
        # Calcola la posizione nella griglia (3 colonne)
        row = (table_num - 1) // 3
        col = (table_num - 1) % 3
        
        # Crea un frame per contenere l'immagine e l'etichetta
        frame = QFrame()
        frame.setStyleSheet("background-color: white; border-radius: 5px; padding: 5px;")
        frame_layout = QVBoxLayout(frame)
        frame_layout.setContentsMargins(5, 5, 5, 5)
        
        # Crea un label per l'immagine QR
        qr_label = QLabel()
        qr_pixmap = QPixmap.fromImage(qr_image)
        # Ridimensiona per adattarsi al layout
        qr_pixmap = qr_pixmap.scaled(QSize(200, 250), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        qr_label.setPixmap(qr_pixmap)
        qr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Crea un label per il numero del tavolo
        table_label = QLabel(f"Tavolo {table_num}")
        table_label.setStyleSheet("font-size: 12pt; font-weight: bold; color: #2196F3;")
        table_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Aggiungi al layout del frame
        frame_layout.addWidget(table_label)
        frame_layout.addWidget(qr_label)
        
        # Aggiungi il frame alla griglia
        self.scroll_layout.addWidget(frame, row, col)
    
    def clear_preview_area(self):
        """Pulisce l'area di anteprima"""
        # Rimuovi tutti i widget dal layout
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
    
    def generation_completed(self):
        """Gestisce il completamento della generazione"""
        # Riabilita i controlli
        self.generate_button.setEnabled(True)
        self.table_spinner.setEnabled(True)
        self.open_folder_button.setEnabled(True)
        
        # Mostra un messaggio di completamento
        num_tables = self.table_spinner.value()
        QMessageBox.information(
            self,
            "Generazione Completata",
            f"{num_tables} codici QR sono stati generati con successo nella directory:\n{self.output_dir}"
        )
    
    def show_error(self, error_message):
        """Mostra un messaggio di errore"""
        # Riabilita i controlli
        self.generate_button.setEnabled(True)
        self.table_spinner.setEnabled(True)
        
        # Mostra il messaggio di errore
        QMessageBox.critical(
            self,
            "Errore",
            f"Si è verificato un errore durante la generazione dei codici QR:\n{error_message}"
        )
    
    def open_output_folder(self):
        """Apre la directory di output nel file explorer"""
        import subprocess
        import platform
        
        try:
            if platform.system() == "Windows":
                os.startfile(self.output_dir)
            elif platform.system() == "Darwin":  # macOS
                subprocess.call(["open", self.output_dir])
            else:  # Linux
                subprocess.call(["xdg-open", self.output_dir])
        except Exception as e:
            QMessageBox.warning(
                self,
                "Avviso",
                f"Impossibile aprire la directory:\n{str(e)}"
            )
    
    def closeEvent(self, event):
        """Gestisce la chiusura della finestra"""
        # Se c'è un thread in esecuzione, interrompilo
        if self.qr_thread and self.qr_thread.isRunning():
            self.qr_thread.abort = True
            self.qr_thread.wait(1000)  # Attendi fino a 1 secondo
        
        # Pulisci la directory temporanea
        try:
            import shutil
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        except:
            pass
        
        event.accept()