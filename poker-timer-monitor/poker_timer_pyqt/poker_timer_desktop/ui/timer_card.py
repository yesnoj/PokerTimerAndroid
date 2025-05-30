#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Widget per visualizzare un singolo timer con icona floorman
"""

import os
import time
from PyQt6.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QMenu, QDialog, QMessageBox, QGridLayout)
from PyQt6.QtCore import Qt, pyqtSlot, QTimer, pyqtSignal
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
    """Widget che rappresenta un singolo timer nel pannello principale (versione compatta)"""
    
    # Segnale emesso quando la chiamata floorman viene gestita
    floorman_handled = pyqtSignal(str)  # device_id
    
    def __init__(self, device_id, timer_data, server, parent=None):
        super().__init__(parent)
        self.device_id = device_id
        self.timer_data = timer_data
        self.server = server
        
        # Inizializza il timestamp dell'ultimo click
        self._last_click_time = 0
        
        # Flag per tracciare se c'è una chiamata floorman attiva
        self.has_active_floorman_call = False
        
        # Imposta dimensioni fisse
        self.setFixedWidth(420)
        
        # IMPORTANTE: Imposta il nome dell'oggetto per lo stile
        self.setObjectName("TimerCard")
        
        # Stile del frame - bordi arrotondati e colore bianco
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setStyleSheet("""
            TimerCard {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 10px;
            }
        """)
        
        # Il frame è cliccabile per aprire i dettagli
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Layout principale - ridotti margini per compattare
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(5)  # Ridotto lo spazio tra elementi
        
        # ---- HEADER COMPATTO ----
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(5)
        
        # Titolo "Table X" con font ridotto - fissato per avere altezza uniforme
        title = QLabel(f"Table {timer_data.get('table_number', 'N/A')}")
        title.setObjectName("title_label")
        title.setStyleSheet("font-size: 14pt; font-weight: bold; color: #000000; background-color: #f8f9fa; padding: 4px 8px; border-radius: 4px;")
        title.setFixedHeight(30)  # Altezza fissa
        header_layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignLeft)
        
        # Icona dispositivo (Android o Arduino) - integrata nel proprio contenitore
        device_icon = QLabel()
        device_icon.setObjectName("device_icon")
        device_icon.setFixedHeight(30)  # Altezza fissa
        device_icon.setStyleSheet("background-color: #f8f9fa; padding: 4px 8px; border-radius: 4px;")
        
        if self.is_android_timer(device_id):
            # Usa l'icona SVG di Android
            icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                    'resources', 'icons', 'ic_android.svg')
            if os.path.exists(icon_path):
                # Carica l'icona come QIcon
                icon = QIcon(icon_path)
                # Crea un QPixmap dalle dimensioni desiderate
                pixmap = icon.pixmap(20, 20)  # Dimensione ridotta
                # Imposta il pixmap sulla QLabel
                device_icon.setPixmap(pixmap)
                device_icon.setToolTip("Android App")
            else:
                # Emoji visibile come fallback
                device_icon.setText("🤖")
                device_icon.setStyleSheet("color: #000000; font-size: 18px; background-color: #f8f9fa; padding: 4px 8px; border-radius: 4px;")
                device_icon.setToolTip("Android App")
        elif self.is_hardware_timer(device_id):
            # Usa l'icona SVG di Hardware
            icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                    'resources', 'icons', 'ic_hardware.svg')
            if os.path.exists(icon_path):
                # Carica l'icona come QIcon
                icon = QIcon(icon_path)
                # Crea un QPixmap dalle dimensioni desiderate
                pixmap = icon.pixmap(20, 20)  # Dimensione ridotta
                # Imposta il pixmap sulla QLabel
                device_icon.setPixmap(pixmap)
                device_icon.setToolTip("Hardware Timer")
            else:
                # Emoji visibile come fallback
                device_icon.setText("🔌")
                device_icon.setStyleSheet("color: #000000; font-size: 18px; background-color: #f8f9fa; padding: 4px 8px; border-radius: 4px;")
                device_icon.setToolTip("Hardware Timer")
        
        header_layout.addWidget(device_icon)
        
        # Spazio flessibile per allineare il titolo a sinistra
        header_layout.addStretch()
        
        # Icona floorman (inizialmente nascosta)
        self.floorman_icon = QLabel()
        self.floorman_icon.setObjectName("floorman_icon")
        self.floorman_icon.setFixedSize(30, 30)
        self.floorman_icon.setStyleSheet("""
            QLabel#floorman_icon {
                background-color: #FF9800;
                border-radius: 15px;
                font-size: 18px;
                color: white;
                font-weight: bold;
            }
        """)
        self.floorman_icon.setText("!")
        self.floorman_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.floorman_icon.setCursor(Qt.CursorShape.PointingHandCursor)
        self.floorman_icon.setToolTip("Chiamata Floorman Attiva - Clicca per gestire")
        self.floorman_icon.setVisible(False)
        
        header_layout.addWidget(self.floorman_icon)
        
        main_layout.addLayout(header_layout)
        
        # ---- SEAT INFO (se presente) ----
        self.seat_info_container = QVBoxLayout()
        self.seat_info_container.setSpacing(2)  # Ridotto spazio
        main_layout.addLayout(self.seat_info_container)
        
        if 'seat_info' in timer_data and 'open_seats' in timer_data['seat_info'] and timer_data['seat_info']['open_seats']:
            seats = ', '.join(map(str, timer_data['seat_info']['open_seats']))
            
            self.seat_info = QLabel(f"SEAT OPEN: {seats}")
            self.seat_info.setObjectName("seat_info_label")
            self.seat_info.setStyleSheet("""
                background-color: #fde68a; 
                color: #854d0e; 
                padding: 4px; 
                border-radius: 4px; 
                font-weight: bold;
                font-size: 12pt;
            """)
            self.seat_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # Gestione separata del click per il reset dei posti
            self.seat_info.mousePressEvent = lambda e: self.on_seat_info_click(e)
            self.seat_info.setCursor(Qt.CursorShape.PointingHandCursor)
            self.seat_info_container.addWidget(self.seat_info)
        
        # ---- INFO GRID - Layout a griglia per informazioni ----
        info_grid = QGridLayout()
        info_grid.setSpacing(5)  # Ridotto spazio tra celle

        # Stile comune per le info - RIMOSSO border: none che causava il problema
        info_style = """
            background-color: #f8f9fa; 
            padding: 4px 6px; 
            border-radius: 4px; 
            font-size: 11pt;
        """

        # Prima riga della griglia (0)
        col = 0

        # T1 (sempre visibile)
        self.t1_label = QLabel(f"T1: {timer_data.get('t1_value', 'N/A')}s")
        self.t1_label.setObjectName("t1_label")
        self.t1_label.setStyleSheet(info_style)
        info_grid.addWidget(self.t1_label, 0, col)
        col += 1

        # Stato Timer (sostituisce Giocatori)
        is_running = timer_data.get('is_running', False)
        is_paused = timer_data.get('is_paused', False)
        status_text = "Paused" if is_paused else "Running" if is_running else "Stopped"
        self.timer_status_label = QLabel(status_text)
        self.timer_status_label.setObjectName("timer_status_label")

        # Utilizza lo stesso stile del badge rimosso
        if status_text == "Running":
            self.timer_status_label.setStyleSheet("background-color: #d4edda; color: #155724; padding: 4px 8px; border-radius: 4px; font-size: 13pt;")
        elif status_text == "Paused":
            self.timer_status_label.setStyleSheet("background-color: #fff3cd; color: #856404; padding: 4px 8px; border-radius: 4px; font-size: 13pt;")
        else:  # Stopped
            self.timer_status_label.setStyleSheet("background-color: #f8d7da; color: #721c24; padding: 4px 8px; border-radius: 4px; font-size: 13pt;")
        info_grid.addWidget(self.timer_status_label, 0, col)
        col += 1

        # Buzzer
        self.buzzer_label = QLabel(f"Buzzer: {'On' if timer_data.get('buzzer', False) else 'Off'}")
        self.buzzer_label.setObjectName("buzzer_label")
        self.buzzer_label.setStyleSheet(info_style)
        info_grid.addWidget(self.buzzer_label, 0, col)
        
        # Seconda riga della griglia (1)
        col = 0
        
        # Battery con colore verde
        battery_level = timer_data.get('battery_level', 100)
        battery_text = f"Battery: {battery_level}%"
        self.battery_label = QLabel(battery_text)
        self.battery_label.setObjectName("battery_label")
        self.battery_label.setStyleSheet(f"{info_style} color: #28a745;")
        info_grid.addWidget(self.battery_label, 1, 0)
        
        # Voltage e WiFi sulla stessa riga
        voltage = timer_data.get('voltage', 5.00)
        voltage_text = f"Voltage: {voltage:.2f}V"
        self.voltage_label = QLabel(voltage_text)
        self.voltage_label.setObjectName("voltage_label")
        self.voltage_label.setStyleSheet(info_style)
        info_grid.addWidget(self.voltage_label, 1, 1)
        
        # WiFi accanto a Voltage - valore dinamico in base alla qualità
        wifi_quality = timer_data.get('wifi_quality', 100)
        wifi_dots = self.format_wifi_indicator(wifi_quality)
        self.wifi_label = QLabel(f"WiFi: <span style='color: #28a745;'>{wifi_dots}")
        self.wifi_label.setObjectName("wifi_label")
        self.wifi_label.setStyleSheet(info_style)
        info_grid.addWidget(self.wifi_label, 1, 2)
        
        # T2 e modalità - solo per timer hardware (Arduino), posizionati in altre celle
        if self.is_hardware_timer(device_id):
            # T2 - mostralo solo se la modalità è 1 o 2 (modalità che usano T1/T2)
            mode = timer_data.get('mode', 1)
            if mode in [1, 2]:
                self.t2_label = QLabel(f"T2: {timer_data.get('t2_value', 'N/A')}s")
                self.t2_label.setObjectName("t2_label")
                self.t2_label.setStyleSheet(info_style)
                # Posiziona in una cella specifica
                info_grid.addWidget(self.t2_label, 2, 0)
        
        main_layout.addLayout(info_grid)
        
        # ---- BARRA DI STATO - Compattata con info essenziali ----
        status_layout = QHBoxLayout()
        status_layout.setSpacing(5)  # Ridotto spazio

        # Indicatore Online/Offline - con altezza fissa
        is_online = timer_data.get('is_online', False)
        online_status_text = "● Online" if is_online else "● Offline"
        online_status_color = "#28a745" if is_online else "#dc3545"  # Verde o rosso

        online_status = QLabel(online_status_text)
        online_status.setObjectName("online_status")
        online_status.setFixedHeight(30)  # Altezza fissa uguale agli altri componenti
        online_status.setStyleSheet(f"color: {online_status_color}; font-size: 12pt; background-color: #f8f9fa; padding: 4px 6px; border-radius: 4px;")
        status_layout.addWidget(online_status)

        # Spaziatore
        status_layout.addStretch()

        # Ultimo aggiornamento - con altezza fissa
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

        self.last_update_label = QLabel(f"Last update: {formatted_time}")
        self.last_update_label.setObjectName("last_update_label")
        self.last_update_label.setFixedHeight(30)  # Altezza fissa
        self.last_update_label.setStyleSheet("color: #6c757d; font-size: 11pt; background-color: #f8f9fa; padding: 4px 6px; border-radius: 4px;")
        status_layout.addWidget(self.last_update_label)

        main_layout.addLayout(status_layout)
        
        # Menu contestuale
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def mousePressEvent(self, event):
        """Override del mousePressEvent per gestire i click sulla card"""
        # Verifica se il click è sull'icona floorman
        if self.floorman_icon.isVisible():
            # Ottieni la posizione globale dell'icona floorman
            icon_rect = self.floorman_icon.geometry()
            # Converti la posizione del click in coordinate relative al widget
            click_pos = event.pos()
            
            # Verifica se il click è nell'area dell'icona
            if icon_rect.contains(click_pos):
                # Il click è sull'icona floorman, gestiscilo
                self.on_floorman_icon_click(event)
                event.accept()
                return
        
        # Altrimenti, gestisci il click normale sulla card
        self.on_card_click(event)

    def set_floorman_active(self, active=True):
        """Imposta lo stato della chiamata floorman"""
        self.has_active_floorman_call = active
        self.floorman_icon.setVisible(active)
        
        if active:
            # Fai lampeggiare l'icona e aggiungi il bordo arancione
            self.start_floorman_animation()
            # Aggiungi un bordo arancione SOLO al frame principale
            self.setStyleSheet("""
                QFrame#TimerCard {
                    background-color: white;
                    border: 3px solid #FF9800;
                    border-radius: 10px;
                }
            """)
        else:
            # Ferma l'animazione e rimuovi il bordo
            self.stop_floorman_animation()
            # Ripristina lo stile originale
            self.setStyleSheet("""
                QFrame#TimerCard {
                    background-color: white;
                    border: 1px solid #ddd;
                    border-radius: 10px;
                }
            """)
            
            # Assicurati che l'icona sia nascosta
            self.floorman_icon.setVisible(False)
            self.has_active_floorman_call = False
    
    def start_floorman_animation(self):
        """Avvia l'animazione lampeggiante dell'icona floorman"""
        if not hasattr(self, 'floorman_timer'):
            self.floorman_timer = QTimer(self)
            self.floorman_timer.timeout.connect(self.toggle_floorman_icon)
        
        self.floorman_visible = True
        self.floorman_timer.start(500)  # Lampeggia ogni 500ms
    
    def stop_floorman_animation(self):
        """Ferma l'animazione dell'icona floorman"""
        if hasattr(self, 'floorman_timer') and self.floorman_timer.isActive():
            self.floorman_timer.stop()
        self.floorman_icon.setVisible(False)
    
    def toggle_floorman_icon(self):
        """Alterna la visibilità dell'icona per l'effetto lampeggiante"""
        if self.has_active_floorman_call:
            self.floorman_visible = not self.floorman_visible
            self.floorman_icon.setVisible(self.floorman_visible)
    
    def on_floorman_icon_click(self, event):
        """Gestisce il click sull'icona floorman"""
        event.accept()  # Ferma la propagazione
        
        # Importa il dialog dalla finestra principale
        from .main_window import FloormanCallDialog
        
        # Mostra il dialog personalizzato
        dialog = FloormanCallDialog(self.timer_data.get('table_number', 'N/A'), None)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # L'utente ha cliccato "Gestita"
            # Invia il comando al server per cancellare la chiamata floorman
            self.server.send_command(self.device_id, "clear_floorman")
            
            # Rimuovi il timestamp floorman dai dati locali
            if 'floorman_call_timestamp' in self.timer_data:
                del self.timer_data['floorman_call_timestamp']
            
            # Rimuovi l'icona e ferma l'animazione immediatamente
            self.set_floorman_active(False)
            
            # Emetti il segnale per notificare che è stata gestita
            self.floorman_handled.emit(self.device_id)
            
            # Forza un aggiornamento della card dal server
            QTimer.singleShot(500, lambda: self.server.timer_updated.emit(self.device_id))

    def format_wifi_indicator(self, wifi_quality):
        """Formatta l'indicatore WiFi in base alla qualità del segnale"""
        if wifi_quality >= 80:
            return "●●●●●"
        elif wifi_quality >= 60:
            return "●●●●○"
        elif wifi_quality >= 40:
            return "●●●○○"
        elif wifi_quality >= 20:
            return "●●○○○"
        elif wifi_quality > 0:
            return "●○○○○"
        else:
            return "○○○○○"
            
    def update_data(self, new_timer_data):
        """Aggiorna i dati della card senza ricrearla"""
        # Rimuovi il controllo che potrebbe bloccare gli aggiornamenti
        # if self.timer_data == new_timer_data:
        #     return
        
        # Aggiorna i dati interni
        old_timer_data = self.timer_data.copy() if self.timer_data else {}
        self.timer_data = new_timer_data
        
        # IMPORTANTE: Gestione dello stato floorman
        # Controlla se c'è un timestamp floorman nei nuovi dati
        has_floorman_call = 'floorman_call_timestamp' in new_timer_data and new_timer_data['floorman_call_timestamp'] is not None
        
        # Aggiorna lo stato dell'icona floorman solo se è cambiato
        if has_floorman_call != self.has_active_floorman_call:
            self.set_floorman_active(has_floorman_call)
        
        # Aggiorna il titolo
        title_label = self.findChild(QLabel, "title_label")
        if title_label:
            new_title = f"Table {new_timer_data.get('table_number', 'N/A')}"
            if title_label.text() != new_title:
                title_label.setText(new_title)
        
        # Aggiorna i posti liberi (se presenti o cambiati)
        if ('seat_info' in new_timer_data and 'open_seats' in new_timer_data['seat_info'] and 
            new_timer_data['seat_info']['open_seats']):
            
            seats = ', '.join(map(str, new_timer_data['seat_info']['open_seats']))
            seat_text = f"SEAT OPEN: {seats}"
            seat_info_label = self.findChild(QLabel, "seat_info_label")
            
            if seat_info_label:
                # Aggiorna l'etichetta esistente solo se il testo è cambiato
                if seat_info_label.text() != seat_text:
                    seat_info_label.setText(seat_text)
            else:
                # Crea una nuova etichetta
                self.seat_info = QLabel(seat_text)
                self.seat_info.setObjectName("seat_info_label")
                self.seat_info.setStyleSheet("""
                    background-color: #fde68a; 
                    color: #854d0e; 
                    padding: 4px; 
                    border-radius: 4px; 
                    font-weight: bold;
                    font-size: 12pt;
                """)
                self.seat_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.seat_info.mousePressEvent = lambda e: self.on_seat_info_click(e)
                self.seat_info.setCursor(Qt.CursorShape.PointingHandCursor)
                
                # Pulisci il layout prima di aggiungere la nuova etichetta
                for i in reversed(range(self.seat_info_container.count())): 
                    self.seat_info_container.itemAt(i).widget().setParent(None)
                
                self.seat_info_container.addWidget(self.seat_info)
        else:
            # Rimuovi l'etichetta dei posti se non ci sono posti
            seat_info_label = self.findChild(QLabel, "seat_info_label")
            if seat_info_label:
                seat_info_label.setParent(None)
        
        # Aggiorna i valori dei timer
        t1_label = self.findChild(QLabel, "t1_label")
        if t1_label:
            new_t1_text = f"T1: {new_timer_data.get('t1_value', 'N/A')}s"
            if t1_label.text() != new_t1_text:
                t1_label.setText(new_t1_text)
        
        if self.is_hardware_timer(self.device_id):
            t2_label = self.findChild(QLabel, "t2_label")
            mode = new_timer_data.get('mode', 1)
            
            if t2_label and mode in [1, 2]:
                new_t2_text = f"T2: {new_timer_data.get('t2_value', 'N/A')}s"
                if t2_label.text() != new_t2_text:
                    t2_label.setText(new_t2_text)
                t2_label.setVisible(True)
            elif t2_label:
                t2_label.setVisible(False)
        
        # IMPORTANTE: Aggiorna stato timer - questo è il punto critico
        timer_status_label = self.findChild(QLabel, "timer_status_label")
        if timer_status_label:
            is_running = new_timer_data.get('is_running', False)
            is_paused = new_timer_data.get('is_paused', False)
            
            # Determina il nuovo stato
            if is_paused:
                status_text = "Paused"
            elif is_running:
                status_text = "Running"
            else:
                status_text = "Stopped"
            
            # Aggiorna solo se il testo è cambiato
            if timer_status_label.text() != status_text:
                timer_status_label.setText(status_text)
                
                # Aggiorna anche lo stile
                if status_text == "Running":
                    timer_status_label.setStyleSheet("background-color: #d4edda; color: #155724; padding: 4px 8px; border-radius: 4px; font-size: 13pt;")
                elif status_text == "Paused":
                    timer_status_label.setStyleSheet("background-color: #fff3cd; color: #856404; padding: 4px 8px; border-radius: 4px; font-size: 13pt;")
                else:  # Stopped
                    timer_status_label.setStyleSheet("background-color: #f8d7da; color: #721c24; padding: 4px 8px; border-radius: 4px; font-size: 13pt;")
                
                print(f"Timer {self.device_id} stato aggiornato a: {status_text}")
        
        # Aggiorna buzzer
        buzzer_label = self.findChild(QLabel, "buzzer_label")
        if buzzer_label:
            buzzer_text = f"Buzzer: {'On' if new_timer_data.get('buzzer', False) else 'Off'}"
            if buzzer_label.text() != buzzer_text:
                buzzer_label.setText(buzzer_text)
        
        # Aggiorna batteria
        battery_label = self.findChild(QLabel, "battery_label")
        if battery_label:
            battery_level = new_timer_data.get('battery_level', 100)
            battery_text = f"Battery: {battery_level}%"
            if battery_label.text() != battery_text:
                battery_label.setText(battery_text)
        
        # Aggiorna voltage
        voltage_label = self.findChild(QLabel, "voltage_label")
        if voltage_label:
            voltage = new_timer_data.get('voltage', 5.00)
            voltage_text = f"Voltage: {voltage:.2f}V"
            if voltage_label.text() != voltage_text:
                voltage_label.setText(voltage_text)
        
        # Aggiorna WiFi
        wifi_label = self.findChild(QLabel, "wifi_label")
        if wifi_label:
            wifi_quality = new_timer_data.get('wifi_quality', 100)
            wifi_dots = self.format_wifi_indicator(wifi_quality)
            wifi_text = f"WiFi: <span style='color: #28a745;'>{wifi_dots}</span>"
            if wifi_label.text() != wifi_text:
                wifi_label.setText(wifi_text)
        
        # Aggiorna stato online/offline
        online_status = self.findChild(QLabel, "online_status")
        if online_status:
            is_online = new_timer_data.get('is_online', False)
            online_status_text = "● Online" if is_online else "● Offline"
            if online_status.text() != online_status_text:
                online_status.setText(online_status_text)
                online_status_color = "#28a745" if is_online else "#dc3545"
                online_status.setStyleSheet(f"color: {online_status_color}; font-size: 12pt; background-color: #f8f9fa; padding: 4px 6px; border-radius: 4px;")
        
        # Aggiorna l'orario dell'ultimo aggiornamento
        last_update_label = self.findChild(QLabel, "last_update_label")
        if last_update_label:
            try:
                from datetime import datetime
                last_update = new_timer_data.get('last_update', '')
                if last_update:
                    last_update_dt = datetime.fromisoformat(last_update)
                    formatted_time = last_update_dt.strftime("%H:%M:%S")
                else:
                    formatted_time = "N/A"
            except:
                formatted_time = "N/A"
            
            new_update_text = f"Last update: {formatted_time}"
            if last_update_label.text() != new_update_text:
                last_update_label.setText(new_update_text)

        
    def on_card_click(self, event):
        """Gestisce il click sulla card - apre i dettagli"""
        # Verifica se il click è intenzionale (non durante lo sfarfallio)
        current_time = time.time()
        if current_time - self._last_click_time < 0.5:  # Ignora click troppo ravvicinati
            event.accept()
            return
        
        self._last_click_time = current_time
        
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
    
    def send_start_command(self):
        """Invia il comando di avvio al timer"""
        self.server.send_command(self.device_id, "start")
    
    def send_pause_command(self):
        """Invia il comando di pausa al timer"""
        self.server.send_command(self.device_id, "pause")
    
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
        start_action.triggered.connect(self.send_start_command)
        menu.addAction(start_action)
        
        pause_action = QAction("Pause", self)
        pause_action.triggered.connect(self.send_pause_command)
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