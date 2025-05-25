#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Finestra di dialogo per i dettagli di un timer
"""

import os
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                           QComboBox, QTabWidget, QWidget, QGroupBox, QMessageBox, 
                           QLineEdit, QFrame, QGridLayout)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPixmap, QFont

class TimerDetailsDialog(QDialog):
    """Finestra di dialogo per visualizzare e modificare i dettagli di un timer"""
    def __init__(self, device_id, timer_data, server, parent=None):
        super().__init__(parent)
        self.device_id = device_id
        self.timer_data = timer_data
        self.server = server
        
        # Configurazione finestra
        self.setWindowTitle(f"Timer Details - Table {timer_data.get('table_number', 'N/A')}")
        self.setMinimumSize(400, 500)  # Leggermente più alta
        self.setMaximumWidth(450)
        
        # Layout principale
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(5)
        
        # ---- HEADER ----
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(5)

        # Titolo "Table X"
        self.title_label = QLabel(f"Table {timer_data.get('table_number', 'N/A')}")
        self.title_label.setStyleSheet("font-size: 14pt; font-weight: bold; color: #000000;")
        header_layout.addWidget(self.title_label, alignment=Qt.AlignmentFlag.AlignLeft)

        # Icona dispositivo (Android o Arduino)
        device_icon = QLabel()
        if self.is_android_timer(device_id):
            icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                   'resources', 'icons', 'ic_android.svg')
            if os.path.exists(icon_path):
                icon = QIcon(icon_path)
                pixmap = icon.pixmap(18, 18)
                device_icon.setPixmap(pixmap)
                device_icon.setToolTip("Android App")
            else:
                device_icon.setText("🤖")
                device_icon.setStyleSheet("color: #000000; font-size: 16px;")
                device_icon.setToolTip("Android App")
        elif self.is_hardware_timer(device_id):
            icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                   'resources', 'icons', 'ic_hardware.svg')
            if os.path.exists(icon_path):
                icon = QIcon(icon_path)
                pixmap = icon.pixmap(18, 18)
                device_icon.setPixmap(pixmap)
                device_icon.setToolTip("Hardware Timer")
            else:
                device_icon.setText("🔌")
                device_icon.setStyleSheet("color: #000000; font-size: 16px;")
                device_icon.setToolTip("Hardware Timer")

        header_layout.addWidget(device_icon, alignment=Qt.AlignmentFlag.AlignLeft)
        header_layout.addStretch(1)
        layout.addLayout(header_layout)
        
        # Tab Widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #ddd; border-radius: 4px; padding: 5px; background-color: white; }
            QTabBar::tab { padding: 6px 12px; margin-right: 2px; border: 1px solid #ddd; 
                           border-bottom: none; border-top-left-radius: 4px; border-top-right-radius: 4px; 
                           font-size: 12pt; background-color: #f0f0f0; color: #666666; }
            QTabBar::tab:selected { background: white; border-bottom-color: white; 
                                    font-weight: bold; color: #007bff; }
        """)
        
        # Tab Settings
        settings_tab = QWidget()
        settings_layout = QVBoxLayout(settings_tab)
        settings_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        settings_layout.setSpacing(10)
        
        # Stili comuni
        input_style = "font-size: 12pt; background-color: #f8f9fa; color: #000000; border: 1px solid #ddd; border-radius: 4px; padding: 5px;"
        label_style = "font-size: 12pt; font-weight: bold;"
        
        # Funzione helper per creare bottoni +/-
        def create_increment_button(is_plus=True):
            btn = QPushButton("+" if is_plus else "-")
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #28a745; 
                    color: white; 
                    font-weight: bold; 
                    border: none; 
                    border-radius: 4px; 
                    font-size: 14pt;
                }
                QPushButton:hover {
                    background-color: #218838;
                }
            """)
            btn.setFixedSize(40, 40)  # Bottoni più grandi
            return btn
        
        # Griglia per le impostazioni
        settings_grid = QGridLayout()
        settings_grid.setVerticalSpacing(10)
        settings_grid.setHorizontalSpacing(10)
        
        # Numero tavolo
        table_label = QLabel("Numero Tavolo:")
        table_label.setStyleSheet(label_style)
        self.table_number = QLineEdit(str(timer_data.get('table_number', 0)))
        self.table_number.setStyleSheet(input_style)
        self.table_number.setFixedWidth(50)
        self.table_number.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        minus_btn = create_increment_button(False)
        minus_btn.clicked.connect(lambda: self.decrement_value(self.table_number, 0, 99))
        
        plus_btn = create_increment_button(True)
        plus_btn.clicked.connect(lambda: self.increment_value(self.table_number, 0, 99))
        
        settings_grid.addWidget(table_label, 0, 0)
        settings_grid.addWidget(self.table_number, 0, 1)
        settings_grid.addWidget(minus_btn, 0, 2)
        settings_grid.addWidget(plus_btn, 0, 3)
        
        # Numero Giocatori
        players_label = QLabel("Numero Giocatori:")
        players_label.setStyleSheet(label_style)
        self.players_count = QLineEdit(str(timer_data.get('players_count', 6)))
        self.players_count.setStyleSheet(input_style)
        self.players_count.setFixedWidth(50)
        self.players_count.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        minus_btn2 = create_increment_button(False)
        minus_btn2.clicked.connect(lambda: self.decrement_value(self.players_count, 1, 10))
        
        plus_btn2 = create_increment_button(True)
        plus_btn2.clicked.connect(lambda: self.increment_value(self.players_count, 1, 10))
        
        settings_grid.addWidget(players_label, 1, 0)
        settings_grid.addWidget(self.players_count, 1, 1)
        settings_grid.addWidget(minus_btn2, 1, 2)
        settings_grid.addWidget(plus_btn2, 1, 3)
        
        # Timer T1
        t1_label = QLabel("Timer T1:")
        t1_label.setStyleSheet(label_style)
        self.t1_value = QLineEdit(str(timer_data.get('t1_value', 25)))
        self.t1_value.setStyleSheet(input_style)
        self.t1_value.setFixedWidth(50)
        self.t1_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.t1_value.textChanged.connect(lambda t: self.validate_timer_value(self.t1_value))
        
        minus_btn3 = create_increment_button(False)
        minus_btn3.clicked.connect(lambda: self.decrement_value(self.t1_value, 5, 95, 5))
        
        plus_btn3 = create_increment_button(True)
        plus_btn3.clicked.connect(lambda: self.increment_value(self.t1_value, 5, 95, 5))
        
        settings_grid.addWidget(t1_label, 2, 0)
        settings_grid.addWidget(self.t1_value, 2, 1)
        settings_grid.addWidget(minus_btn3, 2, 2)
        settings_grid.addWidget(plus_btn3, 2, 3)
        
        # Timer T2
        self.t2_label = QLabel("Timer T2:")
        self.t2_label.setStyleSheet(label_style)
        self.t2_value = QLineEdit(str(timer_data.get('t2_value', 20)))
        self.t2_value.setStyleSheet(input_style)
        self.t2_value.setFixedWidth(50)
        self.t2_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.t2_value.textChanged.connect(lambda t: self.validate_timer_value(self.t2_value))
        
        minus_btn4 = create_increment_button(False)
        minus_btn4.clicked.connect(lambda: self.decrement_value(self.t2_value, 5, 95, 5))
        
        plus_btn4 = create_increment_button(True)
        plus_btn4.clicked.connect(lambda: self.increment_value(self.t2_value, 5, 95, 5))
        
        settings_grid.addWidget(self.t2_label, 3, 0)
        settings_grid.addWidget(self.t2_value, 3, 1)
        settings_grid.addWidget(minus_btn4, 3, 2)
        settings_grid.addWidget(plus_btn4, 3, 3)
        
        # Buzzer
        buzzer_label = QLabel("Buzzer:")
        buzzer_label.setStyleSheet(label_style)
        
        self.buzzer_switch = QPushButton()
        self.buzzer_switch.setFixedSize(60, 30)
        self.buzzer_switch.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self.buzzer_state = timer_data.get('buzzer', False)
        self.update_buzzer_switch_style()
        self.buzzer_switch.clicked.connect(self.toggle_buzzer)
        
        settings_grid.addWidget(buzzer_label, 4, 0)
        settings_grid.addWidget(self.buzzer_switch, 4, 1)
        
        # Operation Mode (solo per hardware timer)
        if not self.is_android_timer(device_id):
            self.mode_label = QLabel("Operation Mode:")
            self.mode_label.setStyleSheet(label_style)
            self.mode_select = QComboBox()
            self.mode_select.addItem("Mode 1: T1/T2 auto start", 1)
            self.mode_select.addItem("Mode 2: T1/T2 manual start", 2)
            self.mode_select.addItem("Mode 3: T1 and auto start", 3)
            self.mode_select.addItem("Mode 4: T1 and manual start", 4)
            self.mode_select.setCurrentIndex(self.mode_select.findData(timer_data.get('mode', 1)))
            self.mode_select.setStyleSheet(input_style)
            self.mode_select.currentIndexChanged.connect(self.on_mode_changed)
            
            settings_grid.addWidget(self.mode_label, 5, 0, 1, 2)
            settings_grid.addWidget(self.mode_select, 5, 2, 1, 2)
        
        # Aggiungi la griglia al layout
        settings_layout.addLayout(settings_grid)
        
        # Pulsanti
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        buttons_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        save_btn = QPushButton("Save Settings")
        save_btn.setStyleSheet("background-color: #007bff; color: white; border: none; border-radius: 4px; padding: 8px; font-size: 12pt; font-weight: bold;")
        save_btn.clicked.connect(self.save_settings)
        save_btn.setFixedWidth(150)
        
        close_btn = QPushButton("Chiudi")
        close_btn.setStyleSheet("background-color: #6c757d; color: white; border: none; border-radius: 4px; padding: 8px; font-size: 12pt;")
        close_btn.clicked.connect(self.accept)
        close_btn.setFixedWidth(150)
        
        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(close_btn)
        settings_layout.addLayout(buttons_layout)
        
        # Tab Advanced
        advanced_tab = QWidget()
        advanced_layout = QVBoxLayout(advanced_tab)
        advanced_layout.setSpacing(15)
        advanced_layout.setContentsMargins(15, 15, 15, 15)
        
        # Warning con sfondo rosa e testo più grande
        warning_label = QLabel("<strong>Warning:</strong> These options can permanently affect the timer's functionality.")
        warning_label.setStyleSheet("""
            background-color: #f8d7da; 
            color: #721c24; 
            padding: 12px; 
            border-radius: 6px; 
            font-size: 13pt; 
            text-align: center;
        """)
        warning_label.setWordWrap(True)
        advanced_layout.addWidget(warning_label)
        
        # Factory Reset con layout più ampio
        reset_layout = QVBoxLayout()
        reset_layout.setSpacing(10)
        reset_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Descrizione reset con testo più grande
        reset_info = QLabel("This will restore ALL settings to factory defaults including timer values, table number, buzzer settings, operation mode, and WiFi settings.")
        reset_info.setStyleSheet("""font-size: 12pt; 
            font-weight: normal; 
            color: #333; 
            margin-bottom: 15px;
            text-align: center;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
        """)
        reset_info.setWordWrap(True)
        reset_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Bottone Factory Reset con stile più prominente
        reset_btn = QPushButton("Factory Reset")
        reset_btn.setStyleSheet("""
            background-color: #dc3545; 
            color: white; 
            border: none; 
            border-radius: 6px; 
            padding: 10px 20px; 
            font-size: 14pt; 
            font-weight: bold;
        """)
        reset_btn.clicked.connect(self.confirm_factory_reset)
        reset_btn.setFixedWidth(250)
        
        # Aggiungi elementi al layout
        reset_layout.addWidget(reset_info)
        reset_layout.addWidget(reset_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Aggiungi il layout al tab
        advanced_layout.addLayout(reset_layout)
        
        # Add tabs
        self.tab_widget.addTab(settings_tab, "Settings")
        self.tab_widget.addTab(advanced_tab, "Advanced")
        layout.addWidget(self.tab_widget)
        
        # Inizializza UI in base alla modalità
        self.update_ui_based_on_mode()

    def update_buzzer_switch_style(self):
        """Aggiorna lo stile dello switch buzzer in base allo stato corrente"""
        if self.buzzer_state:
            # Stile per ON - Testo più leggibile
            self.buzzer_switch.setStyleSheet("""
                QPushButton {
                    background-color: #28a745;
                    border-radius: 15px;
                    text-align: right;
                    padding-right: 5px;
                    color: white;
                    font-size: 11pt;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #218838;
                }
            """)
            self.buzzer_switch.setText("ON ")
        else:
            # Stile per OFF - Testo più leggibile
            self.buzzer_switch.setStyleSheet("""
                QPushButton {
                    background-color: #ccc;
                    border-radius: 15px;
                    text-align: left;
                    padding-left: 5px;
                    color: #666;
                    font-size: 11pt;
                    font-weight: bold;
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
        if hasattr(self, 'mode_select'):
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
            f"<div style='text-align: center; font-weight: bold; font-size: 18px;'>Table {self.timer_data.get('table_number', 'N/A')}</div><br>"
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
            if not self.is_android_timer(self.device_id) and hasattr(self, 'mode_select'):
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
                self.accept()
            else:
                QMessageBox.warning(self, "Errore", "Impossibile salvare le impostazioni")
        except Exception as e:
            print(f"Errore nel salvataggio delle impostazioni: {e}")
            QMessageBox.critical(self, "Errore", f"Errore nel salvataggio: {str(e)}")