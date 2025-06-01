#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Modulo per l'integrazione di ngrok nel Poker Timer Server
Consente l'accesso al server da qualsiasi rete tramite tunnel ngrok
"""

import os
import sys
import time
import logging
import threading
import qrcode
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QLineEdit, QCheckBox, QMessageBox,
                           QWidget)
from PyQt6.QtCore import Qt, pyqtSignal, QObject
from PyQt6.QtGui import QFont, QPixmap, QImage



# Configura logging
logger = logging.getLogger('ngrok_service')
logger.setLevel(logging.INFO)

# Prova a importare pyngrok
try:
    from pyngrok import ngrok, conf
    HAS_NGROK = True
except ImportError:
    HAS_NGROK = False
    logger.warning("pyngrok non trovato. Tunneling esterno non disponibile.")

class NgrokService(QObject):
    """Servizio per gestire il tunneling ngrok"""
    
    # Segnali emessi dal servizio
    tunnel_started = pyqtSignal(str)  # URL pubblico
    tunnel_stopped = pyqtSignal()
    tunnel_error = pyqtSignal(str)    # Messaggio d'errore
    
    def __init__(self, http_port=3000):
        super().__init__()
        self.http_port = http_port
        self.tunnel = None
        self.public_url = None
        self.is_running = False
        self.ngrok_thread = None
    
    def start_tunnel(self, authtoken=None):
        """Avvia il tunnel ngrok"""
        if not HAS_NGROK:
            self.tunnel_error.emit("Pacchetto pyngrok non installato. Esegui: pip install pyngrok")
            return False
        
        # Configura il token di autenticazione se fornito
        if authtoken:
            conf.get_default().auth_token = authtoken
        
        # Avvia in un thread separato per non bloccare l'UI
        self.ngrok_thread = threading.Thread(target=self._start_tunnel_thread)
        self.ngrok_thread.daemon = True
        self.ngrok_thread.start()
        
        return True
    
    def _start_tunnel_thread(self):
        """Thread interno per avviare ngrok"""
        try:
            # Verifica se c'è già un tunnel attivo
            existing_tunnels = ngrok.get_tunnels()
            
            for tunnel in existing_tunnels:
                # Cerca un tunnel HTTP/HTTPS esistente
                if tunnel.proto in ['http', 'https'] and f":{self.http_port}" in tunnel.config['addr']:
                    # Usa il tunnel esistente
                    self.tunnel = tunnel
                    self.public_url = tunnel.public_url
                    
                    # Converti da http a https se necessario
                    if self.public_url.startswith("http://"):
                        self.public_url = "https://" + self.public_url[7:]
                    
                    logger.info(f"Riutilizzo tunnel ngrok esistente: {self.public_url}")
                    self.is_running = True
                    
                    # Emetti il segnale con l'URL pubblico
                    self.tunnel_started.emit(self.public_url)
                    return
            
            # Se non ci sono tunnel esistenti, prova a chiudere tutti i processi ngrok
            logger.info("Tentativo di chiusura di tutti i processi ngrok esistenti")
            ngrok.kill()
            
            # Attendi che tutti i processi siano chiusi
            time.sleep(2)
            
            # Avvia un nuovo tunnel
            logger.info(f"Avvio tunnel ngrok sulla porta {self.http_port}")
            self.tunnel = ngrok.connect(self.http_port, "http")
            self.public_url = self.tunnel.public_url
            
            # Converti da http a https se necessario
            if self.public_url.startswith("http://"):
                self.public_url = "https://" + self.public_url[7:]
            
            logger.info(f"Tunnel ngrok avviato: {self.public_url}")
            self.is_running = True
            
            # Emetti il segnale con l'URL pubblico
            self.tunnel_started.emit(self.public_url)
            
        except Exception as e:
            logger.error(f"Errore nell'avvio del tunnel ngrok: {e}")
            self.tunnel_error.emit(f"Errore nell'avvio del tunnel: {str(e)}")
            self.is_running = False
    
    def stop_tunnel(self):
        """Ferma il tunnel ngrok"""
        if not HAS_NGROK:
            return
        
        try:
            self.is_running = False
            
            if self.tunnel:
                logger.info("Chiusura tunnel ngrok")
                ngrok.disconnect(self.tunnel.public_url)
                self.tunnel = None
                self.public_url = None
            
            # Per sicurezza, termina tutti i processi ngrok
            ngrok.kill()
            
            # Emetti il segnale
            self.tunnel_stopped.emit()
            
            logger.info("Tunnel ngrok fermato")
            
        except Exception as e:
            logger.error(f"Errore nella chiusura del tunnel ngrok: {e}")
            self.tunnel_error.emit(f"Errore nella chiusura del tunnel: {str(e)}")
    
    def get_status(self):
        """Restituisce lo stato corrente del tunnel"""
        if not HAS_NGROK:
            return {
                "running": False,
                "error": "pyngrok non installato"
            }
        
        return {
            "running": self.is_running,
            "public_url": self.public_url
        }


class NgrokConfigDialog(QDialog):
    """Dialog per configurare ngrok"""
    
    def __init__(self, parent=None, http_port=3000, authtoken=None):
        super().__init__(parent)
        
        self.http_port = http_port
        self.saved_authtoken = authtoken
        self.ngrok_service = NgrokService(http_port)
        
        # Connetti i segnali
        self.ngrok_service.tunnel_started.connect(self.on_tunnel_started)
        self.ngrok_service.tunnel_stopped.connect(self.on_tunnel_stopped)
        self.ngrok_service.tunnel_error.connect(self.on_tunnel_error)
        
        self.init_ui()
    
    def init_ui(self):
        """Inizializza l'interfaccia utente"""
        self.setWindowTitle("Configurazione accesso esterno (ngrok)")
        self.setMinimumWidth(600)
        
        # Layout principale
        layout = QVBoxLayout(self)
        
        # Titolo
        title_label = QLabel("Configurazione ngrok - Accesso esterno")
        title_label.setStyleSheet("font-size: 16pt; font-weight: bold;")
        layout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Spiegazione
        info_text = """
        <p>ngrok consente di esporre il server locale su Internet, permettendo l'accesso ai QR code
        per il servizio bar da qualsiasi rete.</p>
        
        <p>Per utilizzare questo servizio è necessario:
        <ol>
            <li>Registrarsi gratuitamente su <a href="https://ngrok.com">ngrok.com</a></li>
            <li>Ottenere un token di autenticazione dalla dashboard ngrok</li>
            <li>Inserire il token nel campo sottostante</li>
        </ol>
        </p>
        """
        info_label = QLabel(info_text)
        info_label.setWordWrap(True)
        info_label.setOpenExternalLinks(True)
        layout.addWidget(info_label)
        
        # Separatore
        separator = QLabel()
        separator.setFrameShape(QLabel.Shape.HLine)
        separator.setFrameShadow(QLabel.Shadow.Sunken)
        layout.addWidget(separator)
        
        # Campo per il token
        token_layout = QHBoxLayout()
        token_label = QLabel("Auth Token:")
        self.token_input = QLineEdit()
        self.token_input.setPlaceholderText("Inserisci il tuo token ngrok...")
        if self.saved_authtoken:
            self.token_input.setText(self.saved_authtoken)
        
        token_layout.addWidget(token_label)
        token_layout.addWidget(self.token_input, 1)  # 1 = stretch factor
        layout.addLayout(token_layout)
        
        # Stato corrente
        self.status_layout = QHBoxLayout()
        self.status_label = QLabel("Stato: Non attivo")
        self.status_label.setStyleSheet("font-weight: bold; color: #777;")
        self.status_layout.addWidget(self.status_label)
        layout.addLayout(self.status_layout)
        
        # URL pubblico (inizialmente nascosto)
        self.url_container = QWidget()  # Crea un widget contenitore
        self.url_layout = QHBoxLayout(self.url_container)  # Associa il layout al contenitore
        self.url_label = QLabel("URL pubblico:")
        self.url_value = QLabel("N/A")
        self.url_value.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.url_layout.addWidget(self.url_label)
        self.url_layout.addWidget(self.url_value, 1)
        self.url_container.setVisible(False)  # Nascondi il contenitore invece del layout
        layout.addWidget(self.url_container)  # Aggiungi il contenitore al layout principale
        
        
        # QR Code display (inizialmente nascosto)
        self.qr_container = QLabel("QR Code non disponibile")
        self.qr_container.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.qr_container.setVisible(False)
        layout.addWidget(self.qr_container)
        
        # Avvio automatico
        self.autostart_check = QCheckBox("Avvia automaticamente all'avvio del server")
        layout.addWidget(self.autostart_check)
        
        # Pulsanti di controllo
        button_layout = QHBoxLayout()
        
        self.start_button = QPushButton("Avvia Tunnel")
        self.start_button.clicked.connect(self.start_tunnel)
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        
        self.stop_button = QPushButton("Ferma Tunnel")
        self.stop_button.clicked.connect(self.stop_tunnel)
        self.stop_button.setEnabled(False)
        self.stop_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        layout.addLayout(button_layout)
        
        # Pulsante Chiudi
        close_button = QPushButton("Chiudi")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button, alignment=Qt.AlignmentFlag.AlignRight)
        
        # Controlla se pyngrok è installato
        if not HAS_NGROK:
            self.show_ngrok_missing_message()
    
    def show_ngrok_missing_message(self):
        """Mostra un messaggio se pyngrok non è installato"""
        QMessageBox.warning(
            self,
            "Dipendenza mancante",
            "Il pacchetto 'pyngrok' non è installato. Questa funzionalità richiede pyngrok.\n\n"
            "Installa pyngrok con il comando:\npip install pyngrok",
            QMessageBox.StandardButton.Ok
        )
        self.start_button.setEnabled(False)
    
    def start_tunnel(self):
        """Avvia il tunnel ngrok"""
        # Ottieni il token
        authtoken = self.token_input.text().strip()
        
        if not authtoken:
            QMessageBox.warning(
                self,
                "Token mancante",
                "Per utilizzare ngrok è necessario inserire un token di autenticazione.\n\n"
                "Registrati su ngrok.com per ottenere un token gratuito.",
                QMessageBox.StandardButton.Ok
            )
            return
        
        # Aggiorna l'interfaccia
        self.status_label.setText("Stato: Avvio in corso...")
        self.status_label.setStyleSheet("font-weight: bold; color: #ff9800;")
        self.start_button.setEnabled(False)
        
        # Avvia il tunnel
        if not self.ngrok_service.start_tunnel(authtoken):
            # Errore gestito dai segnali
            return
    
    def stop_tunnel(self):
        """Ferma il tunnel ngrok"""
        self.status_label.setText("Stato: Arresto in corso...")
        self.status_label.setStyleSheet("font-weight: bold; color: #ff9800;")
        self.stop_button.setEnabled(False)
        
        # Ferma il tunnel
        self.ngrok_service.stop_tunnel()
    
    def on_tunnel_started(self, public_url):
        """Gestisce l'evento di avvio del tunnel"""
        # Aggiorna l'interfaccia
        self.status_label.setText("Stato: Attivo")
        self.status_label.setStyleSheet("font-weight: bold; color: #4CAF50;")
        
        self.url_value.setText(public_url)
        
        # Rendi visibile il container, non il layout
        self.url_container.setVisible(True)
        
        # Aggiorna lo stato dei pulsanti
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
    
    def on_tunnel_stopped(self):
        """Gestisce l'evento di arresto del tunnel"""
        # Aggiorna l'interfaccia
        self.status_label.setText("Stato: Non attivo")
        self.status_label.setStyleSheet("font-weight: bold; color: #777;")
        
        # Nascondi il container, non il layout
        self.url_container.setVisible(False)
        
        # Aggiorna lo stato dei pulsanti
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
    
    def on_tunnel_error(self, error_message):
        """Gestisce gli errori del tunnel"""
        # Aggiorna l'interfaccia
        self.status_label.setText("Stato: Errore")
        self.status_label.setStyleSheet("font-weight: bold; color: #f44336;")
        
        # Mostra il messaggio di errore
        QMessageBox.critical(
            self,
            "Errore ngrok",
            f"Si è verificato un errore con il tunnel ngrok:\n\n{error_message}",
            QMessageBox.StandardButton.Ok
        )
        
        # Aggiorna lo stato dei pulsanti
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
    
    def generate_qr_code(self, url):
        """Genera e visualizza un QR code per l'URL pubblico"""
        try:
            # Crea il QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=10,
                border=4,
            )
            qr.add_data(url)
            qr.make(fit=True)
            
            # Crea un'immagine dal QR code
            qr_img = qr.make_image(fill_color="black", back_color="white")
            
            # Aggiungi testo informativo sotto
            img_width, img_height = qr_img.size
            new_height = img_height + 50
            new_img = Image.new('RGB', (img_width, new_height), color='white')
            new_img.paste(qr_img, (0, 0))
            
            # Aggiungi il testo
            draw = ImageDraw.Draw(new_img)
            
            # Usa un font di default
            try:
                font = ImageFont.truetype("Arial", 15)
            except:
                font = ImageFont.load_default()
            
            text = "Scansiona per test accesso esterno"
            text_width = draw.textlength(text, font=font)
            text_position = ((img_width - text_width) // 2, img_height + 15)
            draw.text(text_position, text, font=font, fill="black")
            
            # Converti l'immagine PIL in QImage/QPixmap
            img_bytes = BytesIO()
            new_img.save(img_bytes, format='PNG')
            img_data = img_bytes.getvalue()
            
            qimage = QImage.fromData(img_data)
            pixmap = QPixmap.fromImage(qimage)
            
            # Mostra il QR code
            self.qr_container.setPixmap(pixmap)
            self.qr_container.setVisible(True)
            
        except Exception as e:
            logger.error(f"Errore nella generazione del QR code: {e}")
            self.qr_container.setText(f"Errore nella generazione del QR code: {str(e)}")
            self.qr_container.setVisible(True)
    
    def get_settings(self):
        """Restituisce le impostazioni configurate"""
        return {
            'authtoken': self.token_input.text().strip(),
            'autostart': self.autostart_check.isChecked(),
            'is_running': self.ngrok_service.is_running,
            'public_url': self.ngrok_service.public_url
        }
    
    def closeEvent(self, event):
        """Gestisce la chiusura della finestra"""
        # Assicurati che il servizio ngrok continui a funzionare
        # anche dopo la chiusura della finestra se attivo
        if self.ngrok_service.is_running:
            event.accept()
        else:
            # Se non è attivo, ferma completamente il servizio
            self.ngrok_service.stop_tunnel()
            event.accept()