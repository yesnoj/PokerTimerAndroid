#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Dialog avanzato per la configurazione di ngrok con interfaccia migliorata
"""

import os
import sys
import qrcode
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QLineEdit, QCheckBox, QMessageBox,
                           QTabWidget, QWidget, QFormLayout, QFrame,
                           QProgressBar, QFileDialog, QComboBox, QSpinBox)
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot, QSize, QTimer, QUrl
from PyQt6.QtGui import QFont, QPixmap, QImage, QDesktopServices, QIcon, QPalette, QColor

from .package_installer import check_and_install_package
from .ngrok_integration import NgrokService, NgrokTunnelInfo

class AdvancedNgrokDialog(QDialog):
    """Dialog avanzato per la configurazione di ngrok"""
    
    def __init__(self, parent=None, http_port=3000, authtoken=None):
        super().__init__(parent)
        
        # Verifica se pyngrok è installato
        self.has_ngrok = check_and_install_package("pyngrok", self)
        
        self.http_port = http_port
        self.saved_authtoken = authtoken
        self.ngrok_service = NgrokService(http_port)
        
        # Connetti i segnali
        self.ngrok_service.tunnel_started.connect(self.on_tunnel_started)
        self.ngrok_service.tunnel_stopped.connect(self.on_tunnel_stopped)
        self.ngrok_service.tunnel_error.connect(self.on_tunnel_error)
        self.ngrok_service.tunnel_status.connect(self.on_tunnel_status)
        
        self.init_ui()
    
    def init_ui(self):
        """Inizializza l'interfaccia utente migliorata"""
        self.setWindowTitle("Configurazione Accesso Remoto")
        self.setMinimumWidth(700)
        self.setMinimumHeight(500)
        
        # Layout principale
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        self.setup_tab = QWidget()
        self.status_tab = QWidget()
        self.qr_tab = QWidget()
        self.help_tab = QWidget()
        
        self.tab_widget.addTab(self.setup_tab, "Configurazione")
        self.tab_widget.addTab(self.status_tab, "Stato")
        self.tab_widget.addTab(self.qr_tab, "QR Test")
        self.tab_widget.addTab(self.help_tab, "Aiuto")
        
        # Imposta le icone per i tab se sono disponibili
        try:
            icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'resources', 'icons')
            
            setup_icon = os.path.join(icon_path, 'ic_settings.svg')
            status_icon = os.path.join(icon_path, 'ic_status.svg')
            qr_icon = os.path.join(icon_path, 'ic_qrcode.svg')
            help_icon = os.path.join(icon_path, 'ic_help.svg')
            
            if os.path.exists(setup_icon):
                self.tab_widget.setTabIcon(0, QIcon(setup_icon))
            if os.path.exists(status_icon):
                self.tab_widget.setTabIcon(1, QIcon(status_icon))
            if os.path.exists(qr_icon):
                self.tab_widget.setTabIcon(2, QIcon(qr_icon))
            if os.path.exists(help_icon):
                self.tab_widget.setTabIcon(3, QIcon(help_icon))
        except Exception as e:
            print(f"Errore nel caricamento delle icone: {e}")
        
        # Configura i singoli tab
        self._setup_configuration_tab()
        self._setup_status_tab()
        self._setup_qr_tab()
        self._setup_help_tab()
        
        layout.addWidget(self.tab_widget)
        
        # Pulsanti di controllo
        button_layout = QHBoxLayout()
        
        self.close_button = QPushButton("Chiudi")
        self.close_button.clicked.connect(self.accept)
        
        button_layout.addStretch()
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
        
        # Timer per aggiornamenti periodici
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_status)
        self.update_timer.start(5000)  # Aggiorna ogni 5 secondi
        
        # Controlla se pyngrok è installato
        if not self.has_ngrok:
            self.show_ngrok_missing_message()
    
    def _setup_configuration_tab(self):
        """Configura il tab di configurazione"""
        layout = QVBoxLayout(self.setup_tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # Titolo
        title_label = QLabel("Configurazione Accesso Remoto (ngrok)")
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
        
        # Form layout per i campi
        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(10)
        form_layout.setHorizontalSpacing(15)
        
        # Campo per il token
        self.token_input = QLineEdit()
        self.token_input.setPlaceholderText("Inserisci il tuo token ngrok...")
        if self.saved_authtoken:
            self.token_input.setText(self.saved_authtoken)
        form_layout.addRow("Auth Token:", self.token_input)
        
        # Campo per la porta HTTP
        self.port_input = QSpinBox()
        self.port_input.setRange(1024, 65535)
        self.port_input.setValue(self.http_port)
        form_layout.addRow("Porta HTTP:", self.port_input)
        
        # Opzione per avvio automatico
        self.autostart_check = QCheckBox("Avvia automaticamente all'avvio del server")
        form_layout.addRow("", self.autostart_check)
        
        layout.addLayout(form_layout)
        
        # Separatore
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)
        
        # Stato corrente
        status_layout = QHBoxLayout()
        status_layout.setSpacing(10)
        
        self.status_label = QLabel("Stato: Non attivo")
        self.status_label.setStyleSheet("font-weight: bold; color: #777;")
        status_layout.addWidget(self.status_label)
        
        status_layout.addStretch()
        
        self.url_label = QLabel("")
        self.url_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        status_layout.addWidget(self.url_label)
        
        layout.addLayout(status_layout)
        
        # Pulsanti di controllo
        control_layout = QHBoxLayout()
        control_layout.setSpacing(10)
        
        self.start_button = QPushButton("Avvia Tunnel")
        self.start_button.clicked.connect(self.start_tunnel)
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px 16px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
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
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        
        control_layout.addWidget(self.start_button)
        control_layout.addWidget(self.stop_button)
        
        layout.addLayout(control_layout)
        
        # Spazio vuoto in fondo
        layout.addStretch()
    
    def _setup_status_tab(self):
        """Configura il tab di stato"""
        layout = QVBoxLayout(self.status_tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # Titolo
        title_label = QLabel("Stato del Tunnel")
        title_label.setStyleSheet("font-size: 16pt; font-weight: bold;")
        layout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Riquadro di stato
        status_frame = QFrame()
        status_frame.setFrameShape(QFrame.Shape.StyledPanel)
        status_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 8px;
                border: 1px solid #dee2e6;
            }
        """)
        
        status_layout = QVBoxLayout(status_frame)
        status_layout.setSpacing(10)
        
        # Stato generale
        self.general_status = QLabel("Stato: Non attivo")
        self.general_status.setStyleSheet("font-size: 14pt; font-weight: bold; color: #777;")
        status_layout.addWidget(self.general_status)
        
        # URL pubblico
        self.public_url_label = QLabel("URL pubblico: N/A")
        self.public_url_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        status_layout.addWidget(self.public_url_label)
        
        # Pulsante copia URL
        self.copy_url_button = QPushButton("Copia URL")
        self.copy_url_button.clicked.connect(self.copy_url)
        self.copy_url_button.setEnabled(False)
        status_layout.addWidget(self.copy_url_button, alignment=Qt.AlignmentFlag.AlignRight)
        
        # Separatore
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        status_layout.addWidget(separator)
        
        # Informazioni dettagliate
        self.detail_info = QLabel("Nessuna informazione disponibile")
        self.detail_info.setWordWrap(True)
        status_layout.addWidget(self.detail_info)
        
        layout.addWidget(status_frame)
        
        # Pulsante aggiorna
        self.refresh_button = QPushButton("Aggiorna Stato")
        self.refresh_button.clicked.connect(self.update_status)
        layout.addWidget(self.refresh_button, alignment=Qt.AlignmentFlag.AlignRight)
        
        # Spazio vuoto in fondo
        layout.addStretch()
    
    def _setup_qr_tab(self):
        """Configura il tab del QR code di test"""
        layout = QVBoxLayout(self.qr_tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # Titolo
        title_label = QLabel("Test QR Code")
        title_label.setStyleSheet("font-size: 16pt; font-weight: bold;")
        layout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Spiegazione
        info_text = """
        <p>Questo QR code di test ti permette di verificare il funzionamento dell'accesso remoto.</p>
        <p>Scansiona il codice con il tuo smartphone e verifica che si apra la pagina web anche usando la rete dati mobili.</p>
        """
        info_label = QLabel(info_text)
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Container per il QR code
        qr_container = QFrame()
        qr_container.setFrameShape(QFrame.Shape.StyledPanel)
        qr_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #dee2e6;
            }
        """)
        
        qr_layout = QVBoxLayout(qr_container)
        
        # QR code placeholder
        self.qr_label = QLabel("QR Code non disponibile - Avvia il tunnel per generare un QR code di test")
        self.qr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.qr_label.setMinimumHeight(200)
        qr_layout.addWidget(self.qr_label)
        
        layout.addWidget(qr_container)
        
        # Tavolo di test
        test_layout = QHBoxLayout()
        test_layout.setSpacing(10)
        
        test_layout.addWidget(QLabel("Tavolo di test:"))
        
        self.table_selector = QSpinBox()
        self.table_selector.setRange(1, 99)
        self.table_selector.setValue(1)
        self.table_selector.valueChanged.connect(self.update_qr_code)
        test_layout.addWidget(self.table_selector)
        
        test_layout.addStretch()
        
        self.generate_qr_button = QPushButton("Genera QR Code")
        self.generate_qr_button.clicked.connect(self.update_qr_code)
        self.generate_qr_button.setEnabled(False)
        test_layout.addWidget(self.generate_qr_button)
        
        layout.addLayout(test_layout)
        
        # Bottone apri URL
        self.open_url_button = QPushButton("Apri URL nel browser")
        self.open_url_button.clicked.connect(self.open_test_url)
        self.open_url_button.setEnabled(False)
        layout.addWidget(self.open_url_button, alignment=Qt.AlignmentFlag.AlignRight)
        
        # Spazio vuoto in fondo
        layout.addStretch()
    
    def _setup_help_tab(self):
        """Configura il tab di aiuto"""
        layout = QVBoxLayout(self.help_tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # Titolo
        title_label = QLabel("Aiuto e Informazioni")
        title_label.setStyleSheet("font-size: 16pt; font-weight: bold;")
        layout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Contenuto
        help_text = """
        <h3>Cos'è ngrok?</h3>
        <p>ngrok è un servizio che crea tunnel sicuri verso il tuo server locale, permettendo l'accesso da Internet senza configurare il router o ottenere un IP pubblico.</p>
        
        <h3>Come funziona?</h3>
        <p>Quando avvii il tunnel, ngrok crea un collegamento tra il tuo server locale e i server cloud di ngrok. Questo collegamento permette ai giocatori di accedere al server anche senza essere connessi alla tua rete WiFi.</p>
        
        <h3>Cosa serve per utilizzarlo?</h3>
        <ul>
            <li>Un account ngrok gratuito</li>
            <li>Un token di autenticazione (ottenibile dalla dashboard ngrok)</li>
            <li>Una connessione Internet sul computer che esegue il server</li>
        </ul>
        
        <h3>Vantaggi principali</h3>
        <ul>
            <li>I giocatori possono effettuare richieste usando la propria connessione dati mobili</li>
            <li>Non è necessario configurare il router o la rete</li>
            <li>Facile da usare e configurare</li>
        </ul>
        
        <h3>Limitazioni</h3>
        <p>Con un account gratuito di ngrok:</p>
        <ul>
            <li>L'URL cambia a ogni avvio del tunnel</li>
            <li>Numero limitato di connessioni simultanee (40)</li>
            <li>Banda limitata (ma sufficiente per le richieste bar)</li>
        </ul>
        
        <h3>Problemi comuni</h3>
        <p>Se riscontri problemi con il tunnel ngrok:</p>
        <ul>
            <li>Verifica che il token di autenticazione sia corretto</li>
            <li>Assicurati di avere una connessione Internet attiva</li>
            <li>Prova a riavviare il tunnel</li>
            <li>Verifica che non ci siano altri tunnel ngrok attivi</li>
        </ul>
        """
        
        help_label = QLabel(help_text)
        help_label.setWordWrap(True)
        help_label.setOpenExternalLinks(True)
        help_label.setTextFormat(Qt.TextFormat.RichText)
        
        # Aggiungi la label a uno scroll area
        scroll_area = QWidget()
        scroll_layout = QVBoxLayout(scroll_area)
        scroll_layout.addWidget(help_label)
        scroll_layout.addStretch()
        
        layout.addWidget(scroll_area)
        
        # Link esterni
        links_layout = QHBoxLayout()
        
        ngrok_site_button = QPushButton("Sito ngrok")
        ngrok_site_button.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://ngrok.com")))
        
        docs_button = QPushButton("Documentazione ngrok")
        docs_button.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://ngrok.com/docs")))
        
        links_layout.addWidget(ngrok_site_button)
        links_layout.addWidget(docs_button)
        
        layout.addLayout(links_layout)
    
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
    
    def copy_url(self):
        """Copia l'URL pubblico negli appunti"""
        if self.ngrok_service.public_url:
            from PyQt6.QtWidgets import QApplication
            QApplication.clipboard().setText(self.ngrok_service.public_url)
            
            # Mostra un messaggio di conferma temporaneo
            old_text = self.copy_url_button.text()
            self.copy_url_button.setText("Copiato!")
            
            # Ripristina il testo originale dopo 2 secondi
            QTimer.singleShot(2000, lambda: self.copy_url_button.setText(old_text))
    
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
        self.general_status.setText("Stato: Avvio in corso...")
        self.general_status.setStyleSheet("font-size: 14pt; font-weight: bold; color: #ff9800;")
        self.start_button.setEnabled(False)
        
        # Avvia il tunnel
        if not self.ngrok_service.start_tunnel(authtoken):
            # Errore gestito dai segnali
            return
        
        # Passa al tab di stato
        self.tab_widget.setCurrentIndex(1)
    
    def stop_tunnel(self):
        """Ferma il tunnel ngrok"""
        self.status_label.setText("Stato: Arresto in corso...")
        self.status_label.setStyleSheet("font-weight: bold; color: #ff9800;")
        self.general_status.setText("Stato: Arresto in corso...")
        self.general_status.setStyleSheet("font-size: 14pt; font-weight: bold; color: #ff9800;")
        self.stop_button.setEnabled(False)
        
        # Ferma il tunnel
        self.ngrok_service.stop_tunnel()
    
    def update_status(self):
        """Aggiorna lo stato visualizzato"""
        if not self.has_ngrok:
            return
            
        # Ottieni lo stato attuale
        status = self.ngrok_service.get_status()
        
        # Aggiorna lo stato generale
        if status.get("running", False):
            # Tunnel attivo
            self.status_label.setText("Stato: Attivo")
            self.status_label.setStyleSheet("font-weight: bold; color: #4CAF50;")
            self.general_status.setText("Stato: Attivo")
            self.general_status.setStyleSheet("font-size: 14pt; font-weight: bold; color: #4CAF50;")
            
            # URL pubblico
            public_url = status.get("public_url", "N/A")
            self.url_label.setText(f"URL: {public_url}")
            self.public_url_label.setText(f"URL pubblico: {public_url}")
            
            # Abilita i pulsanti relativi all'URL
            self.copy_url_button.setEnabled(True)
            self.generate_qr_button.setEnabled(True)
            self.open_url_button.setEnabled(True)
            
            # Aggiorna il QR code se necessario
            self.update_qr_code()
            
        else:
            # Tunnel inattivo
            self.status_label.setText("Stato: Non attivo")
            self.status_label.setStyleSheet("font-weight: bold; color: #777;")
            self.general_status.setText("Stato: Non attivo")
            self.general_status.setStyleSheet("font-size: 14pt; font-weight: bold; color: #777;")
            
            # Resetta l'URL
            self.url_label.setText("")
            self.public_url_label.setText("URL pubblico: N/A")
            
            # Disabilita i pulsanti relativi all'URL
            self.copy_url_button.setEnabled(False)
            self.generate_qr_button.setEnabled(False)
            self.open_url_button.setEnabled(False)
            
            # Resetta il QR code
            self.qr_label.setText("QR Code non disponibile - Avvia il tunnel per generare un QR code di test")
            self.qr_label.setPixmap(QPixmap())
        
        # Aggiorna i dettagli
        detail_text = self._format_status_details(status)
        self.detail_info.setText(detail_text)
        
        # Aggiorna lo stato dei pulsanti
        self.start_button.setEnabled(not status.get("running", False))
        self.stop_button.setEnabled(status.get("running", False))
    
    def _format_status_details(self, status):
        """Formatta i dettagli dello stato in formato HTML"""
        if not status.get("running", False):
            if "error" in status:
                return f"<p style='color: #dc3545;'>Errore: {status['error']}</p>"
            return "<p>Il tunnel non è attivo. Avvialo per vedere i dettagli.</p>"
        
        # Formatta i dettagli in HTML
        details = [
            f"<p><b>URL pubblico:</b> {status.get('public_url', 'N/A')}</p>",
            f"<p><b>Tunnel attivi:</b> {status.get('tunnels_count', 0)}</p>"
        ]
        
        # Aggiungi informazioni sui tunnel
        if "tunnels" in status and status["tunnels"]:
            details.append("<p><b>Dettagli tunnel:</b></p><ul>")
            for i, tunnel in enumerate(status["tunnels"]):
                details.append(f"<li>Tunnel {i+1}: {tunnel.get('public_url', 'N/A')} ({tunnel.get('proto', 'N/A')})</li>")
            details.append("</ul>")
        
        return "".join(details)
    
    def update_qr_code(self):
        """Aggiorna il QR code di test"""
        if not self.has_ngrok or not self.ngrok_service.is_running:
            return
        
        try:
            # Ottieni l'URL del tunnel
            public_url = self.ngrok_service.public_url
            if not public_url:
                return
            
            # Ottieni il numero del tavolo selezionato
            table_num = self.table_selector.value()
            
            # Crea l'URL completo per il QR code
            # Rimuovi eventuali slash finali
            if public_url.endswith('/'):
                public_url = public_url[:-1]
            
            qr_url = f"{public_url}/qr/bar-request/{table_num}"
            
            # Crea il QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=10,
                border=4,
            )
            qr.add_data(qr_url)
            qr.make(fit=True)
            
            # Crea un'immagine dal QR code
            qr_img = qr.make_image(fill_color="black", back_color="white")
            
            # Converti in RGB per poter aggiungere testo colorato
            qr_img = qr_img.convert("RGB")
            
            # Aggiungi titolo e istruzioni sotto il QR code
            img_width, img_height = qr_img.size
            
            # Crea una nuova immagine più grande per contenere il QR code e il testo
            new_height = img_height + 80  # Spazio extra per il testo
            new_img = Image.new('RGB', (img_width, new_height), color='white')
            
            # Incolla il QR code
            new_img.paste(qr_img, (0, 0))
            
            # Aggiungi il testo
            draw = ImageDraw.Draw(new_img)
            
            # Prova a caricare un font, altrimenti usa il default
            try:
                font = ImageFont.truetype("Arial", 15)
            except:
                font = ImageFont.load_default()
            
            # Titolo
            text = f"Test QR Bar - Tavolo {table_num}"
            text_width = draw.textlength(text, font=font)
            text_position = ((img_width - text_width) // 2, img_height + 15)
            draw.text(text_position, text, font=font, fill="black")
            
            # Sottotitolo
            info_text = "Scansiona per testare l'accesso remoto"
            info_width = draw.textlength(info_text, font=font)
            info_position = ((img_width - info_width) // 2, img_height + 40)
            draw.text(info_position, info_text, font=font, fill=(50, 50, 150))
            
            # Converti l'immagine PIL in QImage/QPixmap
            img_bytes = BytesIO()
            new_img.save(img_bytes, format='PNG')
            img_data = img_bytes.getvalue()
            
            qimage = QImage.fromData(img_data)
            pixmap = QPixmap.fromImage(qimage)
            
            # Ridimensiona il pixmap se necessario
            max_size = min(self.qr_label.width(), self.qr_label.height())
            if max_size > 0 and (pixmap.width() > max_size or pixmap.height() > max_size):
                pixmap = pixmap.scaled(QSize(max_size, max_size), 
                                     Qt.AspectRatioMode.KeepAspectRatio, 
                                     Qt.TransformationMode.SmoothTransformation)
            
            # Mostra il QR code
            self.qr_label.setPixmap(pixmap)
            
            # Aggiorna anche l'URL di test
            self.test_url = qr_url
            
        except Exception as e:
            print(f"Errore nella generazione del QR code: {e}")
            self.qr_label.setText(f"Errore nella generazione del QR code: {str(e)}")
    
    def open_test_url(self):
        """Apre l'URL di test nel browser"""
        if hasattr(self, 'test_url') and self.test_url:
            QDesktopServices.openUrl(QUrl(self.test_url))
    
    def on_tunnel_started(self, public_url):
        """Gestisce l'evento di avvio del tunnel"""
        # Aggiorna l'interfaccia
        self.status_label.setText("Stato: Attivo")
        self.status_label.setStyleSheet("font-weight: bold; color: #4CAF50;")
        self.general_status.setText("Stato: Attivo")
        self.general_status.setStyleSheet("font-size: 14pt; font-weight: bold; color: #4CAF50;")
        
        self.url_label.setText(f"URL: {public_url}")
        self.public_url_label.setText(f"URL pubblico: {public_url}")
        
        # Abilita i pulsanti appropriati
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.copy_url_button.setEnabled(True)
        self.generate_qr_button.setEnabled(True)
        self.open_url_button.setEnabled(True)
        
        # Genera il QR code di test
        self.update_qr_code()
        
        # Passa al tab QR test
        self.tab_widget.setCurrentIndex(2)
    
    def on_tunnel_stopped(self):
        """Gestisce l'evento di arresto del tunnel"""
        # Aggiorna l'interfaccia
        self.status_label.setText("Stato: Non attivo")
        self.status_label.setStyleSheet("font-weight: bold; color: #777;")
        self.general_status.setText("Stato: Non attivo")
        self.general_status.setStyleSheet("font-size: 14pt; font-weight: bold; color: #777;")
        
        self.url_label.setText("")
        self.public_url_label.setText("URL pubblico: N/A")
        
        # Aggiorna lo stato dei pulsanti
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.copy_url_button.setEnabled(False)
        self.generate_qr_button.setEnabled(False)
        self.open_url_button.setEnabled(False)
        
        # Resetta il QR code
        self.qr_label.setText("QR Code non disponibile - Avvia il tunnel per generare un QR code di test")
        self.qr_label.setPixmap(QPixmap())
    
    def on_tunnel_error(self, error_message):
        """Gestisce gli errori del tunnel"""
        # Aggiorna l'interfaccia
        self.status_label.setText("Stato: Errore")
        self.status_label.setStyleSheet("font-weight: bold; color: #f44336;")
        self.general_status.setText("Stato: Errore")
        self.general_status.setStyleSheet("font-size: 14pt; font-weight: bold; color: #f44336;")
        
        self.detail_info.setText(f"<p style='color: #dc3545;'>Errore: {error_message}</p>")
        
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
    
    def on_tunnel_status(self, status):
        """Gestisce gli aggiornamenti di stato del tunnel"""
        # Aggiorna i dettagli nella tab di stato
        detail_text = self._format_status_details(status)
        self.detail_info.setText(detail_text)
    
    def get_settings(self):
        """Restituisce le impostazioni configurate"""
        return {
            'authtoken': self.token_input.text().strip(),
            'autostart': self.autostart_check.isChecked(),
            'http_port': self.port_input.value(),
            'is_running': self.ngrok_service.is_running,
            'public_url': self.ngrok_service.public_url
        }
    
    def closeEvent(self, event):
        """Gestisce la chiusura della finestra"""
        # Assicurati che il servizio ngrok continui a funzionare
        # anche dopo la chiusura della finestra se attivo
        if self.ngrok_service.is_running:
            reply = QMessageBox.question(
                self,
                "Conferma",
                "Il tunnel ngrok è attivo. Vuoi fermarlo prima di chiudere?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Cancel:
                event.ignore()
                return
            elif reply == QMessageBox.StandardButton.Yes:
                self.ngrok_service.stop_tunnel()
                event.accept()
            else:
                event.accept()
        else:
            event.accept()
        self.tab_widget