#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Finestra di dialogo per i dettagli di un timer
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                           QSpinBox, QComboBox, QCheckBox, QTabWidget, QWidget,
                           QGroupBox, QFormLayout, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class TimerDetailsDialog(QDialog):
    """Finestra di dialogo per visualizzare e modificare i dettagli di un timer"""
    def __init__(self, device_id, timer_data, server, parent=None):
        super().__init__(parent)
        self.device_id = device_id
        self.timer_data = timer_data
        self.server = server
        
        # Configurazione finestra
        self.setWindowTitle(f"Dettagli Timer - Tavolo {timer_data.get('table_number', 'N/A')}")
        self.setMinimumSize(500, 400)
        
        # Layout principale
        layout = QVBoxLayout(self)
        
        # Timer display
        timer_display = QLabel(f"{timer_data.get('current_timer', '0')} secondi")
        timer_display.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        timer_display.setStyleSheet("margin: 10px 0; text-align: center;")
        timer_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(timer_display)
        
        # Pulsanti di controllo
        control_layout = QHBoxLayout()
        
        # Start button
        self.start_btn = QPushButton("Start")
        self.start_btn.setStyleSheet("background-color: #007bff; color: white; font-weight: bold;")
        self.start_btn.clicked.connect(self.on_start_click)
        self.start_btn.setEnabled(not (timer_data.get('is_running', False) and not timer_data.get('is_paused', False)))
        control_layout.addWidget(self.start_btn)
        
        # Pause button
        self.pause_btn = QPushButton("Pause")
        self.pause_btn.setStyleSheet("background-color: #007bff; color: white; font-weight: bold;")
        self.pause_btn.clicked.connect(self.on_pause_click)
        self.pause_btn.setEnabled(timer_data.get('is_running', False) and not timer_data.get('is_paused', False))
        control_layout.addWidget(self.pause_btn)
        
        layout.addLayout(control_layout)
        
        # Informazioni timer
        info_group = QGroupBox("Informazioni Timer")
        info_layout = QFormLayout(info_group)
        
        # Mostra le informazioni
        info_layout.addRow("Stato:", QLabel("Running" if timer_data.get('is_running', False) and not timer_data.get('is_paused', False) 
                                         else "Paused" if timer_data.get('is_paused', False) else "Stopped"))
        info_layout.addRow("Timer T1:", QLabel(f"{timer_data.get('t1_value', 'N/A')} secondi"))
        info_layout.addRow("Timer T2:", QLabel(f"{timer_data.get('t2_value', 'N/A')} secondi"))
        info_layout.addRow("Modalità:", QLabel(f"{timer_data.get('mode', 'N/A')}"))
        info_layout.addRow("Buzzer:", QLabel("Attivo" if timer_data.get('buzzer', False) else "Disattivo"))
        info_layout.addRow("Batteria:", QLabel(f"{timer_data.get('battery_level', 'N/A')}%"))
        info_layout.addRow("WiFi Signal:", QLabel(f"{timer_data.get('wifi_signal', 'N/A')} dBm"))
        info_layout.addRow("IP Address:", QLabel(f"{timer_data.get('ip_address', 'N/A')}"))
        
        layout.addWidget(info_group)
        
        # Tab Widget per impostazioni e avanzate
        tab_widget = QTabWidget()
        
        # Tab impostazioni
        settings_tab = QWidget()
        settings_layout = QVBoxLayout(settings_tab)
        
        # Form per le impostazioni
        settings_form = QFormLayout()
        
        # Numero tavolo
        self.table_number = QSpinBox()
        self.table_number.setRange(0, 99)
        self.table_number.setValue(timer_data.get('table_number', 0))
        settings_form.addRow("Numero Tavolo:", self.table_number)
        
        # Numero giocatori
        self.players_count = QSpinBox()
        self.players_count.setRange(1, 10)
        self.players_count.setValue(timer_data.get('players_count', 10))
        settings_form.addRow("Numero Giocatori:", self.players_count)
        
        # Timer T1
        self.t1_value = QSpinBox()
        self.t1_value.setRange(5, 95)
        self.t1_value.setSingleStep(5)
        self.t1_value.setValue(timer_data.get('t1_value', 60))
        settings_form.addRow("Timer T1:", self.t1_value)
        
        # Timer T2
        self.t2_value = QSpinBox()
        self.t2_value.setRange(5, 95)
        self.t2_value.setSingleStep(5)
        self.t2_value.setValue(timer_data.get('t2_value', 30))
        settings_form.addRow("Timer T2:", self.t2_value)
        
        # Modalità
        self.mode = QComboBox()
        self.mode.addItem("Modalità 1: T1/T2 con avvio automatico", 1)
        self.mode.addItem("Modalità 2: T1/T2 con avvio manuale", 2)
        self.mode.addItem("Modalità 3: Solo T1 con avvio automatico", 3)
        self.mode.addItem("Modalità 4: Solo T1 con avvio manuale", 4)
        
        # Impostazione della modalità corrente
        current_mode = timer_data.get('mode', 1)
        index = self.mode.findData(current_mode)
        if index >= 0:
            self.mode.setCurrentIndex(index)
        
        self.mode.currentIndexChanged.connect(self.on_mode_changed)
        settings_form.addRow("Modalità:", self.mode)
        
        # Buzzer
        self.buzzer = QCheckBox()
        self.buzzer.setChecked(timer_data.get('buzzer', False))
        settings_form.addRow("Buzzer:", self.buzzer)
        
        settings_layout.addLayout(settings_form)
        
        # Pulsante salva impostazioni
        save_btn = QPushButton("Salva Impostazioni")
        save_btn.setStyleSheet("background-color: #28a745; color: white; font-weight: bold; padding: 8px;")
        save_btn.clicked.connect(self.save_settings)
        settings_layout.addWidget(save_btn)
        
        # Tab avanzate
        advanced_tab = QWidget()
        advanced_layout = QVBoxLayout(advanced_tab)
        
        # Avviso
        warning = QLabel("Attenzione: Queste opzioni possono influenzare permanentemente il funzionamento del timer.")
        warning.setStyleSheet("color: #dc3545; font-weight: bold;")
        advanced_layout.addWidget(warning)
        
        # Factory reset
        reset_group = QGroupBox("Factory Reset")
        reset_layout = QVBoxLayout(reset_group)
        
        reset_info = QLabel("Questa opzione ripristinerà TUTTE le impostazioni ai valori predefiniti, incluse:")
        reset_layout.addWidget(reset_info)
        
        reset_items = QLabel("• Valori timer (T1, T2)\n• Numero tavolo\n• Impostazioni buzzer\n• Modalità operativa\n• Impostazioni WiFi")
        reset_layout.addWidget(reset_items)
        
        reset_warning = QLabel("Questa azione non può essere annullata.")
        reset_warning.setStyleSheet("color: #dc3545; font-style: italic;")
        reset_layout.addWidget(reset_warning)
        
        reset_btn = QPushButton("Factory Reset")
        reset_btn.setStyleSheet("background-color: #dc3545; color: white; font-weight: bold;")
        reset_btn.clicked.connect(self.factory_reset)
        reset_layout.addWidget(reset_btn)
        
        advanced_layout.addWidget(reset_group)
        advanced_layout.addStretch()
        
        # Aggiungi i tab
        tab_widget.addTab(settings_tab, "Impostazioni")
        tab_widget.addTab(advanced_tab, "Avanzate")
        
        layout.addWidget(tab_widget)
        
        # Gestione della visualizzazione iniziale di T2 in base alla modalità
        self.on_mode_changed()
    
    def on_start_click(self):
        """Invia il comando di avvio al timer"""
        self.server.send_command(self.device_id, "start")
        self.start_btn.setEnabled(False)
        self.pause_btn.setEnabled(True)
    
    def on_pause_click(self):
        """Invia il comando di pausa al timer"""
        self.server.send_command(self.device_id, "pause")
        self.start_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
    
    def on_mode_changed(self):
        """Gestisce il cambio della modalità"""
        current_mode = self.mode.currentData()
        
        # Abilita/disabilita il campo T2 in base alla modalità
        # Modalità 3 e 4 usano solo T1
        self.t2_value.setEnabled(current_mode in [1, 2])
    
    def save_settings(self):
        """Salva le impostazioni del timer"""
        # Raccogli i dati
        settings = {
            'mode': self.mode.currentData(),
            't1': self.t1_value.value(),
            't2': self.t2_value.value(),
            'tableNumber': self.table_number.value(),
            'buzzer': 1 if self.buzzer.isChecked() else 0,
            'playersCount': self.players_count.value()
        }
        
        # Invia le impostazioni al server
        success = self.server.update_settings(self.device_id, settings)
        
        if success:
            QMessageBox.information(self, "Successo", "Impostazioni salvate con successo")
        else:
            QMessageBox.warning(self, "Errore", "Impossibile salvare le impostazioni")
    
    def factory_reset(self):
        """Esegue il factory reset del timer"""
        reply = QMessageBox.warning(
            self, 'Conferma Factory Reset',
            f'Stai per eseguire un FACTORY RESET sul timer del tavolo {self.timer_data.get("table_number", "N/A")}.\n\n'
            'Questo ripristinerà TUTTE le impostazioni ai valori predefiniti.\n'
            'Il timer si disconnetterà dalla rete WiFi e potrebbe non riconnettersi automaticamente.\n\n'
            'Questa azione non può essere annullata.',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Invia il comando di factory reset
            self.server.send_command(self.device_id, "factory_reset")
            QMessageBox.information(self, "Factory Reset", "Comando di factory reset inviato. Il timer si riavvierà.")
            self.accept()  # Chiude la finestra di dialogo