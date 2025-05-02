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
        self.setMinimumSize(500, 500)  # Ridotta la larghezza minima
        self.setMaximumWidth(550)      # Limitata la larghezza massima
        
        # Layout principale
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # ---- HEADER ----
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(15)  # Aggiunge spazio tra il titolo e l'icona

        # Titolo "Table X"
        self.title_label = QLabel(f"Table {timer_data.get('table_number', 'N/A')}")
        self.title_label.setStyleSheet("font-size: 18pt; font-weight: bold; color: #000000;")
        header_layout.addWidget(self.title_label, alignment=Qt.AlignmentFlag.AlignLeft)

        # Icona dispositivo (Android o Arduino)
        device_icon = QLabel()
        if self.is_android_timer(device_id):
            # Usa l'icona SVG di Android
            icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                   'resources', 'icons', 'ic_android.svg')
            if os.path.exists(icon_path):
                # Carica l'icona come QIcon
                icon = QIcon(icon_path)
                # Crea un QPixmap dalle dimensioni desiderate
                pixmap = icon.pixmap(24, 24)
                # Imposta il pixmap sulla QLabel
                device_icon.setPixmap(pixmap)
                device_icon.setToolTip("Android App")
            else:
                # Emoji visibile come fallback
                device_icon.setText("🤖")
                device_icon.setStyleSheet("color: #000000; font-size: 22px;")
                device_icon.setToolTip("Android App")
        elif self.is_hardware_timer(device_id):
            # Usa l'icona SVG di Hardware
            icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                   'resources', 'icons', 'ic_hardware.svg')
            if os.path.exists(icon_path):
                # Carica l'icona come QIcon
                icon = QIcon(icon_path)
                # Crea un QPixmap dalle dimensioni desiderate
                pixmap = icon.pixmap(24, 24)
                # Imposta il pixmap sulla QLabel
                device_icon.setPixmap(pixmap)
                device_icon.setToolTip("Hardware Timer")
            else:
                # Emoji visibile come fallback
                device_icon.setText("🔌")
                device_icon.setStyleSheet("color: #000000; font-size: 22px;")
                device_icon.setToolTip("Hardware Timer")

        header_layout.addWidget(device_icon, alignment=Qt.AlignmentFlag.AlignLeft)

        # Aggiungi stretch alla fine per garantire l'allineamento a sinistra
        header_layout.addStretch(1)
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
        settings_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Centra tutto il contenuto
        
        # Titolo
        settings_title = QLabel("Timer Settings")
        settings_title.setStyleSheet("font-size: 20pt; font-weight: bold; color: #000000;")
        settings_title.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Centra il titolo
        settings_layout.addWidget(settings_title)
        
        # Form per le impostazioni
        form_frame = QFrame()
        form_frame.setStyleSheet("border: 1px solid #ddd; border-radius: 5px; background-color: white;")
        form_layout = QVBoxLayout(form_frame)
        form_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Centra il contenuto del form
        
        # Stile comuni
        input_style = "font-size: 14pt; background-color: #f8f9fa; color: #000000; border: 1px solid #ddd; border-radius: 4px; padding: 8px;"
        label_style = "font-size: 14pt; font-weight: bold;"
        button_style = "background-color: #28a745; color: white; font-weight: bold; border: none; border-radius: 4px; font-size: 14pt;"
        
        # Numero tavolo
        table_row = QHBoxLayout()
        table_row.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Centra la riga
        
        table_label = QLabel("Numero Tavolo:")
        table_label.setStyleSheet(label_style)
        table_label.setFixedWidth(160)
        
        self.table_number = QLineEdit(str(timer_data.get('table_number', 0)))
        self.table_number.setStyleSheet(input_style)
        self.table_number.setFixedWidth(40)
        self.table_number.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Rimozione della connessione automatica
        # self.table_number.textChanged.connect(self.update_title)
        
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
        
        # Numero Giocatori
        players_row = QHBoxLayout()
        players_row.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Centra la riga
        
        players_label = QLabel("Numero Giocatori:")
        players_label.setStyleSheet(label_style)
        players_label.setFixedWidth(160)
        
        self.players_count = QLineEdit(str(timer_data.get('players_count', 6)))
        self.players_count.setStyleSheet(input_style)
        self.players_count.setFixedWidth(40)
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
        
        # Timer T1
        t1_row = QHBoxLayout()
        t1_row.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Centra la riga
        
        t1_label = QLabel("Timer T1:")
        t1_label.setStyleSheet(label_style)
        t1_label.setFixedWidth(160)
        
        self.t1_value = QLineEdit(str(timer_data.get('t1_value', 25)))
        self.t1_value.setStyleSheet(input_style)
        self.t1_value.setFixedWidth(40)
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
        
        # Timer T2
        t2_row = QHBoxLayout()
        t2_row.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Centra la riga
        
        self.t2_label = QLabel("Timer T2:")
        self.t2_label.setStyleSheet(label_style)
        self.t2_label.setFixedWidth(160)
        
        self.t2_value = QLineEdit(str(timer_data.get('t2_value', 20)))
        self.t2_value.setStyleSheet(input_style)
        self.t2_value.setFixedWidth(40)
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
        
        # Operation Mode
        mode_row = QHBoxLayout()
        mode_row.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Centra la riga
        
        self.mode_label = QLabel("Operation Mode:")
        self.mode_label.setStyleSheet(label_style)
        self.mode_label.setFixedWidth(160)
        
        self.mode_select = QComboBox()
        self.mode_select.addItem("Mode 1: T1/T2 auto start", 1)
        self.mode_select.addItem("Mode 2: T1/T2 manual start", 2)
        self.mode_select.addItem("Mode 3: T1 and auto start", 3)
        self.mode_select.addItem("Mode 4: T1 and manual start", 4)
        self.mode_select.setCurrentIndex(self.mode_select.findData(timer_data.get('mode', 1)))
        self.mode_select.setStyleSheet(input_style)
        self.mode_select.currentIndexChanged.connect(self.on_mode_changed)
        self.mode_select.setFixedWidth(210)
        
        mode_row.addWidget(self.mode_label)
        mode_row.addWidget(self.mode_select)
        
        # Buzzer - Nuovo approccio con un toggle switch usando QPushButton personalizzato
        buzzer_row = QHBoxLayout()
        buzzer_row.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Centra la riga
        
        buzzer_label = QLabel("Buzzer:")
        buzzer_label.setStyleSheet(label_style)
        buzzer_label.setFixedWidth(160)
        
        # Creiamo un pulsante personalizzato per lo switch
        self.buzzer_switch = QPushButton()
        self.buzzer_switch.setFixedSize(60, 30)
        self.buzzer_switch.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Mettiamo un valore nascosto per tenere traccia dello stato
        self.buzzer_state = timer_data.get('buzzer', False)
        
        # Imposta lo stile iniziale in base allo stato
        self.update_buzzer_switch_style()
        
        # Connetti il click al toggle
        self.buzzer_switch.clicked.connect(self.toggle_buzzer)
        
        buzzer_row.addWidget(buzzer_label)
        buzzer_row.addWidget(self.buzzer_switch)
        
        # Add all rows to the form layout with spaziatura
        form_layout.addSpacing(10)
        form_layout.addLayout(table_row)
        form_layout.addSpacing(15)
        form_layout.addLayout(players_row)
        form_layout.addSpacing(15)
        form_layout.addLayout(t1_row)
        form_layout.addSpacing(15)
        form_layout.addLayout(t2_row)
        form_layout.addSpacing(15)
        
        # Aggiungi mode solo per timer hardware
        if not self.is_android_timer(device_id):
            form_layout.addLayout(mode_row)
            form_layout.addSpacing(15)
        else:
            # Nascondi gli elementi per Android timer
            self.mode_label.hide()
            self.mode_select.hide()
        
        form_layout.addLayout(buzzer_row)
        form_layout.addSpacing(10)
        
        settings_layout.addWidget(form_frame)
        
        # Pulsanti
        buttons_layout = QHBoxLayout()
        buttons_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Centra i pulsanti
        
        save_btn = QPushButton("Save Settings")
        save_btn.setStyleSheet("background-color: #007bff; color: white; border: none; border-radius: 4px; padding: 12px; font-size: 16pt; font-weight: bold;")
        save_btn.clicked.connect(self.save_settings)
        save_btn.setFixedWidth(250)
        
        close_btn = QPushButton("Chiudi")
        close_btn.setStyleSheet("background-color: #6c757d; color: white; border: none; border-radius: 4px; padding: 12px; font-size: 16pt;")
        close_btn.clicked.connect(self.accept)
        close_btn.setFixedWidth(250)
        
        buttons_layout.addWidget(save_btn)
        settings_layout.addLayout(buttons_layout)
        settings_layout.addSpacing(10)
        
        buttons_layout2 = QHBoxLayout()
        buttons_layout2.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Centra i pulsanti
        buttons_layout2.addWidget(close_btn)
        settings_layout.addLayout(buttons_layout2)
        
        # Tab Advanced
        advanced_tab = QWidget()
        advanced_layout = QVBoxLayout(advanced_tab)
        advanced_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Centra il contenuto
        
        advanced_title = QLabel("Advanced Options")
        advanced_title.setStyleSheet("font-size: 20pt; font-weight: bold; color: #000000;")
        advanced_title.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Centra il titolo
        advanced_layout.addWidget(advanced_title)
        
        warning_label = QLabel("<strong>Warning:</strong> These options can permanently affect the timer's functionality.<br>Use with caution!")
        warning_label.setStyleSheet("background-color: #f8d7da; color: #721c24; padding: 15px; border-radius: 4px; border: 1px solid #f5c6cb; font-size: 14pt;")
        warning_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Centra il testo di avviso
        advanced_layout.addWidget(warning_label)
        
        # Factory Reset
        reset_group = QGroupBox("Factory Reset")
        reset_group.setStyleSheet("font-size: 16pt; font-weight: bold; margin-top: 20px;")
        reset_layout = QVBoxLayout(reset_group)
        reset_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Centra il contenuto
        
        reset_info = QLabel("This will restore ALL settings to factory defaults including timer values, table number, buzzer settings, operation mode, and WiFi settings.")
        reset_info.setStyleSheet("font-size: 14pt; font-weight: normal;")
        reset_info.setWordWrap(True)
        reset_info.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Centra il testo
        reset_layout.addWidget(reset_info)
        
        reset_btn = QPushButton("Factory Reset")
        reset_btn.setStyleSheet("background-color: #dc3545; color: white; border: none; border-radius: 4px; padding: 10px; font-size: 16pt; font-weight: bold;")
        reset_btn.clicked.connect(self.confirm_factory_reset)
        reset_btn.setFixedWidth(250)
        
        reset_layout.addWidget(reset_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        advanced_layout.addWidget(reset_group)
        
        # Add tabs
        self.tab_widget.addTab(settings_tab, "Settings")
        self.tab_widget.addTab(advanced_tab, "Advanced")
        layout.addWidget(self.tab_widget)
        
        # Inizializza UI in base alla modalità
        self.update_ui_based_on_mode()
    
    def update_title(self):
        """Aggiorna il titolo quando cambia il numero del tavolo"""
        try:
            table_num = int(self.table_number.text())
            self.title_label.setText(f"Table {table_num}")
        except ValueError:
            # In caso di valore non valido, mostra N/A
            self.title_label.setText("Table N/A")
    
    def update_buzzer_switch_style(self):
        """Aggiorna lo stile dello switch buzzer in base allo stato corrente"""
        if self.buzzer_state:
            # Stile per ON
            self.buzzer_switch.setStyleSheet("""
                QPushButton {
                    background-color: #28a745;
                    border-radius: 15px;
                    text-align: right;
                    padding-right: 5px;
                    color: white;
                }
                QPushButton:hover {
                    background-color: #218838;
                }
            """)
            self.buzzer_switch.setText("ON ")
        else:
            # Stile per OFF
            self.buzzer_switch.setStyleSheet("""
                QPushButton {
                    background-color: #ccc;
                    border-radius: 15px;
                    text-align: left;
                    padding-left: 5px;
                    color: #666;
                }
                QPushButton:hover {
                    background-color: #bbb;
                }
            """)
            self.buzzer_switch.setText(" OFF")
    
    def toggle_buzzer(self):
        """Toggle lo stato del buzzer switch"""
        self.buzzer_state = not self.buzzer_state
        self.update_buzzer_switch_style()
    
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
        """Salva le impostazioni del timer e aggiorna il titolo"""
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
                'buzzer': 1 if self.buzzer_state else 0,  # Usa lo stato del custom toggle switch
                'playersCount': players
            }
            
            # Invia le impostazioni al server
            success = self.server.update_settings(self.device_id, settings)
            
            if success:
                # Invia anche un comando per applicare immediatamente le impostazioni
                self.server.send_command(self.device_id, "apply_settings")
                
                # Aggiorna il titolo della finestra e il titolo del header
                self.title_label.setText(f"Table {table_num}")
                self.setWindowTitle(f"Timer Details - Table {table_num}")
                
                QMessageBox.information(self, "Successo", "Impostazioni salvate e applicate con successo!")
            else:
                QMessageBox.warning(self, "Errore", "Impossibile salvare le impostazioni")
        except Exception as e:
            print(f"Errore nel salvataggio delle impostazioni: {e}")
            QMessageBox.critical(self, "Errore", f"Errore nel salvataggio: {str(e)}")