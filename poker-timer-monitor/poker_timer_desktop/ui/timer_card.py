#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Widget per visualizzare un singolo timer
"""

from PyQt6.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QMenu, QDialog, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QFont, QIcon, QAction

from .timer_details import TimerDetailsDialog

class TimerCard(QFrame):
    """Widget che rappresenta un singolo timer nel pannello principale"""
    def __init__(self, device_id, timer_data, server, parent=None):
        super().__init__(parent)
        self.device_id = device_id
        self.timer_data = timer_data
        self.server = server
        
        # Stile del frame
        self.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        self.setLineWidth(2)
        self.setMidLineWidth(0)
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px solid #9e9e9e;
                border-radius: 8px;
                padding: 15px;
                margin: 8px;
            }
            QFrame:hover {
                background-color: #f5f5f5;
                border: 2px solid #0077cc;
            }
        """)
        
        # Layout principale
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # Header con titolo e stato
        header_layout = QHBoxLayout()
        
        # Titolo
        title = QLabel(f"Tavolo {timer_data.get('table_number', 'N/A')}")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header_layout.addWidget(title)
        
        # Stato
        is_running = timer_data.get('is_running', False)
        is_paused = timer_data.get('is_paused', False)
        
        status_text = "Paused" if is_paused else "Running" if is_running else "Stopped"
        status = QLabel(status_text)
        
        if status_text == "Running":
            status.setStyleSheet("background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; padding: 6px 10px; border-radius: 4px; font-weight: bold; font-size: 12pt;")
        elif status_text == "Paused":
            status.setStyleSheet("background-color: #fff3cd; color: #856404; border: 1px solid #ffeeba; padding: 6px 10px; border-radius: 4px; font-weight: bold; font-size: 12pt;")
        else:
            status.setStyleSheet("background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; padding: 6px 10px; border-radius: 4px; font-weight: bold; font-size: 12pt;")
        
        header_layout.addWidget(status, alignment=Qt.AlignmentFlag.AlignRight)
        
        layout.addLayout(header_layout)
        
        # Timer
        timer_display = QLabel(f"{timer_data.get('current_timer', '0')} secondi")
        timer_display.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        timer_display.setStyleSheet("margin: 15px 0; text-align: center; color: #000000;")
        timer_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(timer_display)
        
        # Visualizza informazioni sui posti liberi se presenti
        if 'seat_info' in timer_data and 'open_seats' in timer_data['seat_info'] and timer_data['seat_info']['open_seats']:
            seats = ', '.join(map(str, timer_data['seat_info']['open_seats']))
            seat_info = QLabel(f"SEAT OPEN: {seats}")
            seat_info.setStyleSheet("""
                background-color: #fde68a; 
                color: #854d0e; 
                padding: 8px 12px; 
                border-radius: 4px; 
                font-weight: bold;
                margin: 8px 0;
                font-size: 14pt;
            """)
            seat_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # Aggiungi un menu contestuale al label dei posti
            seat_info.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            seat_info.customContextMenuRequested.connect(self.show_seat_context_menu)
            
            layout.addWidget(seat_info)
        
        # Info panel
        info_layout = QHBoxLayout()
        
        # T1 value
        t1_label = QLabel(f"T1: {timer_data.get('t1_value', 'N/A')}s")
        t1_label.setStyleSheet("background-color: #f8f9fa; padding: 5px 10px; border-radius: 4px; font-size: 12pt;")
        info_layout.addWidget(t1_label)
        
        # T2 value
        t2_label = QLabel(f"T2: {timer_data.get('t2_value', 'N/A')}s")
        t2_label.setStyleSheet("background-color: #f8f9fa; padding: 5px 10px; border-radius: 4px; font-size: 12pt;")
        info_layout.addWidget(t2_label)
        
        # Battery
        battery_level = timer_data.get('battery_level', 0)
        battery_style = "color: #dc3545;" if battery_level < 20 else "color: #28a745;"
        battery_label = QLabel(f"Batteria: {battery_level}%")
        battery_label.setStyleSheet(f"background-color: #f8f9fa; padding: 5px 10px; border-radius: 4px; {battery_style} font-size: 12pt;")
        info_layout.addWidget(battery_label)
        
        layout.addLayout(info_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        # Start button
        start_btn = QPushButton("Start")
        start_btn.setStyleSheet("background-color: #28a745; color: white; font-weight: bold; font-size: 12pt;")
        start_btn.clicked.connect(self.on_start_click)
        start_btn.setEnabled(not (is_running and not is_paused))
        button_layout.addWidget(start_btn)
        
        # Pause button
        pause_btn = QPushButton("Pause")
        pause_btn.setStyleSheet("background-color: #ffc107; color: #212529; font-weight: bold; font-size: 12pt;")
        pause_btn.clicked.connect(self.on_pause_click)
        pause_btn.setEnabled(is_running and not is_paused)
        button_layout.addWidget(pause_btn)
        
        # Dettagli button
        details_btn = QPushButton("Dettagli")
        details_btn.setStyleSheet("background-color: #6c757d; color: white; font-weight: bold; font-size: 12pt;")
        details_btn.clicked.connect(self.on_details_click)
        button_layout.addWidget(details_btn)
        
        layout.addLayout(button_layout)
        
        # Stato connessione
        is_online = self.server.is_timer_online(timer_data)
        status_bar = QLabel("Online" if is_online else "Offline")
        status_bar.setStyleSheet(f"color: {'#28a745' if is_online else '#dc3545'}; font-size: 12pt; font-weight: bold; text-align: right;")
        status_bar.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(status_bar)
        
        # Menu contestuale
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
    
    def on_start_click(self):
        """Invia il comando di avvio al timer"""
        self.server.send_command(self.device_id, "start")
    
    def on_pause_click(self):
        """Invia il comando di pausa al timer"""
        self.server.send_command(self.device_id, "pause")
    
    def on_details_click(self):
        """Apre la finestra di dialogo dei dettagli"""
        dialog = TimerDetailsDialog(self.device_id, self.timer_data, self.server, self)
        dialog.exec()
    
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
        details_action.triggered.connect(self.on_details_click)
        menu.addAction(details_action)
        
        # Se ci sono posti liberi, aggiungi l'opzione per resetarli
        if 'seat_info' in self.timer_data and 'open_seats' in self.timer_data['seat_info'] and self.timer_data['seat_info']['open_seats']:
            menu.addSeparator()
            
            reset_seats_action = QAction("Reset posti liberi", self)
            reset_seats_action.triggered.connect(self.reset_seat_info)
            menu.addAction(reset_seats_action)
        
        # Mostra il menu
        menu.exec(self.mapToGlobal(pos))
    
    def show_seat_context_menu(self, pos):
        """Mostra il menu contestuale per il label dei posti liberi"""
        menu = QMenu(self)
        
        reset_seats_action = QAction("Reset posti liberi", self)
        reset_seats_action.triggered.connect(self.reset_seat_info)
        menu.addAction(reset_seats_action)
        
        menu.exec(self.mapToGlobal(pos))
    
    def reset_seat_info(self):
        """Reset delle informazioni sui posti liberi"""
        seats = self.timer_data.get('seat_info', {}).get('open_seats', [])
        seats_str = ', '.join(map(str, seats))
        
        reply = QMessageBox.question(
            self, 'Conferma Reset',
            f'Vuoi rimuovere l\'indicazione di posti liberi ({seats_str}) per il tavolo {self.timer_data.get("table_number", "N/A")}?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Reset dei posti
            self.server.reset_seat_info(self.device_id)