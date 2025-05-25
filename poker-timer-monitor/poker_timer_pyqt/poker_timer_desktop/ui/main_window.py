#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Finestra principale dell'applicazione Poker Timer
"""

import sys
import os
import time
import threading

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QPushButton, QFrame, QGridLayout, QScrollArea,
                            QSpinBox, QCheckBox, QGroupBox, QMessageBox, QSplitter,
                            QSizePolicy, QRadioButton, QButtonGroup, QMenu, QMenuBar,
                            QDialog, QFormLayout, QDialogButtonBox)


from PyQt6.QtCore import Qt, QTimer, QSettings, pyqtSlot
from PyQt6.QtGui import QFont, QIcon, QAction

from .timer_card import TimerCard
from .notifications import NotificationManager
from server import PokerTimerServer

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
    """Finestra principale dell'applicazione Poker Timer"""

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
        
        # Gestore notifiche
        self.notification_manager = NotificationManager()
        
        # Connessione segnali del server
        self.server.timer_updated.connect(self.on_timer_updated)
        self.server.timer_connected.connect(self.on_timer_connected)
        self.server.seat_notification.connect(self.on_seat_notification)
        
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
            
            # Avvia il server
            self.server.start()
            
            # Aggiorna l'interfaccia
            self.is_server_running = True
            self.server_action.setText("Ferma Server")
            self.status_label.setText("Server: Attivo")
            self.status_label.setObjectName("status-label-active")
            
            # Aggiorna la barra di stato
            self.statusBar().showMessage(f"Server avviato su porta {self.http_port}, discovery su porta {self.discovery_port}")
            
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
                
            # Aggiorna il contatore dei timer
            timers = self.server.timers
            online_timers = []
            offline_timers = []
            for timer_id, timer_data in timers.items():
                timer_data['is_online'] = self.server.is_timer_online(timer_data)
                if timer_data['is_online']:
                    online_timers.append(timer_id)
                else:
                    offline_timers.append(timer_id)
            
            self.timer_count.setText(f"Timer connessi: {len(online_timers)} online, {len(offline_timers)} offline")
            
            # Aggiorna i dati delle card esistenti
            for device_id, card in list(self.timer_cards.items()):
                if device_id in self.server.timers:
                    timer_data = self.server.timers[device_id]
                    timer_data['is_online'] = self.server.is_timer_online(timer_data)
                    card.update_data(timer_data)
        finally:
            self.update_lock.release()
    
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
                if device_id in self.timer_cards:
                    # Aggiorna i dati della card esistente E CHIAMA update_data
                    self.timer_cards[device_id].update_data(timer_data)
                    
                    # Sposta la card nella nuova posizione se necessario
                    row, col = positions[device_id]
                    current_index = self.grid_layout.indexOf(self.timer_cards[device_id])
                    if current_index >= 0:
                        current_row, current_col, _, _ = self.grid_layout.getItemPosition(current_index)
                        if current_row != row or current_col != col:
                            self.grid_layout.removeWidget(self.timer_cards[device_id])
                            self.grid_layout.addWidget(self.timer_cards[device_id], row, col)
                else:
                    # Crea una nuova card
                    card = TimerCard(device_id, timer_data, self.server)
                    row, col = positions[device_id]
                    self.grid_layout.addWidget(card, row, col)
                    self.timer_cards[device_id] = card
                    
            # Aggiorna il timestamp dell'ultimo aggiornamento completo
            self.last_full_update = time.time()
        finally:
            self.update_lock.release()
    
    @pyqtSlot(str)
    def on_timer_updated(self, device_id):
        """Gestisce il segnale di aggiornamento timer"""
        # Forza l'aggiornamento della card corrispondente
        if device_id in self.timer_cards and device_id in self.server.timers:
            # Crea una nuova card per sostituire quella esistente
            timer_data = self.server.timers[device_id]
            row, col = 0, 0
            
            # Trova la posizione attuale della card
            current_index = self.grid_layout.indexOf(self.timer_cards[device_id])
            if current_index >= 0:
                current_row, current_col, _, _ = self.grid_layout.getItemPosition(current_index)
                row, col = current_row, current_col
            
            # Rimuovi la card esistente
            old_card = self.timer_cards[device_id]
            self.grid_layout.removeWidget(old_card)
            old_card.setParent(None)
            old_card.deleteLater()
            
            # Crea una nuova card
            new_card = TimerCard(device_id, timer_data, self.server)
            self.grid_layout.addWidget(new_card, row, col)
            self.timer_cards[device_id] = new_card
            
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
            self.notification_manager.update_notification(table_number, f"Posti disponibili: {seats_str}", seats)
            print(f"Notifica per tavolo {table_number} aggiornata con posti {seats_str}")
        else:
            # Crea una nuova notifica
            self.notification_manager.show_notification(
                f"Tavolo {table_number} - Seat Open",
                f"Posti disponibili: {seats_str}",
                "success",
                action_button="OK",
                action_callback=reset_seats_callback,
                play_sound=True,
                device_type=device_type,
                auto_close=False,
                table_number=table_number
            )
            print(f"Nuova notifica creata per tavolo {table_number} con posti {seats_str}")
    
    def closeEvent(self, event):
        """Gestisce l'evento di chiusura della finestra"""
        # Salva le impostazioni
        self.settings.setValue("show_filter", self.show_offline)
        
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