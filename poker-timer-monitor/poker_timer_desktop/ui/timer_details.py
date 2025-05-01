#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Finestra di dialogo per i dettagli di un timer
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                           QSpinBox, QComboBox, QCheckBox, QTabWidget, QWidget,
                           QGroupBox, QFormLayout, QMessageBox, QLineEdit)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

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
        
        # Evita che la finestra venga distrutta quando viene chiusa
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, False)
        
        # Imposta la modalità della finestra a Applicazione
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        
        try:
            # Layout principale
            layout = QVBoxLayout(self)
            layout.setContentsMargins(20, 20, 20, 20)
            layout.setSpacing(15)
            
            # Header
            header_layout = QHBoxLayout()
            
            # Titolo con icona Android (se appropriato)
            title = QLabel(f"Timer Details - Table {timer_data.get('table_number', 'N/A')}")
            title.setStyleSheet("color: #007bff; font-size: 24pt; font-weight: bold;")
            header_layout.addWidget(title)
            
            if self.is_android_timer(device_id):
                device_icon = QLabel("📱")
                device_icon.setStyleSheet("color: #a4c639; font-size: 24px;")
                device_icon.setToolTip("Android App")
                header_layout.addWidget(device_icon)
            
            layout.addLayout(header_layout)
            
            # Timer display
            timer_display = QLabel(f"{timer_data.get('current_timer', '0')} seconds")
            timer_display.setStyleSheet("font-size: 30pt; font-weight: bold; color: #000000; margin: 15px 0;")
            timer_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(timer_display)
            
            # Pulsanti di controllo
            control_layout = QHBoxLayout()
            
            # Start button
            self.start_btn = QPushButton("Start")
            self.start_btn.setStyleSheet("""
                QPushButton {
                    background-color: #007bff;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 10px 20px;
                    font-size: 16pt;
                    font-weight: bold;
                }
                QPushButton:disabled {
                    background-color: #cccccc;
                }
            """)
            self.start_btn.clicked.connect(self.on_start_click)
            self.start_btn.setEnabled(not (timer_data.get('is_running', False) and not timer_data.get('is_paused', False)))
            control_layout.addWidget(self.start_btn)
            
            # Pause button
            self.pause_btn = QPushButton("Pause")
            self.pause_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e2e6ea;
                    color: #212529;
                    border: none;
                    border-radius: 5px;
                    padding: 10px 20px;
                    font-size: 16pt;
                    font-weight: bold;
                }
                QPushButton:disabled {
                    background-color: #cccccc;
                    color: #666666;
                }
            """)
            self.pause_btn.clicked.connect(self.on_pause_click)
            self.pause_btn.setEnabled(timer_data.get('is_running', False) and not timer_data.get('is_paused', False))
            control_layout.addWidget(self.pause_btn)
            
            layout.addLayout(control_layout)
            
            # Info bar (in orizzontale)
            info_layout = QHBoxLayout()
            
            # T1
            t1_info = QLabel(f"T1: {timer_data.get('t1_value', 'N/A')}s")
            t1_info.setStyleSheet("font-size: 14pt; color: #000000; padding: 5px 10px;")
            info_layout.addWidget(t1_info)
            
            # T2
            t2_info = QLabel(f"T2: {timer_data.get('t2_value', 'N/A')}s")
            t2_info.setStyleSheet("font-size: 14pt; color: #000000; padding: 5px 10px;")
            info_layout.addWidget(t2_info)
            
            # Battery
            battery_info = QLabel(f"Battery: {timer_data.get('battery_level', 'N/A')}%")
            battery_info.setStyleSheet("font-size: 14pt; color: #28a745; padding: 5px 10px;")
            info_layout.addWidget(battery_info)
            
            # WiFi
            wifi_info = QLabel(f"WiFi: <span style='color: #28a745;'>●●●●●</span> Ottimo")
            wifi_info.setStyleSheet("font-size: 14pt; color: #000000; padding: 5px 10px;")
            info_layout.addWidget(wifi_info)
            
            # IP
            ip_info = QLabel(f"IP: {timer_data.get('ip_address', 'N/A')}")
            ip_info.setStyleSheet("font-size: 14pt; color: #000000; padding: 5px 10px;")
            info_layout.addWidget(ip_info)
            
            # Voltage
            voltage_info = QLabel(f"Voltage: {timer_data.get('voltage', 'N/A')}V")
            voltage_info.setStyleSheet("font-size: 14pt; color: #000000; padding: 5px 10px;")
            info_layout.addWidget(voltage_info)
            
            layout.addLayout(info_layout)
            
            # Seconda riga di info
            info_layout2 = QHBoxLayout()
            
            # Giocatori
            players_info = QLabel(f"Giocatori: {timer_data.get('players_count', 'N/A')}")
            players_info.setStyleSheet("font-size: 14pt; color: #000000; padding: 5px 10px;")
            info_layout2.addWidget(players_info)
            
            # Buzzer
            buzzer_info = QLabel(f"Buzzer: {'On' if timer_data.get('buzzer', False) else 'Off'}")
            buzzer_info.setStyleSheet("font-size: 14pt; color: #000000; padding: 5px 10px;")
            info_layout2.addWidget(buzzer_info)
            
            # Status
            status_info = QLabel(f"Status: {'Paused' if timer_data.get('is_paused', False) else 'Running' if timer_data.get('is_running', False) else 'Stopped'}")
            status_info.setStyleSheet("font-size: 14pt; color: #000000; padding: 5px 10px;")
            info_layout2.addWidget(status_info)
            
            layout.addLayout(info_layout2)
            
            # Tab Widget
            tab_widget = QTabWidget()
            tab_widget.setStyleSheet("""
                QTabWidget::pane {
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    padding: 10px;
                }
                QTabBar::tab {
                    padding: 8px 16px;
                    margin-right: 2px;
                    border: 1px solid #ddd;
                    border-bottom: none;
                    border-top-left-radius: 4px;
                    border-top-right-radius: 4px;
                    font-size: 14pt;
                }
                QTabBar::tab:selected {
                    background: white;
                    border-bottom-color: white;
                    font-weight: bold;
                    color: #007bff;
                }
            """)
            
            # Tab Impostazioni
            settings_tab = QWidget()
            settings_layout = QVBoxLayout(settings_tab)
            settings_layout.setContentsMargins(10, 20, 10, 10)
            
            # Titolo
            settings_title = QLabel("Timer Settings")
            settings_title.setStyleSheet("font-size: 20pt; font-weight: bold; color: #000000;")
            settings_layout.addWidget(settings_title)
            
            # Form layout per le impostazioni
            form_layout = QFormLayout()
            form_layout.setVerticalSpacing(15)
            form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
            
            # Styling comune dei label
            form_layout.setFormAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            
            # Styling comune
            input_style = """
                font-size: 14pt;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px;
                background: white;
            """
            
            # Numero tavolo
            table_layout = QHBoxLayout()
            self.table_number = QLineEdit()
            self.table_number.setText(str(timer_data.get('table_number', 0)))
            self.table_number.setStyleSheet(input_style)
            self.table_number.setFixedHeight(38)
            table_layout.addWidget(self.table_number)
            
            # Pulsanti +/-
            minus_btn = QPushButton("-")
            minus_btn.setStyleSheet("background-color: #28a745; color: white; font-weight: bold; padding: 4px 10px; border-radius: 4px; font-size: 14pt;")
            minus_btn.setFixedWidth(38)
            minus_btn.setFixedHeight(38)
            minus_btn.clicked.connect(lambda: self.decrement_value(self.table_number, 0, 99))
            
            plus_btn = QPushButton("+")
            plus_btn.setStyleSheet("background-color: #28a745; color: white; font-weight: bold; padding: 4px 10px; border-radius: 4px; font-size: 14pt;")
            plus_btn.setFixedWidth(38)
            plus_btn.setFixedHeight(38)
            plus_btn.clicked.connect(lambda: self.increment_value(self.table_number, 0, 99))
            
            table_layout.addWidget(minus_btn)
            table_layout.addWidget(plus_btn)
            
            # Label per il form
            table_label = QLabel("Numero Tavolo:")
            table_label.setStyleSheet("font-size: 14pt; font-weight: bold;")
            form_layout.addRow(table_label, table_layout)
            
            # Numero Giocatori
            players_layout = QHBoxLayout()
            self.players_count = QLineEdit()
            self.players_count.setText(str(timer_data.get('players_count', 6)))
            self.players_count.setStyleSheet(input_style)
            self.players_count.setFixedHeight(38)
            players_layout.addWidget(self.players_count)
            
            minus_btn2 = QPushButton("-")
            minus_btn2.setStyleSheet("background-color: #28a745; color: white; font-weight: bold; padding: 4px 10px; border-radius: 4px; font-size: 14pt;")
            minus_btn2.setFixedWidth(38)
            minus_btn2.setFixedHeight(38)
            minus_btn2.clicked.connect(lambda: self.decrement_value(self.players_count, 1, 10))
            
            plus_btn2 = QPushButton("+")
            plus_btn2.setStyleSheet("background-color: #28a745; color: white; font-weight: bold; padding: 4px 10px; border-radius: 4px; font-size: 14pt;")
            plus_btn2.setFixedWidth(38)
            plus_btn2.setFixedHeight(38)
            plus_btn2.clicked.connect(lambda: self.increment_value(self.players_count, 1, 10))
            
            players_layout.addWidget(minus_btn2)
            players_layout.addWidget(plus_btn2)
            
            # Label per il form
            players_label = QLabel("Numero Giocatori:")
            players_label.setStyleSheet("font-size: 14pt; font-weight: bold;")
            form_layout.addRow(players_label, players_layout)
            
            # Timer T1
            t1_layout = QHBoxLayout()
            self.t1_value = QLineEdit()
            self.t1_value.setText(str(timer_data.get('t1_value', 25)))
            self.t1_value.setStyleSheet(input_style)
            self.t1_value.setFixedHeight(38)
            t1_layout.addWidget(self.t1_value)
            
            minus_btn3 = QPushButton("-")
            minus_btn3.setStyleSheet("background-color: #28a745; color: white; font-weight: bold; padding: 4px 10px; border-radius: 4px; font-size: 14pt;")
            minus_btn3.setFixedWidth(38)
            minus_btn3.setFixedHeight(38)
            minus_btn3.clicked.connect(lambda: self.decrement_value(self.t1_value, 5, 95, 5))
            
            plus_btn3 = QPushButton("+")
            plus_btn3.setStyleSheet("background-color: #28a745; color: white; font-weight: bold; padding: 4px 10px; border-radius: 4px; font-size: 14pt;")
            plus_btn3.setFixedWidth(38)
            plus_btn3.setFixedHeight(38)
            plus_btn3.clicked.connect(lambda: self.increment_value(self.t1_value, 5, 95, 5))
            
            t1_layout.addWidget(minus_btn3)
            t1_layout.addWidget(plus_btn3)
            
            # Label per il form
            t1_label = QLabel("Timer T1:")
            t1_label.setStyleSheet("font-size: 14pt; font-weight: bold;")
            form_layout.addRow(t1_label, t1_layout)
            
            # Timer T2
            t2_layout = QHBoxLayout()
            self.t2_value = QLineEdit()
            self.t2_value.setText(str(timer_data.get('t2_value', 20)))
            self.t2_value.setStyleSheet(input_style)
            self.t2_value.setFixedHeight(38)
            t2_layout.addWidget(self.t2_value)
            
            minus_btn4 = QPushButton("-")
            minus_btn4.setStyleSheet("background-color: #28a745; color: white; font-weight: bold; padding: 4px 10px; border-radius: 4px; font-size: 14pt;")
            minus_btn4.setFixedWidth(38)
            minus_btn4.setFixedHeight(38)
            minus_btn4.clicked.connect(lambda: self.decrement_value(self.t2_value, 5, 95, 5))
            
            plus_btn4 = QPushButton("+")
            plus_btn4.setStyleSheet("background-color: #28a745; color: white; font-weight: bold; padding: 4px 10px; border-radius: 4px; font-size: 14pt;")
            plus_btn4.setFixedWidth(38)
            plus_btn4.setFixedHeight(38)
            plus_btn4.clicked.connect(lambda: self.increment_value(self.t2_value, 5, 95, 5))
            
            t2_layout.addWidget(minus_btn4)
            t2_layout.addWidget(plus_btn4)
            
            # Label per il form
            t2_label = QLabel("Timer T2:")
            t2_label.setStyleSheet("font-size: 14pt; font-weight: bold;")
            form_layout.addRow(t2_label, t2_layout)
            
            # Buzzer
            buzzer_layout = QHBoxLayout()
            self.buzzer = QCheckBox()
            self.buzzer.setChecked(timer_data.get('buzzer', False))
            self.buzzer.setStyleSheet("""
                QCheckBox {
                    spacing: 5px;
                    font-size: 14pt;
                }
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
            buzzer_layout.addWidget(self.buzzer)
            
            # Label per il form
            buzzer_label = QLabel("Buzzer:")
            buzzer_label.setStyleSheet("font-size: 14pt; font-weight: bold;")
            form_layout.addRow(buzzer_label, buzzer_layout)
            
            settings_layout.addLayout(form_layout)
            
            # Pulsante salva impostazioni
            save_btn = QPushButton("Save Settings")
            save_btn.setStyleSheet("""
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px;
                margin-top: 20px;
                font-size: 16pt;
                font-weight: bold;
            """)
            save_btn.clicked.connect(self.safe_save_settings)
            settings_layout.addWidget(save_btn)
            
            # Close button
            close_btn = QPushButton("Chiudi")
            close_btn.setStyleSheet("""
                background-color: #6c757d;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px;
                margin-top: 10px;
                font-size: 16pt;
            """)
            close_btn.clicked.connect(self.accept)
            settings_layout.addWidget(close_btn)
            
            # Tab Avanzate
            advanced_tab = QWidget()
            advanced_layout = QVBoxLayout(advanced_tab)
            
            tab_widget.addTab(settings_tab, "Settings")
            tab_widget.addTab(advanced_tab, "Advanced")
            
            layout.addWidget(tab_widget)
            
        except Exception as e:
            print(f"Errore nell'inizializzazione della finestra dettagli: {e}")
    
    def is_android_timer(self, device_id):
        """Determina se un timer è un'app Android basato sul device_id"""
        return device_id and device_id.startswith('android_')
    
    def on_start_click(self):
        """Invia il comando di avvio al timer"""
        try:
            QTimer.singleShot(0, lambda: self.server.send_command(self.device_id, "start"))
            self.start_btn.setEnabled(False)
            self.pause_btn.setEnabled(True)
        except Exception as e:
            print(f"Errore nell'invio del comando start: {e}")
    
    def on_pause_click(self):
        """Invia il comando di pausa al timer"""
        try:
            QTimer.singleShot(0, lambda: self.server.send_command(self.device_id, "pause"))
            self.start_btn.setEnabled(True)
            self.pause_btn.setEnabled(False)
        except Exception as e:
            print(f"Errore nell'invio del comando pause: {e}")
    
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
    
    def safe_save_settings(self):
        """Salva le impostazioni del timer in modo sicuro"""
        try:
            QTimer.singleShot(0, self.save_settings)
        except Exception as e:
            print(f"Errore nel salvataggio: {e}")
    
    def save_settings(self):
        """Salva le impostazioni del timer"""
        try:
            # Raccogli i dati
            try:
                table_num = int(self.table_number.text())
                players = int(self.players_count.text())
                t1 = int(self.t1_value.text())
                t2 = int(self.t2_value.text())
            except ValueError:
                self.show_message("Errore", "I valori devono essere numeri interi", QMessageBox.Icon.Warning)
                return
            
            settings = {
                'mode': 1,  # Modalità predefinita
                't1': t1,
                't2': t2,
                'tableNumber': table_num,
                'buzzer': 1 if self.buzzer.isChecked() else 0,
                'playersCount': players
            }
            
            # Invia le impostazioni al server
            success = self.server.update_settings(self.device_id, settings)
            
            # Mostra il messaggio in modo sicuro
            if success:
                self.show_message("Successo", "Impostazioni salvate con successo")
            else:
                self.show_message("Errore", "Impossibile salvare le impostazioni", QMessageBox.Icon.Warning)
        except Exception as e:
            print(f"Errore nel salvataggio delle impostazioni: {e}")
            self.show_message("Errore", f"Errore nel salvataggio: {str(e)}", QMessageBox.Icon.Critical)
    
    def show_message(self, title, text, icon=QMessageBox.Icon.Information):
        """Mostra un messaggio in modo sicuro"""
        try:
            msg = QMessageBox()
            msg.setWindowTitle(title)
            msg.setText(text)
            msg.setIcon(icon)
            QTimer.singleShot(0, lambda: msg.exec())
        except Exception as e:
            print(f"Errore nella visualizzazione del messaggio: {e}")