#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Finestra principale dell'applicazione Poker Timer
"""

import sys
import os
import time

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QPushButton, QFrame, QGridLayout, QScrollArea,
                            QSpinBox, QCheckBox, QGroupBox, QMessageBox, QSplitter,
                            QSizePolicy, QRadioButton, QButtonGroup)


from PyQt6.QtCore import Qt, QTimer, QSettings, pyqtSlot
from PyQt6.QtGui import QFont, QIcon

from .timer_card import TimerCard
from .notifications import NotificationManager
from server import PokerTimerServer

class MainWindow(QMainWindow):
    """Finestra principale dell'applicazione Poker Timer"""

    def __init__(self):
        super().__init__()
        
        # Impostazioni
        self.settings = QSettings("PokerTimer", "Monitor")
        
        # Configura la finestra
        self.setWindowTitle("Poker Timer Monitor")
        self.setMinimumSize(1200, 800)
        
        # Server e dati
        self.http_port = self.settings.value("http_port", 3000, int)
        self.discovery_port = self.settings.value("discovery_port", 8888, int)
        self.show_offline = self.settings.value("show_filter", "only_online", str)  # Modificato per i 3 filtri
        
        self.server = PokerTimerServer(port=self.http_port, discovery_port=self.discovery_port)
        self.is_server_running = False
        
        # Gestore notifiche
        self.notification_manager = NotificationManager()
        
        # Connessione segnali del server
        self.server.timer_updated.connect(self.on_timer_updated)
        self.server.timer_connected.connect(self.on_timer_connected)
        self.server.seat_notification.connect(self.on_seat_notification)
        
        # Widget centrale
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)
        
        # Rimuoviamo l'header "Poker Timer Monitor"
        
        # Pannello di controllo
        control_panel = self.create_control_panel()
        main_layout.addWidget(control_panel)
        
        # Area di scorrimento per i timer
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setMinimumHeight(400)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)  # Rimuovi il bordo
        self.scroll_area.setStyleSheet("background-color: #f5f5f5;")
        
        self.timer_container = QWidget()
        self.timer_container.setStyleSheet("background-color: #f5f5f5;")
        self.grid_layout = QGridLayout(self.timer_container)
        self.grid_layout.setSpacing(20)  # Spazio tra le card
        self.grid_layout.setContentsMargins(20, 20, 20, 20)
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)  # Allineamento in alto a sinistra
        
        self.scroll_area.setWidget(self.timer_container)
        main_layout.addWidget(self.scroll_area)
        
        # Etichetta per quando non ci sono timer
        self.no_timers_label = QLabel("Nessun timer connesso")
        self.no_timers_label.setObjectName("no-timers-label")
        self.no_timers_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.no_timers_label.setStyleSheet("font-size: 16pt; color: #333333; font-weight: bold; padding: 20px;")
        self.grid_layout.addWidget(self.no_timers_label, 0, 0, 1, 3)  # Span su 3 colonne
        
        # Timer per aggiornamenti periodici
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_timers)
        self.update_timer.start(1000)  # Aggiorna ogni secondo
        
        # Barra di stato
        self.statusBar().showMessage("Server Poker Timer pronto")
        self.statusBar().setFont(QFont("Arial", 12))
        
        # Posiziona la finestra al centro dello schermo
        self.center_window()
        
        # Autostart del server se era attivo alla chiusura
        if self.settings.value("autostart_server", False, bool):
            self.start_server()
    
    def center_window(self):
        """Centra la finestra sullo schermo"""
        frame_geometry = self.frameGeometry()
        screen_center = self.screen().availableGeometry().center()
        frame_geometry.moveCenter(screen_center)
        self.move(frame_geometry.topLeft())
    
    def create_control_panel(self):
        """Crea il pannello di controllo"""
        panel = QFrame()
        panel.setFrameStyle(QFrame.Shape.StyledPanel)
        panel.setStyleSheet("background-color: #f0f0f0; border-radius: 8px; padding: 15px; border: 2px solid #9e9e9e;")
        
        layout = QHBoxLayout(panel)
        layout.setSpacing(20)
        
        # Gruppo impostazioni server
        server_group = QGroupBox("Server")
        server_group.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        server_layout = QHBoxLayout(server_group)
        
        # Porte
        port_layout = QVBoxLayout()
        http_layout = QHBoxLayout()
        http_layout.addWidget(QLabel("Porta HTTP:"))
        self.http_port_spin = QSpinBox()
        self.http_port_spin.setRange(1024, 65535)
        self.http_port_spin.setValue(self.http_port)
        self.http_port_spin.setMinimumWidth(100)
        # Rimuoviamo i bottoni +/- dallo spinbox
        self.http_port_spin.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        http_layout.addWidget(self.http_port_spin)
        port_layout.addLayout(http_layout)
        
        udp_layout = QHBoxLayout()
        udp_layout.addWidget(QLabel("Porta Discovery:"))
        self.udp_port_spin = QSpinBox()
        self.udp_port_spin.setRange(1024, 65535)
        self.udp_port_spin.setValue(self.discovery_port)
        self.udp_port_spin.setMinimumWidth(100)
        # Rimuoviamo i bottoni +/- dallo spinbox
        self.udp_port_spin.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        udp_layout.addWidget(self.udp_port_spin)
        port_layout.addLayout(udp_layout)
        
        server_layout.addLayout(port_layout)
        
        # Bottone avvio/stop
        self.server_btn = QPushButton("Avvia Server")
        self.server_btn.setObjectName("start-server-btn")
        self.server_btn.setMinimumHeight(60)
        self.server_btn.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.server_btn.clicked.connect(self.toggle_server)
        server_layout.addWidget(self.server_btn)
        
        layout.addWidget(server_group)
        
        # Filtro timer - MODIFICATO
        filter_group = QGroupBox("Filtro")
        filter_group.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        filter_layout = QHBoxLayout(filter_group)
        
        # Creiamo un gruppo di radio button per i filtri
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
        
        # Auto-start
        autostart_group = QGroupBox("Avvio")
        autostart_group.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        autostart_layout = QHBoxLayout(autostart_group)
        
        self.autostart_check = QCheckBox("Avvia server automaticamente")
        self.autostart_check.setFont(QFont("Arial", 12))
        self.autostart_check.setChecked(self.settings.value("autostart_server", False, bool))
        self.autostart_check.toggled.connect(self.on_autostart_toggled)
        autostart_layout.addWidget(self.autostart_check)
        
        layout.addWidget(autostart_group)
        
        # Informazioni sul server
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
            # Aggiorna le porte dal UI
            self.http_port = self.http_port_spin.value()
            self.discovery_port = self.udp_port_spin.value()
            
            # Salva le impostazioni
            self.settings.setValue("http_port", self.http_port)
            self.settings.setValue("discovery_port", self.discovery_port)
            
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
            self.server_btn.setText("Ferma Server")
            self.server_btn.setObjectName("stop-server-btn")
            self.server_btn.setStyleSheet("background-color: #d32f2f; color: white; font-weight: bold; padding: 8px 16px;")
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
            self.server_btn.setText("Avvia Server")
            self.server_btn.setObjectName("start-server-btn")
            self.server_btn.setStyleSheet("background-color: #2e7d32; color: white; font-weight: bold; padding: 8px 16px;")
            self.status_label.setText("Server: Non attivo")
            self.status_label.setObjectName("status-label-inactive")
            
            # Aggiorna la barra di stato
            self.statusBar().showMessage("Server fermato")
            
            # Pulisci il layout
            self.clear_grid()
            self.grid_layout.addWidget(self.no_timers_label, 0, 0)
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore nella chiusura del server: {str(e)}")

    def update_timers(self):
        """Aggiorna la visualizzazione dei timer"""
        if not self.is_server_running:
            return
        
        # Ottieni i timer dal server
        timers = self.server.timers
        
        # Conta i timer online
        online_timers = []
        offline_timers = []
        for timer_id, timer_data in timers.items():
            if self.server.is_timer_online(timer_data):
                online_timers.append(timer_id)
            else:
                offline_timers.append(timer_id)
        
        # Aggiorna il contatore
        self.timer_count.setText(f"Timer connessi: {len(online_timers)} online, {len(offline_timers)} offline")
        
        # Pulisci COMPLETAMENTE il layout corrente - questo è cruciale
        self.clear_grid()
        
        # Ricrea l'etichetta "Nessun timer connesso" dopo la pulizia
        self.no_timers_label = QLabel("Nessun timer connesso")
        self.no_timers_label.setObjectName("no-timers-label")
        self.no_timers_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.no_timers_label.setStyleSheet("font-size: 16pt; color: #333333; font-weight: bold; padding: 20px;")
        
        # Filtra i timer in base al filtro selezionato
        filtered_timers = {}
        for device_id, timer_data in timers.items():
            # Aggiungiamo un flag al timer_data per indicare se è online o offline
            timer_data['is_online'] = self.server.is_timer_online(timer_data)
            
            # Applica il filtro
            if self.show_offline == "all":
                # Mostra tutti i timer
                filtered_timers[device_id] = timer_data
            elif self.show_offline == "only_online" and timer_data['is_online']:
                # Mostra solo i timer online
                filtered_timers[device_id] = timer_data
            elif self.show_offline == "only_offline" and not timer_data['is_online']:
                # Mostra solo i timer offline
                filtered_timers[device_id] = timer_data
        
        # Se non ci sono timer, mostra il messaggio centrato nella griglia
        if not filtered_timers:
            self.grid_layout.addWidget(self.no_timers_label, 0, 0, 1, 3)  # Span su 3 colonne
            return
        
        # Aggiungi i timer alla griglia
        row, col = 0, 0
        max_cols = 3  # Numero di colonne nella griglia
        
        # Ordina i timer per numero tavolo
        sorted_timers = sorted(filtered_timers.items(), 
                            key=lambda x: x[1].get('table_number', 999))
        
        for device_id, timer_data in sorted_timers:
            # Crea un nuovo widget TimerCard
            timer_card = TimerCard(device_id, timer_data, self.server)
            
            # Aggiungi alla griglia nella posizione corretta
            self.grid_layout.addWidget(timer_card, row, col)
            
            # Passa alla prossima posizione nella griglia
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
    

    def clear_grid(self):
        """Rimuove tutti i widget dalla griglia in modo sicuro"""
        # Prima rimuovi tutti i widget
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item:
                widget = item.widget()
                if widget:
                    self.grid_layout.removeWidget(widget)
                    widget.setParent(None)
                    widget.deleteLater()  # Programma la cancellazione sicura
        
        # Ricrea il container con lo stesso layout
        self.timer_container = QWidget()
        self.timer_container.setStyleSheet("background-color: #f5f5f5;")
        self.grid_layout = QGridLayout(self.timer_container)
        self.grid_layout.setSpacing(20)
        self.grid_layout.setContentsMargins(20, 20, 20, 20)
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        
        # Imposta il widget aggiornato nell'area di scorrimento
        self.scroll_area.setWidget(self.timer_container)
    
    @pyqtSlot(str)
    def on_timer_updated(self, device_id):
        """Gestisce il segnale di aggiornamento timer"""
        self.update_timers()
        
    @pyqtSlot(str)
    def on_timer_connected(self, device_id):
        """Gestisce il segnale di connessione nuovo timer"""
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
            device_type=device_type  # Passa il tipo di dispositivo
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
                f"Tavolo {table_number} - Posti Liberi",
                f"Posti disponibili: {seats_str}",
                "success",
                action_button="Reset Posti",
                action_callback=reset_seats_callback,
                play_sound=True,
                device_type=device_type,
                auto_close=False,
                table_number=table_number
            )
            print(f"Nuova notifica creata per tavolo {table_number} con posti {seats_str}")
    
    def on_show_offline_toggled(self, checked):
        """Gestisce il cambio stato del checkbox per mostrare i timer offline"""
        self.show_offline = checked
        self.settings.setValue("show_offline", checked)
        self.update_timers()
    
    def on_autostart_toggled(self, checked):
        """Gestisce il cambio stato del checkbox per l'autostart"""
        self.settings.setValue("autostart_server", checked)
    
    def closeEvent(self, event):
        """Gestisce l'evento di chiusura della finestra"""
        # Salva le impostazioni
        self.settings.setValue("http_port", self.http_port_spin.value())
        self.settings.setValue("discovery_port", self.udp_port_spin.value())
        self.settings.setValue("show_filter", self.show_offline)  # Modificato: usa show_filter invece di show_offline
        
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