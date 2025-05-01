#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Widget per visualizzare un singolo timer
"""

from PyQt6.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QMenu, QDialog, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSlot, QTimer
from PyQt6.QtGui import QFont, QAction, QIcon

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
            # Controlla se è disponibile l'icona da file, altrimenti usa emoji
            try:
                # Se hai i file delle icone, usa questo codice
                # icon = QIcon("path/to/android_icon.svg")
                # pixmap = icon.pixmap(24, 24)
                # device_icon.setPixmap(pixmap)
                # Fallback all'emoji se l'icona non è disponibile
                device_icon.setText("🤖")
                device_icon.setStyleSheet("color: #3DDC84; font-size: 22px;")
            except:
                device_icon.setText("🤖")
                device_icon.setStyleSheet("color: #3DDC84; font-size: 22px;")
            device_icon.setToolTip("Android App")
        elif self.is_hardware_timer(device_id):
            try:
                # Se hai i file delle icone, usa questo codice
                # icon = QIcon("path/to/arduino_icon.svg")
                # pixmap = icon.pixmap(24, 24)
                # device_icon.setPixmap(pixmap)
                # Fallback all'emoji se l'icona non è disponibile
                device_icon.setText("🔌")
                device_icon.setStyleSheet("color: #00979D; font-size: 22px;")
            except:
                device_icon.setText("🔌")
                device_icon.setStyleSheet("color: #00979D; font-size: 22px;")
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
        
        # ---- TIMER DISPLAY ----
        # Layout con due colonne per il timer
        timer_grid = QHBoxLayout()
        timer_grid.setContentsMargins(0, 15, 0, 15)
        
        # Valore del timer
        timer_value = timer_data.get('current_timer', '0')
        
        # Timer principale (numero)
        timer_container = QFrame()
        timer_container.setFrameShape(QFrame.Shape.Box)
        timer_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        timer_box_layout = QVBoxLayout(timer_container)
        timer_box_layout.setContentsMargins(10, 10, 10, 10)
        
        timer_number = QLabel(str(timer_value))
        timer_number.setStyleSheet("font-size: 40pt; font-weight: bold; color: #000000;")
        timer_number.setAlignment(Qt.AlignmentFlag.AlignCenter)
        timer_box_layout.addWidget(timer_number)
        
        # Aggiungiamo il container al layout
        timer_grid.addWidget(timer_container)
        
        # Container per "seconds"
        seconds_container = QFrame()
        seconds_container.setFrameShape(QFrame.Shape.Box)
        seconds_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        seconds_box_layout = QVBoxLayout(seconds_container)
        seconds_box_layout.setContentsMargins(10, 10, 10, 10)
        
        seconds_label = QLabel("seconds")
        seconds_label.setStyleSheet("font-size: 18pt; color: #000000;")
        seconds_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        seconds_box_layout.addWidget(seconds_label)
        
        # Aggiungiamo il container per "seconds" al layout
        timer_grid.addWidget(seconds_container)
        
        main_layout.addLayout(timer_grid)
        
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
        # Prima riga: T1, T2, Giocatori
        row1_layout = QHBoxLayout()
        row1_layout.setSpacing(8)
        
        # T1
        t1_label = QLabel(f"T1: {timer_data.get('t1_value', 'N/A')}s")
        t1_label.setStyleSheet("background-color: #f8f9fa; padding: 8px; border-radius: 5px; font-size: 14pt;")
        row1_layout.addWidget(t1_label)
        
        # T2
        t2_label = QLabel(f"T2: {timer_data.get('t2_value', 'N/A')}s")
        t2_label.setStyleSheet("background-color: #f8f9fa; padding: 8px; border-radius: 5px; font-size: 14pt;")
        row1_layout.addWidget(t2_label)
        
        # Giocatori - Aggiunto testo più esplicito
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
        
        # IP
        ip_text = f"IP: {timer_data.get('ip_address', '192.168.1.194')}"
        ip_label = QLabel(ip_text)
        ip_label.setStyleSheet("background-color: #f8f9fa; padding: 8px; border-radius: 5px; font-size: 14pt;")
        row4_layout.addWidget(ip_label)
        
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
        
        # Contenitore di sinistra per Online e pallino
        online_container = QHBoxLayout()
        
        # Pallino verde "Online"
        online_dot = QLabel("●")
        online_dot.setStyleSheet("color: #28a745; font-size: 16pt;")
        online_container.addWidget(online_dot)
        
        # Testo "Online"
        online_text = QLabel("Online")
        online_text.setStyleSheet("color: #28a745; font-size: 16pt;")
        online_container.addWidget(online_text)
        
        status_layout.addLayout(online_container)
        
        # Spaziatore
        status_layout.addStretch()
        
        # Data ultimo aggiornamento - Completa senza troncatura
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
        if 'seat_info' in self.timer_data and 'open_seats' in timer_data['seat_info'] and timer_data['seat_info']['open_seats']:
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