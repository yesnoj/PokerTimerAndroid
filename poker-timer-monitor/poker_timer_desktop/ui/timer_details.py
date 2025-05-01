#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Finestra di dialogo per i dettagli di un timer
"""

import os
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                           QSpinBox, QComboBox, QCheckBox, QTabWidget, QWidget,
                           QGroupBox, QFormLayout, QMessageBox, QLineEdit, QFrame)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QIcon, QPixmap

class TimerDetailsDialog(QDialog):
    """Finestra di dialogo per visualizzare e modificare i dettagli di un timer"""
    def __init__(self, device_id, timer_data, server, parent=None):
        super().__init__(parent)
        self.device_id = device_id
        self.timer_data = timer_data
        self.server = server
        
        # Configurazione finestra
        self.setWindowTitle(f"Timer Details - Table {timer_data.get('table_number', 'N/A')}")
        self.setMinimumSize(600, 500)
        
        # Layout principale
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header con due container
        header_layout = QHBoxLayout()
        
        # Container per il titolo
        title_container = QFrame()
        title_container.setStyleSheet("background-color: white; border: 1px solid #ddd; border-radius: 8px; padding: 10px;")
        title_layout = QHBoxLayout(title_container)
        
        # Titolo
        title = QLabel(f"Timer Details - Table {timer_data.get('table_number', 'N/A')}")
        title.setStyleSheet("color: #007bff; font-size: 18pt; font-weight: bold;")
        title_layout.addWidget(title)
        
        # Container per l'icona
        icon_container = QFrame()
        icon_container.setStyleSheet("background-color: white; border: 1px solid #ddd; border-radius: 8px; padding: 10px;")
        icon_container.setFixedWidth(80)
        icon_layout = QHBoxLayout(icon_container)
        
        # Icona basata sul tipo di dispositivo
        device_icon = QLabel()
        icon_path = ""
        
        if self.is_android_timer(device_id):
            icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                   'resources', 'icons', 'ic_android.svg')
        elif self.is_hardware_timer(device_id):
            icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                   'resources', 'icons', 'ic_hardware.svg')
        
        if icon_path and os.path.exists(icon_path):
            pixmap = QPixmap(icon_path)
            if not pixmap.isNull():
                device_icon.setPixmap(pixmap.scaled(24, 24, Qt.AspectRatioMode.KeepAspectRatio))
            else:
                # Fallback per icone
                device_icon.setText("🔌" if self.is_hardware_timer(device_id) else "🤖")
                device_icon.setStyleSheet("color: #000000; font-size: 24px;")
        else:
            # Fallback per icone
            device_icon.setText("🔌" if self.is_hardware_timer(device_id) else "🤖")
            device_icon.setStyleSheet("color: #000000; font-size: 24px;")
            
        device_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_layout.addWidget(device_icon)
        
        header_layout.addWidget(title_container, 7)
        header_layout.addWidget(icon_container, 3)
        layout.addLayout(header_layout)
        
        # Tab Widget con stile migliorato
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 10px;
                background-color: white;
            }
            QTabBar::tab {
                padding: 8px 16px;
                margin-right: 2px;
                border: 1px solid #ddd;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                font-size: 14pt;
                background-color: #f0f0f0;
                color: #666666;
            }
            QTabBar::tab:selected {
                background: white;
                border-bottom-color: white;
                font-weight: bold;
                color: #007bff;
            }
        """)
        
        # Tab Settings
        settings_tab = QWidget()
        settings_layout = QVBoxLayout(settings_tab)
        
        # Titolo
        settings_title = QLabel("Timer Settings")
        settings_title.setStyleSheet("font-size: 20pt; font-weight: bold; color: #000000;")
        settings_layout.addWidget(settings_title)
        
        # Form per le impostazioni
        form_frame = QFrame()
        form_frame.setStyleSheet("border: 1px solid #ddd; border-radius: 5px; background-color: white;")
        form_layout = QVBoxLayout(form_frame)
        
        # Form principale
        settings_form = QFormLayout()
        settings_form.setVerticalSpacing(20)
        settings_form.setHorizontalSpacing(20)
        
        # Stile comuni
        input_style = "font-size: 14pt; background-color: #f8f9fa; color: #000000; border: 1px solid #ddd; border-radius: 4px; padding: 8px;"
        label_style = "font-size: 14pt; font-weight: bold;"
        button_style = "background-color: #28a745; color: white; font-weight: bold; border: none; border-radius: 4px; font-size: 14pt;"
        
        # Numero tavolo
        table_row = QHBoxLayout()
        table_label = QLabel("Numero Tavolo:")
        table_label.setStyleSheet(label_style)
        table_label.setFixedWidth(180)
        
        self.table_number = QLineEdit(str(timer_data.get('table_number', 0)))
        self.table_number.setStyleSheet(input_style)
        self.table_number.setFixedWidth(180)
        self.table_number.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        minus_btn = QPushButton("-")
        minus_btn.setStyleSheet(button_style)
        minus_btn.setFixedSize(40, 40)
        minus_btn.clicked.connect(lambda: self.decrement_value(self.table_number, 0, 99))
        
        plus_btn = QPushButton("+")
        plus_btn.setStyleSheet(button_style)
        plus_btn.setFixedSize(40, 40)
        plus_btn.clicked.connect(lambda: self.increment_value(self.table_number, 0, 99))
        
        table_row.addWidget(table_label)
        table_row.addWidget(self.table_number)
        table_row.addWidget(minus_btn)
        table_row.addWidget(plus_btn)
        table_row.addStretch()
        
        # Numero Giocatori
        players_row = QHBoxLayout()
        players_label = QLabel("Numero Giocatori:")
        players_label.setStyleSheet(label_style)
        players_label.setFixedWidth(180)
        
        self.players_count = QLineEdit(str(timer_data.get('players_count', 6)))
        self.players_count.setStyleSheet(input_style)
        self.players_count.setFixedWidth(180)
        self.players_count.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        minus_btn2 = QPushButton("-")
        minus_btn2.setStyleSheet(button_style)
        minus_btn2.setFixedSize(40, 40)
        minus_btn2.clicked.connect(lambda: self.decrement_value(self.players_count, 1, 10))
        
        plus_btn2 = QPushButton("+")
        plus_btn2.setStyleSheet(button_style)
        plus_btn2.setFixedSize(40, 40)
        plus_btn2.clicked.connect(lambda: self.increment_value(self.players_count, 1, 10))
        
        players_row.addWidget(players_label)
        players_row.addWidget(self.players_count)
        players_row.addWidget(minus_btn2)
        players_row.addWidget(plus_btn2)
        players_row.addStretch()
        
        # Timer T1
        t1_row = QHBoxLayout()
        t1_label = QLabel("Timer T1:")
        t1_label.setStyleSheet(label_style)
        t1_label.setFixedWidth(180)
        
        self.t1_value = QLineEdit(str(timer_data.get('t1_value', 25)))
        self.t1_value.setStyleSheet(input_style)
        self.t1_value.setFixedWidth(180)
        self.t1_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Restricting to multiples of 5
        self.t1_value.textChanged.connect(lambda t: self.validate_timer_value(self.t1_value))
        
        minus_btn3 = QPushButton("-")
        minus_btn3.setStyleSheet(button_style)
        minus_btn3.setFixedSize(40, 40)
        minus_btn3.clicked.connect(lambda: self.decrement_value(self.t1_value, 5, 95, 5))
        
        plus_btn3 = QPushButton("+")
        plus_btn3.setStyleSheet(button_style)
        plus_btn3.setFixedSize(40, 40)
        plus_btn3.clicked.connect(lambda: self.increment_value(self.t1_value, 5, 95, 5))
        
        t1_row.addWidget(t1_label)
        t1_row.addWidget(self.t1_value)
        t1_row.addWidget(minus_btn3)
        t1_row.addWidget(plus_btn3)
        t1_row.addStretch()
        
        # Timer T2
        t2_row = QHBoxLayout()
        self.t2_label = QLabel("Timer T2:")
        self.t2_label.setStyleSheet(label_style)
        self.t2_label.setFixedWidth(180)
        
        self.t2_value = QLineEdit(str(timer_data.get('t2_value', 20)))
        self.t2_value.setStyleSheet(input_style)
        self.t2_value.setFixedWidth(180)
        self.t2_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Restricting to multiples of 5
        self.t2_value.textChanged.connect(lambda t: self.validate_timer_value(self.t2_value))
        
        self.minus_btn4 = QPushButton("-")
        self.minus_btn4.setStyleSheet(button_style)
        self.minus_btn4.setFixedSize(40, 40)
        self.minus_btn4.clicked.connect(lambda: self.decrement_value(self.t2_value, 5, 95, 5))
        
        self.plus_btn4 = QPushButton("+")
        self.plus_btn4.setStyleSheet(button_style)
        self.plus_btn4.setFixedSize(40, 40)
        self.plus_btn4.clicked.connect(lambda: self.increment_value(self.t2_value, 5, 95, 5))
        
        t2_row.addWidget(self.t2_label)
        t2_row.addWidget(self.t2_value)
        t2_row.addWidget(self.minus_btn4)
        t2_row.addWidget(self.plus_btn4)
        t2_row.addStretch()
        
        # Operation Mode
        mode_row = QHBoxLayout()
        self.mode_label = QLabel("Operation Mode:")
        self.mode_label.setStyleSheet(label_style)
        self.mode_label.setFixedWidth(180)
        
        self.mode_select = QComboBox()
        self.mode_select.addItem("Mode 1: T1/T2 with automatic start", 1)
        self.mode_select.addItem("Mode 2: T1/T2 with manual start", 2)
        self.mode_select.addItem("Mode 3: T1 only with automatic start", 3)
        self.mode_select.addItem("Mode 4: T1 only with manual start", 4)
        self.mode_select.setCurrentIndex(self.mode_select.findData(timer_data.get('mode', 1)))
        self.mode_select.setStyleSheet(input_style)
        self.mode_select.currentIndexChanged.connect(self.on_mode_changed)
        
        mode_row.addWidget(self.mode_label)
        mode_row.addWidget(self.mode_select)
        mode_row.addStretch()
        
        # Buzzer
        buzzer_row = QHBoxLayout()
        buzzer_label = QLabel("Buzzer:")
        buzzer_label.setStyleSheet(label_style)
        buzzer_label.setFixedWidth(180)
        
        self.buzzer = QCheckBox()
        self.buzzer.setChecked(timer_data.get('buzzer', False))
        self.buzzer.setStyleSheet("""
            QCheckBox::indicator {
                width: 40px;
                height: 20px;
                border-radius: 10px;
            }
            QCheckBox::indicator:unchecked {
                background-color: #ccc;
            }
            QCheckBox::indicator:checked {
                background-color: #28a745;
            }
        """)
        
        buzzer_row.addWidget(buzzer_label)
        buzzer_row.addWidget(self.buzzer)
        buzzer_row.addStretch()
        
        # Add all rows to the form layout
        form_layout.addLayout(table_row)
        form_layout.addLayout(players_row)
        form_layout.addLayout(t1_row)
        form_layout.addLayout(t2_row)
        
        # Aggiungi mode solo per timer hardware
        if not self.is_android_timer(device_id):
            form_layout.addLayout(mode_row)
        else:
            # Nascondi gli elementi per Android timer
            self.mode_label.hide()
            self.mode_select.hide()
        
        form_layout.addLayout(buzzer_row)
        form_layout.addStretch()
        
        settings_layout.addWidget(form_frame)
        
        # Pulsanti
        save_btn = QPushButton("Save Settings")
        save_btn.setStyleSheet("background-color: #007bff; color: white; border: none; border-radius: 4px; padding: 12px; font-size: 16pt; font-weight: bold;")
        save_btn.clicked.connect(self.save_settings)
        settings_layout.addWidget(save_btn)
        
        close_btn = QPushButton("Chiudi")
        close_btn.setStyleSheet("background-color: #6c757d; color: white; border: none; border-radius: 4px; padding: 12px; font-size: 16pt;")
        close_btn.clicked.connect(self.accept)
        settings_layout.addWidget(close_btn)
        
        # Tab Advanced
        advanced_tab = QWidget()
        advanced_layout = QVBoxLayout(advanced_tab)
        
        advanced_title = QLabel("Advanced Options")
        advanced_title.setStyleSheet("font-size: 20pt; font-weight: bold; color: #000000;")
        advanced_layout.addWidget(advanced_title)
        
        warning_label = QLabel("<strong>Warning:</strong> These options can permanently affect the timer's functionality.<br>Use with caution!")
        warning_label.setStyleSheet("background-color: #f8d7da; color: #721c24; padding: 15px; border-radius: 4px; border: 1px solid #f5c6cb; font-size: 14pt;")
        advanced_layout.addWidget(warning_label)
        
        # Factory Reset
        reset_group = QGroupBox("Factory Reset")
        reset_group.setStyleSheet("font-size: 16pt; font-weight: bold; margin-top: 20px;")
        reset_layout = QVBoxLayout(reset_group)
        
        reset_info = QLabel("This will restore ALL settings to factory defaults including timer values, table number, buzzer settings, operation mode, and WiFi settings.")
        reset_info.setStyleSheet("font-size: 14pt; font-weight: normal;")
        reset_info.setWordWrap(True)
        reset_layout.addWidget(reset_info)
        
        reset_btn = QPushButton("Factory Reset")
        reset_btn.setStyleSheet("background-color: #dc3545; color: white; border: none; border-radius: 4px; padding: 10px; font-size: 16pt; font-weight: bold;")
        reset_btn.clicked.connect(self.confirm_factory_reset)
        reset_layout.addWidget(reset_btn)
        
        advanced_layout.addWidget(reset_group)
        advanced_layout.addStretch()
        
        # Add tabs
        self.tab_widget.addTab(settings_tab, "Settings")
        self.tab_widget.addTab(advanced_tab, "Advanced")
        layout.addWidget(self.tab_widget)
        
        # Inizializza UI in base alla modalità
        self.update_ui_based_on_mode()
    
    def validate_timer_value(self, field):
        """Verifica che il valore del timer sia un multiplo di 5"""
        try:
            value = int(field.text())
            if value < 5 or value > 95 or value % 5 != 0:
                # Valore non valido, imposta il multiplo di 5 più vicino
                nearest = round(value / 5) * 5
                if nearest < 5:
                    nearest = 5
                elif nearest > 95:
                    nearest = 95
                field.setText(str(nearest))
        except ValueError:
            # Se non è un numero, imposta il valore predefinito
            field.setText("25")
    
    def is_android_timer(self, device_id):
        """Determina se un timer è un'app Android basato sul device_id"""
        return device_id and device_id.startswith('android_')
    
    def is_hardware_timer(self, device_id):
        """Determina se un timer è hardware (ESP32/Arduino) basato sul device_id"""
        return device_id and device_id.startswith('arduino_')
    
    def update_ui_based_on_mode(self):
        """Aggiorna l'interfaccia in base alla modalità selezionata"""
        # Ottieni la modalità corrente
        mode = self.mode_select.currentData()
        
        # Per le modalità solo T1 (3 e 4), nascondi T2
        if mode in [3, 4]:
            self.t2_label.setVisible(False)
            self.t2_value.setVisible(False)
            self.minus_btn4.setVisible(False)
            self.plus_btn4.setVisible(False)
        else:
            self.t2_label.setVisible(True)
            self.t2_value.setVisible(True)
            self.minus_btn4.setVisible(True)
            self.plus_btn4.setVisible(True)
    
    def on_mode_changed(self, index):
        """Gestisce il cambio della modalità"""
        self.update_ui_based_on_mode()
    
    def increment_value(self, field, min_val, max_val, step=1):
        """Incrementa il valore di un campo"""
        try:
            current = int(field.text())
            new_val = min(current + step, max_val)
            field.setText(str(new_val))
        except (ValueError, TypeError):
            field.setText(str(min_val))
    
    def decrement_value(self, field, min_val, max_val, step=1):
        """Decrementa il valore di un campo"""
        try:
            current = int(field.text())
            new_val = max(current - step, min_val)
            field.setText(str(new_val))
        except (ValueError, TypeError):
            field.setText(str(min_val))
    
    def confirm_factory_reset(self):
        """Mostra dialogo di conferma per il factory reset"""
        reply = QMessageBox.question(
            self, 
            '⚠️ Factory Reset Confirmation',
            f"You are about to perform a <strong>FACTORY RESET</strong> on:<br><br>"
            f"<div style='text-align: center; font-weight: bold; font-size: 16px;'>Table {self.timer_data.get('table_number', 'N/A')}</div><br>"
            f"This will restore ALL settings to factory defaults.<br>"
            f"The timer will disconnect from WiFi and may not reconnect automatically.<br><br>"
            f"This action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.execute_factory_reset()
    
    def execute_factory_reset(self):
        """Invia il comando di factory reset al timer"""
        try:
            self.server.send_command(self.device_id, "factory_reset")
            self.accept()
            QMessageBox.information(
                None, 
                'Factory Reset',
                'Factory reset command sent. The timer will restart and may disconnect from the network.'
            )
        except Exception as e:
            print(f"Errore nell'invio del comando factory reset: {e}")
            QMessageBox.critical(
                None, 
                'Error',
                f'Error sending factory reset command: {str(e)}'
            )
    
    def save_settings(self):
        """Salva le impostazioni del timer"""
        try:
            # Validazione dei campi
            try:
                table_num = int(self.table_number.text())
                players = int(self.players_count.text())
                t1 = int(self.t1_value.text())
                t2 = int(self.t2_value.text())
                
                # Verifica i valori
                if table_num < 0 or table_num > 99:
                    raise ValueError("Table number must be between 0 and 99")
                if players < 1 or players > 10:
                    raise ValueError("Players count must be between 1 and 10")
                if t1 < 5 or t1 > 95 or t1 % 5 != 0:
                    raise ValueError("T1 must be between 5 and 95 and a multiple of 5")
                if t2 < 5 or t2 > 95 or t2 % 5 != 0:
                    raise ValueError("T2 must be between 5 and 95 and a multiple of 5")
            except ValueError as e:
                QMessageBox.warning(self, "Errore", str(e))
                return
            
            # Ottieni la modalità dal combobox (solo per hardware timer)
            mode = 1  # Valore predefinito
            if not self.is_android_timer(self.device_id):
                mode = self.mode_select.currentData()
            
            settings = {
                'mode': mode,
                't1': t1,
                't2': t2,
                'tableNumber': table_num,
                'buzzer': 1 if self.buzzer.isChecked() else 0,
                'playersCount': players
            }
            
            # Invia le impostazioni al server
            success = self.server.update_settings(self.device_id, settings)
            
            if success:
                # Invia anche un comando per applicare immediatamente le impostazioni
                self.server.send_command(self.device_id, "apply_settings")
                QMessageBox.information(self, "Successo", "Impostazioni salvate e applicate con successo!")
            else:
                QMessageBox.warning(self, "Errore", "Impossibile salvare le impostazioni")
        except Exception as e:
            print(f"Errore nel salvataggio delle impostazioni: {e}")
            QMessageBox.critical(self, "Errore", f"Errore nel salvataggio: {str(e)}")