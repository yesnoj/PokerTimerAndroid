#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Gestione delle notifiche desktop e in-app
"""

import os
import sys
import platform
from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLabel, 
                           QPushButton, QApplication)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QRect, pyqtSignal

class ToastNotification(QWidget):
    """Widget per notifiche tipo toast"""
    closed = pyqtSignal()
    
    def __init__(self, title, message, type="info", duration=5000, parent=None):
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
        container_layout = QHBoxLayout(container)
        container_layout.setContentsMargins(10, 10, 10, 10)
        
        # Contenuto
        content_layout = QVBoxLayout()
        
        # Titolo
        title_label = QLabel(title)
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        content_layout.addWidget(title_label)
        
        # Messaggio
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        content_layout.addWidget(message_label)
        
        container_layout.addLayout(content_layout)
        
        # Pulsante di chiusura
        close_btn = QPushButton("×")
        close_btn.setFixedSize(20, 20)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #aaa;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                color: #333;
            }
        """)
        close_btn.clicked.connect(self.close_animation)
        container_layout.addWidget(close_btn, 0, Qt.AlignmentFlag.AlignTop)
        
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
        
        # Mostra il widget
        self.show()
        
        # Avvia l'animazione
        self.show_animation.start()
        
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
    
    def show_notification(self, title, message, type="info", duration=5000):
        """Mostra una notifica desktop o in-app"""
        # Prova a mostrare una notifica desktop nativa
        if self.desktop_notifications_supported:
            if self.show_desktop_notification(title, message):
                return True
        
        # Fallback a notifica in-app
        return self.show_in_app_notification(title, message, type, duration)
    
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
    
    def show_in_app_notification(self, title, message, type="info", duration=5000):
        """Mostra una notifica in-app"""
        # Se ci sono troppe notifiche attive, rimuovi le più vecchie
        while len(self.active_notifications) >= self.max_notifications:
            if self.active_notifications:
                oldest = self.active_notifications.pop(0)
                oldest.close_animation()
        
        # Crea la notifica
        notification = ToastNotification(title, message, type, duration)
        
        # Collega il segnale di chiusura
        notification.closed.connect(lambda: self.remove_notification(notification))
        
        # Calcola la posizione
        margin = self.margin
        desktop = QApplication.primaryScreen().availableGeometry()
        width = notification.width()
        height = notification.sizeHint().height()
        
        # Posizione X (fissa sul lato destro)
        pos_x = desktop.right() - width - margin
        
        # Posizione Y (dipende dalle notifiche attive)
        pos_y = desktop.bottom() - height - margin
        for n in self.active_notifications:
            pos_y -= n.height() + margin
        
        # Memorizza e mostra la notifica
        self.active_notifications.append(notification)
        notification.show_notification(QApplication.primaryScreen().availableGeometry().topRight() + Qt.QPoint(-notification.width() - margin, margin))
        
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