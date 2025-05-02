#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Gestione delle notifiche desktop e in-app
"""

import os
import sys
import platform
import subprocess
import threading

from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLabel, 
                           QPushButton, QApplication)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QRect, pyqtSignal, QPoint
from PyQt6.QtGui import QIcon, QPixmap  # Aggiunto QIcon e QPixmap

class ToastNotification(QWidget):
    """Widget per notifiche tipo toast"""
    closed = pyqtSignal()
    action_clicked = pyqtSignal()  # Nuovo segnale per click su azione
    
    def __init__(self, title, message, type="info", duration=5000, parent=None, 
                action_button=None, device_type=None):  # Aggiunto parametro device_type
        super().__init__(parent)
        
        # Configurazione finestra
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | 
                           Qt.WindowType.WindowStaysOnTopHint | 
                           Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMinimumWidth(300)
        self.setMaximumWidth(350)
        
        # Proprietà
        self.duration = duration
        self.type = type
        
        # Layout principale
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Contenitore con sfondo e bordi
        container = QWidget()
        container.setObjectName("toast-container")
        
        # Stile del container in base al tipo
        border_color = "#4CAF50"  # Default: success (green)
        if type == "info":
            border_color = "#0dcaf0"  # Blue
        elif type == "warning":
            border_color = "#FFC107"  # Yellow
        elif type == "error":
            border_color = "#DC3545"  # Red
        
        container.setStyleSheet(f"""
            #toast-container {{
                background-color: white;
                border-left: 4px solid {border_color};
                border-radius: 4px;
                padding: 10px;
            }}
        """)
        
        # Layout del contenitore
        # Layout verticale per il contenitore principale
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(10, 10, 10, 10)
        
        # Aggiungi un layout orizzontale per il titolo e il pulsante di chiusura
        header_layout = QHBoxLayout()
        
        # Titolo
        title_label = QLabel(title)
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        header_layout.addWidget(title_label)
        
        # Icona del dispositivo (se specificata)
        if device_type:
            device_icon = QLabel()
            if device_type == "android":
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
            elif device_type == "hardware":
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
        
        # Pulsante di chiusura - con X in rosso in alto a destra
        close_btn = QPushButton("X")
        close_btn.setFixedSize(24, 24)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 12px;
                font-weight: bold;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
            QPushButton:pressed {
                background-color: #bd2130;
            }
        """)
        close_btn.clicked.connect(self.close_animation)
        header_layout.addWidget(close_btn)
        
        # Aggiungi il layout dell'header al layout principale
        container_layout.addLayout(header_layout)
        
        # Messaggio
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        container_layout.addWidget(message_label)
        
        # Pulsante di azione (se specificato)
        if action_button:
            action_btn = QPushButton(action_button)
            action_btn.setStyleSheet("""
                QPushButton {
                    background-color: #007bff;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 5px 10px;
                    font-weight: bold;
                    margin-top: 5px;
                }
                QPushButton:hover {
                    background-color: #0069d9;
                }
            """)
            action_btn.clicked.connect(self._on_action_clicked)
            container_layout.addWidget(action_btn)
        
        main_layout.addWidget(container)
        
        # Timer per auto-chiusura
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.close_animation)
        
        # Animazioni
        self.show_animation = None
        self.hide_animation = None
        
        # Configura le animazioni dopo la visualizzazione
        self.init_animations()
    
    # Resto della classe rimane invariato
    def _on_action_clicked(self):
        """Gestisce il click sul pulsante di azione"""
        self.action_clicked.emit()
        self.close_animation()  # Chiude la notifica dopo l'azione
    
    def init_animations(self):
        """Inizializza le animazioni"""
        # Per sicurezza, impostiamo l'opacità iniziale a 0
        self.setWindowOpacity(0.0)
        
        # Le animazioni verranno configurate quando conosciamo la posizione
        self.show_animation = QPropertyAnimation(self, b"windowOpacity")
        self.show_animation.setDuration(250)
        self.show_animation.setStartValue(0.0)
        self.show_animation.setEndValue(1.0)
        self.show_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        self.hide_animation = QPropertyAnimation(self, b"windowOpacity")
        self.hide_animation.setDuration(250)
        self.hide_animation.setStartValue(1.0)
        self.hide_animation.setEndValue(0.0)
        self.hide_animation.setEasingCurve(QEasingCurve.Type.InCubic)
        self.hide_animation.finished.connect(self.on_hide_finished)
    
    def show_notification(self, pos):
        """Mostra la notifica con animazione"""
        # Imposta la posizione
        self.move(pos)
        
        # Forza la dimensione
        self.setFixedSize(self.sizeHint())
        
        # Mostra il widget
        self.show()
        print(f"ToastNotification.show(): Widget mostrato in posizione {pos}")
        
        # Imposta manualmente l'opacità prima di iniziare l'animazione
        self.setWindowOpacity(0.0)
        
        # Avvia l'animazione
        self.show_animation.start()
        print(f"ToastNotification.show(): Animazione avviata")
        
        # Avvia il timer per chiusura automatica
        self.timer.start(self.duration)
    
    def close_animation(self):
        """Avvia l'animazione di chiusura"""
        self.timer.stop()
        self.hide_animation.start()
    
    def on_hide_finished(self):
        """Gestisce la fine dell'animazione di chiusura"""
        self.hide()
        self.closed.emit()
        
    def enterEvent(self, event):
        """Gestisce l'evento di ingresso del mouse"""
        self.timer.stop()
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        """Gestisce l'evento di uscita del mouse"""
        self.timer.start(self.duration)
        super().leaveEvent(event)

class NotificationManager:
    """Gestisce le notifiche desktop e in-app"""
    def __init__(self):
        self.active_notifications = []
        self.notification_height = 100  # Altezza stimata di una notifica
        self.max_notifications = 5      # Numero massimo di notifiche simultanee
        self.margin = 10                # Margine tra le notifiche
        
        # Verifica se le notifiche desktop sono supportate
        self.desktop_notifications_supported = False
        
        # Controlla il sistema operativo
        self.system = platform.system()
        
        # Inizializza il supporto alle notifiche desktop in base al sistema
        if self.system == "Windows":
            try:
                from win10toast import ToastNotifier
                self.win_toaster = ToastNotifier()
                self.desktop_notifications_supported = True
            except ImportError:
                pass
        elif self.system == "Darwin":  # macOS
            self.desktop_notifications_supported = True
        elif self.system == "Linux":
            try:
                import dbus
                self.desktop_notifications_supported = True
            except ImportError:
                pass
    
    def play_notification_sound(self, sound_file=None):
        """Riproduce un suono di notifica utilizzando strumenti nativi del sistema"""
        try:
            # Se non è specificato un file, usa quello predefinito
            if not sound_file:
                sound_file = os.path.join(
                    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    'resources', 'sounds', 'notification.wav'
                )
            
            # Verifica l'esistenza del file
            if not os.path.exists(sound_file):
                print(f"File audio non trovato: {sound_file}")
                return False
            
            # Utilizza il comando appropriato in base al sistema operativo
            if self.system == "Darwin":  # macOS
                # Usa afplay (utility nativa di macOS)
                threading.Thread(
                    target=lambda: subprocess.run(['afplay', sound_file]), 
                    daemon=True
                ).start()
                return True
            elif self.system == "Windows":
                # Usa PowerShell per riprodurre suoni su Windows
                cmd = f'powershell -c (New-Object Media.SoundPlayer "{sound_file}").PlaySync();'
                threading.Thread(
                    target=lambda: subprocess.run(cmd, shell=True), 
                    daemon=True
                ).start()
                return True
            elif self.system == "Linux":
                # Usa paplay (parte di PulseAudio) su Linux
                threading.Thread(
                    target=lambda: subprocess.run(['paplay', sound_file]), 
                    daemon=True
                ).start()
                return True
            
            print(f"Sistema operativo {self.system} non supportato per l'audio")
            return False
        except Exception as e:
            print(f"Errore nella riproduzione del suono: {e}")
            return False
    
    def show_notification(self, title, message, type="info", duration=5000, 
                         action_button=None, action_callback=None, play_sound=False, device_type=None):
        """Mostra una notifica desktop o in-app con possibile azione e suono"""
        # Riproduci suono se richiesto (solo una volta)
        if play_sound:
            self.play_notification_sound()
        
        # Prova a mostrare una notifica desktop nativa
        if self.desktop_notifications_supported:
            if self.show_desktop_notification(title, message):
                # Se è stata mostrata la notifica desktop,
                # mostra comunque quella in-app per avere il pulsante di azione
                return self.show_in_app_notification(title, message, type, duration, 
                                                   action_button, action_callback, device_type)
        
        # Fallback a notifica in-app
        return self.show_in_app_notification(title, message, type, duration, 
                                           action_button, action_callback, device_type)
        
    def show_desktop_notification(self, title, message):
        """Mostra una notifica desktop nativa"""
        try:
            if self.system == "Windows":
                # Windows 10/11
                self.win_toaster.show_toast(
                    title,
                    message,
                    duration=5,
                    threaded=True
                )
                return True
            elif self.system == "Darwin":  # macOS
                # Usa AppleScript per mostrare una notifica
                os.system(f"""
                osascript -e 'display notification "{message}" with title "{title}"'
                """)
                return True
            elif self.system == "Linux":
                # Usa D-Bus per notifiche su Linux
                import dbus
                bus = dbus.SessionBus()
                notify = bus.get_object('org.freedesktop.Notifications', 
                                      '/org/freedesktop/Notifications')
                interface = dbus.Interface(notify, 'org.freedesktop.Notifications')
                interface.Notify('Poker Timer', 0, '', title, message, [], {}, 5000)
                return True
            
            return False
        except Exception:
            return False
    
    def show_in_app_notification(self, title, message, type="info", duration=5000,
                               action_button=None, action_callback=None, device_type=None):
        """Mostra una notifica in-app con possibile pulsante di azione"""
        # Se ci sono troppe notifiche attive, rimuovi le più vecchie
        while len(self.active_notifications) >= self.max_notifications:
            if self.active_notifications:
                oldest = self.active_notifications.pop(0)
                oldest.close_animation()
        
        # Crea la notifica
        notification = ToastNotification(
            title, message, type, duration, 
            action_button=action_button,
            device_type=device_type
        )
        
        # Collega il segnale di chiusura
        notification.closed.connect(lambda: self.remove_notification(notification))
        
        # Collega il segnale di azione se specificato
        if action_callback and action_button:
            notification.action_clicked.connect(action_callback)
        
        # Calcola la posizione
        margin = self.margin
        desktop = QApplication.primaryScreen().availableGeometry()
        width = notification.sizeHint().width() or 350  # Usa una larghezza predefinita se sizeHint() non funziona
        height = notification.sizeHint().height() or 100  # Usa un'altezza predefinita se sizeHint() non funziona
        
        # Posizione X (fissa sul lato destro)
        pos_x = desktop.right() - width - margin
        
        # Posizione Y (in alto a destra)
        pos_y = desktop.top() + margin
        
        # Aggiusta la posizione Y in base alle notifiche esistenti
        for n in reversed(self.active_notifications):
            pos_y += n.height() + margin
        
        # Assicurati che la notifica sia almeno parzialmente visibile
        pos_y = min(pos_y, desktop.bottom() - height - margin)
        
        # Debugging
        print(f"Mostrando notifica in posizione: ({pos_x}, {pos_y})")
        print(f"Dimensioni desktop: {desktop.width()}x{desktop.height()}")
        print(f"Dimensioni notifica: {width}x{height}")
        
        # Memorizza e mostra la notifica
        self.active_notifications.append(notification)
        
        # Imposta subito la posizione e la visibilità
        notification.setGeometry(pos_x, pos_y, width, height)
        notification.show()
        notification.show_notification(QPoint(pos_x, pos_y))
        
        # Debug
        print(f"La notifica è visibile: {notification.isVisible()}")
        print(f"Opacità della notifica: {notification.windowOpacity()}")
        
        return True
    
    def remove_notification(self, notification):
        """Rimuove una notifica dall'elenco delle attive"""
        if notification in self.active_notifications:
            self.active_notifications.remove(notification)
            notification.deleteLater()
            
            # Riposiziona le notifiche rimanenti
            self.reposition_notifications()
    
    def reposition_notifications(self):
        """Riposiziona le notifiche attive"""
        if not self.active_notifications:
            return
        
        # Calcola le nuove posizioni
        margin = self.margin
        desktop = QApplication.primaryScreen().availableGeometry()
        pos_y = margin
        
        for notification in self.active_notifications:
            pos_x = desktop.right() - notification.width() - margin
            notification.move(pos_x, pos_y)
            pos_y += notification.height() + margin