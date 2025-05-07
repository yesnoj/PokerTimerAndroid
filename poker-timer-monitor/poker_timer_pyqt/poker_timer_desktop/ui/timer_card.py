#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Widget per visualizzare un singolo timer
"""

import os
from PyQt6.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QMenu, QDialog, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSlot, QTimer
from PyQt6.QtGui import QFont, QAction, QIcon, QPixmap, QPainter, QColor

from .timer_details import TimerDetailsDialog

# Funzione sicura per mostrare messaggi che non causa crash
def safe_message_box(title, text, icon=QMessageBox.Icon.Question,
                    buttons=QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    default_button=QMessageBox.StandardButton.No):
    """Mostra una finestra di dialogo in modo sicuro senza riferimenti al parent"""
    msg_box = QMessageBox()
    msg_box.setWindowTitle(title)
    msg_box.setText(text)
    msg_box.setIcon(icon)
    msg_box.setStandardButtons(buttons)
    msg_box.setDefaultButton(default_button)
    return msg_box.exec()

class TimerCard(QFrame):
    """Widget che rappresenta un singolo timer nel pannello principale"""
    def __init__(self, device_id, timer_data, server, parent=None):
        super().__init__(parent)
        self.device_id = device_id
        self.timer_data = timer_data
        self.server = server
        
        # Imposta dimensioni fisse
        self.setFixedWidth(420)
        
        # Stile del frame - bordi arrotondati e colore bianco
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 10px;
            }
        """)
        
        # Il frame è cliccabile per aprire i dettagli
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.mousePressEvent = self.on_card_click
        
        # Layout principale
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)
        
        # ---- HEADER ----
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        # Titolo "Table X"
        title = QLabel(f"Table {timer_data.get('table_number', 'N/A')}")
        title.setStyleSheet("font-size: 18pt; font-weight: bold; color: #000000;")
        header_layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignLeft)
        
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
        
        header_layout.addWidget(device_icon)
        
        # Spazio flessibile
        header_layout.addStretch()
        
        # Etichetta stato
        is_running = timer_data.get('is_running', False)
        is_paused = timer_data.get('is_paused', False)
        
        status_text = "Paused" if is_paused else "Running" if is_running else "Stopped"
        status = QLabel(status_text)
        
        if status_text == "Running":
            status.setStyleSheet("background-color: #d4edda; color: #155724; padding: 6px 12px; border-radius: 5px; font-size: 16pt;")
        elif status_text == "Paused":
            status.setStyleSheet("background-color: #fff3cd; color: #856404; padding: 6px 12px; border-radius: 5px; font-size: 16pt;")
        else:
            status.setStyleSheet("background-color: #f8d7da; color: #721c24; padding: 6px 12px; border-radius: 5px; font-size: 16pt;")
        
        header_layout.addWidget(status)
        main_layout.addLayout(header_layout)
        
        # Linea separatrice
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("background-color: #eee;")
        separator.setMaximumHeight(1)
        main_layout.addWidget(separator)
        
        # NOTA: Rimosso completamente il blocco del timer con i secondi qui
        
        # ---- SEAT INFO (se presente) ----
        if 'seat_info' in timer_data and 'open_seats' in timer_data['seat_info'] and timer_data['seat_info']['open_seats']:
            seats = ', '.join(map(str, timer_data['seat_info']['open_seats']))
            
            self.seat_info = QLabel(f"SEAT OPEN: {seats}")
            self.seat_info.setStyleSheet("""
                background-color: #fde68a; 
                color: #854d0e; 
                padding: 8px; 
                border-radius: 5px; 
                font-weight: bold;
                font-size: 14pt;
            """)
            self.seat_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # Gestione separata del click per il reset dei posti
            self.seat_info.mousePressEvent = lambda e: self.on_seat_info_click(e)
            self.seat_info.setCursor(Qt.CursorShape.PointingHandCursor)
            main_layout.addWidget(self.seat_info)
        
        # ---- INFO PILLS ----
        # Prima riga: T1, [T2 e modalità solo per Arduino], Giocatori
        row1_layout = QHBoxLayout()
        row1_layout.setSpacing(8)

        # T1 (sempre visibile)
        t1_label = QLabel(f"T1: {timer_data.get('t1_value', 'N/A')}s")
        t1_label.setStyleSheet("background-color: #f8f9fa; padding: 8px; border-radius: 5px; font-size: 14pt;")
        row1_layout.addWidget(t1_label)

        # T2 e modalità - solo per timer hardware (Arduino)
        if self.is_hardware_timer(device_id):
            # T2 - mostralo solo se la modalità è 1 o 2 (modalità che usano T1/T2)
            mode = timer_data.get('mode', 1)
            if mode in [1, 2]:
                t2_label = QLabel(f"T2: {timer_data.get('t2_value', 'N/A')}s")
                t2_label.setStyleSheet("background-color: #f8f9fa; padding: 8px; border-radius: 5px; font-size: 14pt;")
                row1_layout.addWidget(t2_label)
                
            # Visualizza la modalità
            mode_text = ""
            if mode == 1:
                mode_text = "Mode: 1"
            elif mode == 2:
                mode_text = "Mode: 2"
            elif mode == 3:
                mode_text = "Mode: 3"
            elif mode == 4:
                mode_text = "Mode: 4"
            else:
                mode_text = f"Mode: {mode}"
                
            mode_label = QLabel(mode_text)
            mode_label.setStyleSheet("background-color: #f8f9fa; padding: 8px; border-radius: 5px; font-size: 14pt;")
            row1_layout.addWidget(mode_label)
        else:
            # Per i timer Android, non mostriamo né T2 né la modalità
            pass  # Non aggiungere nulla qui

        # Giocatori - Aggiunto testo più esplicito (sempre visibile per entrambi i tipi)
        players_label = QLabel(f"Giocatori: {timer_data.get('players_count', 6)}")
        players_label.setStyleSheet("background-color: #f8f9fa; padding: 8px; border-radius: 5px; font-size: 14pt;")
        row1_layout.addWidget(players_label)

        main_layout.addLayout(row1_layout)
        
        # Seconda riga: Buzzer, Battery
        row2_layout = QHBoxLayout()
        row2_layout.setSpacing(8)
        
        # Buzzer
        buzzer_label = QLabel(f"Buzzer: {'On' if timer_data.get('buzzer', False) else 'Off'}")
        buzzer_label.setStyleSheet("background-color: #f8f9fa; padding: 8px; border-radius: 5px; font-size: 14pt;")
        row2_layout.addWidget(buzzer_label)
        
        # Battery (in verde)
        battery_level = timer_data.get('battery_level', 100)
        battery_text = f"Battery: {battery_level}%"
        battery_label = QLabel(battery_text)
        battery_label.setStyleSheet("background-color: #f8f9fa; padding: 8px; border-radius: 5px; font-size: 14pt; color: #28a745;")
        row2_layout.addWidget(battery_label)
        
        main_layout.addLayout(row2_layout)
        
        # Terza riga: Voltage, WiFi
        row3_layout = QHBoxLayout()
        row3_layout.setSpacing(8)
        
        # Voltage
        voltage = timer_data.get('voltage', 5.00)
        voltage_text = f"Voltage: {voltage:.2f}V"
        voltage_label = QLabel(voltage_text)
        voltage_label.setStyleSheet("background-color: #f8f9fa; padding: 8px; border-radius: 5px; font-size: 14pt;")
        row3_layout.addWidget(voltage_label)
        
        # WiFi (con pallini verdi)
        wifi_label = QLabel(f"WiFi: <span style='color: #28a745;'>●●●●●</span> Ottimo")
        wifi_label.setStyleSheet("background-color: #f8f9fa; padding: 8px; border-radius: 5px; font-size: 14pt;")
        row3_layout.addWidget(wifi_label)
        
        main_layout.addLayout(row3_layout)
        
        # Quarta riga: IP
        row4_layout = QHBoxLayout()
                
        main_layout.addLayout(row4_layout)
        
        # ---- BUTTONS (solo Start e Pause) ----
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 10, 0, 10)
        button_layout.setSpacing(10)
        
        # Start button
        start_btn = QPushButton("Start")
        start_btn.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
                font-size: 14pt;
                font-weight: bold;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
            QPushButton:focus {
                outline: none;
            }
        """)
        start_btn.clicked.connect(self.on_start_click)
        start_btn.setEnabled(not (is_running and not is_paused))
        button_layout.addWidget(start_btn)
        
        # Pause button
        pause_btn = QPushButton("Pause")
        pause_btn.setStyleSheet("""
            QPushButton {
                background-color: #e2e6ea;
                color: #212529;
                border: none;
                border-radius: 5px;
                padding: 10px;
                font-size: 14pt;
                font-weight: bold;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
            QPushButton:focus {
                outline: none;
            }
        """)
        pause_btn.clicked.connect(self.on_pause_click)
        pause_btn.setEnabled(is_running and not is_paused)
        button_layout.addWidget(pause_btn)
        
        main_layout.addLayout(button_layout)
        
        # ---- STATUS BAR ----
        status_layout = QHBoxLayout()

        # Contenitore unico per Online e pallino
        is_online = timer_data.get('is_online', False)
        online_status_text = "● Online" if is_online else "● Offline"
        online_status_color = "#28a745" if is_online else "#dc3545"  # Verde se online, rosso se offline

        online_status = QLabel(online_status_text)
        online_status.setStyleSheet(f"color: {online_status_color}; font-size: 16pt; background-color: #f8f9fa; padding: 8px; border-radius: 5px;")
        status_layout.addWidget(online_status)

        # Spaziatore
        status_layout.addStretch()

        # Data ultimo aggiornamento
        try:
            from datetime import datetime
            last_update = timer_data.get('last_update', '')
            if last_update:
                last_update_dt = datetime.fromisoformat(last_update)
                formatted_time = last_update_dt.strftime("%H:%M:%S")
            else:
                formatted_time = "N/A"
        except:
            formatted_time = "N/A"

        last_update_label = QLabel(f"Last update: {formatted_time}")
        last_update_label.setStyleSheet("color: #6c757d; font-size: 16pt;")
        status_layout.addWidget(last_update_label)

        main_layout.addLayout(status_layout)
        
        # Menu contestuale
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
    
    def on_card_click(self, event):
        """Gestisce il click sulla card - apre i dettagli"""
        # Apre i dettagli del timer quando si clicca sulla card
        self.safe_open_details()
    
    def on_seat_info_click(self, event):
        """Gestisce il click sul label dei posti liberi"""
        # Ferma la propagazione dell'evento per evitare che apra i dettagli
        event.accept()
        # Mostra il dialogo di reset
        self.show_reset_dialog()
    
    def is_android_timer(self, device_id):
        """Determina se un timer è un'app Android basato sul device_id"""
        return device_id and device_id.startswith('android_')
    
    def is_hardware_timer(self, device_id):
        """Determina se un timer è hardware (ESP32/Arduino) basato sul device_id"""
        return device_id and device_id.startswith('arduino_')
    
    def on_start_click(self, checked=False):
        """Invia il comando di avvio al timer"""
        # Ferma la propagazione dell'evento per evitare che apra i dettagli
        event = QTimer.singleShot(0, lambda: self.server.send_command(self.device_id, "start"))
        return True
    
    def on_pause_click(self, checked=False):
        """Invia il comando di pausa al timer"""
        # Ferma la propagazione dell'evento per evitare che apra i dettagli
        event = QTimer.singleShot(0, lambda: self.server.send_command(self.device_id, "pause"))
        return True
    
    def safe_open_details(self):
        """Apre la finestra di dialogo dei dettagli in modo sicuro"""
        try:
            # Usa QTimer.singleShot per evitare problemi di callback
            QTimer.singleShot(0, lambda: self._open_details())
        except Exception as e:
            print(f"Errore nell'apertura dei dettagli: {e}")
    
    def _open_details(self):
        """Implementazione dell'apertura dei dettagli"""
        try:
            # Crea e mostra la finestra di dialogo
            dialog = TimerDetailsDialog(self.device_id, self.timer_data, self.server, None)  # Usa None come parent
            dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)  # Assicura che il widget venga distrutto
            dialog.exec()
        except Exception as e:
            print(f"Errore nell'apertura della finestra dettagli: {e}")
    
    def show_context_menu(self, pos):
        """Mostra il menu contestuale per il timer"""
        menu = QMenu(self)
        
        # Azioni
        start_action = QAction("Start", self)
        start_action.triggered.connect(self.on_start_click)
        start_action.setEnabled(not (self.timer_data.get('is_running', False) and not self.timer_data.get('is_paused', False)))
        menu.addAction(start_action)
        
        pause_action = QAction("Pause", self)
        pause_action.triggered.connect(self.on_pause_click)
        pause_action.setEnabled(self.timer_data.get('is_running', False) and not self.timer_data.get('is_paused', False))
        menu.addAction(pause_action)
        
        menu.addSeparator()
        
        details_action = QAction("Dettagli", self)
        details_action.triggered.connect(self.safe_open_details)
        menu.addAction(details_action)
        
        # Se ci sono posti liberi, aggiungi l'opzione per resetarli
        if 'seat_info' in self.timer_data and 'open_seats' in self.timer_data['seat_info'] and self.timer_data['seat_info']['open_seats']:
            menu.addSeparator()
            
            reset_seats_action = QAction("Reset posti liberi", self)
            reset_seats_action.triggered.connect(self.show_reset_dialog)
            menu.addAction(reset_seats_action)
        
        # Mostra il menu
        menu.exec(self.mapToGlobal(pos))
    
    def show_reset_dialog(self):
        """Mostra il dialogo di conferma per il reset dei posti liberi in modo sicuro"""
        try:
            seats = self.timer_data.get('seat_info', {}).get('open_seats', [])
            if not seats:
                return
                
            seats_str = ', '.join(map(str, seats))
            
            result = safe_message_box(
                'Conferma Reset',
                f'Vuoi rimuovere l\'indicazione di posti liberi ({seats_str}) per il tavolo {self.timer_data.get("table_number", "N/A")}?'
            )
            
            if result == QMessageBox.StandardButton.Yes:
                QTimer.singleShot(100, lambda: self.execute_seat_reset())
        except Exception as e:
            print(f"Errore nella visualizzazione del dialogo di reset: {e}")
    
    def execute_seat_reset(self):
        """Esegue il reset dei posti in modo sicuro"""
        try:
            print("Esecuzione reset posti...")
            self.server.reset_seat_info(self.device_id)
            print("Reset posti completato con successo")
        except Exception as e:
            print(f"Errore nell'esecuzione del reset posti: {e}")