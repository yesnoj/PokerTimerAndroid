#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Implementazione completa del servizio ngrok con gestione avanzata degli errori
"""

import os
import sys
import time
import logging
import threading
import json
import tempfile
import re
from PyQt6.QtCore import QObject, pyqtSignal, QThread, QTimer
from PyQt6.QtWidgets import QMessageBox

# Inizializza logger con gestione avanzata
logger = logging.getLogger('ngrok_service')
logger.setLevel(logging.INFO)

# Aggiungi handler per console se non già presente
if not logger.handlers:
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(console_handler)
    
    # Prova ad aggiungere anche un file handler
    try:
        log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        file_handler = logging.FileHandler(os.path.join(log_dir, 'ngrok_service.log'))
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        logger.addHandler(file_handler)
    except Exception as e:
        logger.warning(f"Impossibile configurare il log su file: {e}")

# Importazione condizionale di pyngrok
try:
    from pyngrok import ngrok, conf, exception
    HAS_NGROK = True
    
    # Log della versione di pyngrok
    logger.info(f"pyngrok versione: {ngrok.__version__}")
except ImportError:
    HAS_NGROK = False
    logger.warning("pyngrok non trovato. Il servizio di tunneling remoto non sarà disponibile.")
except Exception as e:
    HAS_NGROK = False
    logger.error(f"Errore nell'importazione di pyngrok: {e}")

class NgrokMonitor(QThread):
    """
    Thread dedicato al monitoraggio dello stato del tunnel ngrok
    Emette segnali quando rileva problemi o cambiamenti nello stato
    """
    status_changed = pyqtSignal(dict)  # Emette lo stato aggiornato
    tunnel_error = pyqtSignal(str)     # Emette messaggi di errore
    
    def __init__(self, check_interval=10):
        """
        Inizializza il monitor ngrok
        
        Args:
            check_interval: Intervallo in secondi tra i controlli
        """
        super().__init__()
        self.check_interval = check_interval
        self.running = False
        self.last_status = None
    
    def run(self):
        """Esecuzione principale del thread di monitoraggio"""
        if not HAS_NGROK:
            self.tunnel_error.emit("pyngrok non installato")
            return
            
        self.running = True
        logger.info(f"Avvio monitoraggio ngrok (intervallo: {self.check_interval}s)")
        
        while self.running:
            try:
                # Ottieni lo stato attuale dei tunnel
                tunnels = ngrok.get_tunnels()
                
                # Crea dizionario con informazioni sui tunnel
                status = {
                    "timestamp": time.time(),
                    "tunnels": [],
                    "count": len(tunnels),
                    "healthy": True
                }
                
                # Aggiungi dettagli di ogni tunnel
                for tunnel in tunnels:
                    tunnel_info = {
                        "public_url": tunnel.public_url,
                        "proto": tunnel.proto,
                        "name": tunnel.name,
                        "config": tunnel.config
                    }
                    status["tunnels"].append(tunnel_info)
                
                # Emetti il segnale di aggiornamento stato solo se è cambiato
                if status != self.last_status:
                    logger.debug(f"Stato ngrok aggiornato: {json.dumps(status)}")
                    self.status_changed.emit(status)
                    self.last_status = status
                
            except exception.PyngrokNgrokError as e:
                # Errore specifico di ngrok
                error_msg = f"Errore ngrok: {str(e)}"
                logger.error(error_msg)
                self.tunnel_error.emit(error_msg)
                
                # Prova a riconnettersi dopo un errore
                time.sleep(self.check_interval * 2)
                
            except Exception as e:
                # Errore generico
                error_msg = f"Errore nel monitoraggio ngrok: {str(e)}"
                logger.error(error_msg)
                self.tunnel_error.emit(error_msg)
            
            # Pausa tra i controlli
            for _ in range(self.check_interval):
                if not self.running:
                    break
                time.sleep(1)
        
        logger.info("Monitoraggio ngrok terminato")
    
    def stop(self):
        """Ferma il thread di monitoraggio"""
        self.running = False


class NgrokService(QObject):
    """Servizio completo per gestire il tunneling ngrok"""
    
    # Segnali emessi dal servizio
    tunnel_started = pyqtSignal(str)    # URL pubblico
    tunnel_stopped = pyqtSignal()
    tunnel_error = pyqtSignal(str)      # Messaggio d'errore
    tunnel_status = pyqtSignal(dict)    # Stato completo
    
    def __init__(self, http_port=3000):
        """
        Inizializza il servizio ngrok
        
        Args:
            http_port: Porta HTTP del server da esporre
        """
        super().__init__()
        self.http_port = http_port
        self.tunnel = None
        self.public_url = None
        self.is_running = False
        self.ngrok_thread = None
        self.monitor = None
        self.config_file = None
        
        # Crea directory per i file temporanei se non esiste
        self.temp_dir = os.path.join(tempfile.gettempdir(), 'poker_timer_ngrok')
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)
        
        # Inizializza il monitor
        self._setup_monitor()
        
        logger.info(f"Servizio ngrok inizializzato (porta HTTP: {http_port})")
    
    def _setup_monitor(self):
        """Configura il monitor dello stato ngrok"""
        if not HAS_NGROK:
            return
            
        self.monitor = NgrokMonitor()
        self.monitor.status_changed.connect(self._on_status_changed)
        self.monitor.tunnel_error.connect(self._on_monitor_error)
    
    def _on_status_changed(self, status):
        """Gestisce i cambiamenti di stato rilevati dal monitor"""
        # Emetti il segnale di stato
        self.tunnel_status.emit(status)
        
        # Verifica se ci sono tunnel attivi
        if status["count"] == 0 and self.is_running:
            logger.warning("Il monitor ha rilevato che non ci sono più tunnel attivi")
            self._handle_tunnel_closed()
    
    def _on_monitor_error(self, error_msg):
        """Gestisce gli errori rilevati dal monitor"""
        logger.error(f"Errore rilevato dal monitor: {error_msg}")
        
        # Se c'è un errore ma pensiamo di essere ancora attivi, verifica lo stato
        if self.is_running:
            self._verify_tunnel_status()
    
    def _verify_tunnel_status(self):
        """Verifica lo stato del tunnel e aggiorna di conseguenza"""
        if not HAS_NGROK:
            return
            
        try:
            # Ottieni i tunnel attivi
            tunnels = ngrok.get_tunnels()
            
            # Se non ci sono tunnel ma pensiamo di essere attivi, c'è un problema
            if not tunnels and self.is_running:
                logger.warning("Stato inconsistente: ngrok service attivo ma nessun tunnel trovato")
                self._handle_tunnel_closed()
            
            # Se ci sono tunnel ma pensiamo di essere inattivi, aggiorna lo stato
            elif tunnels and not self.is_running:
                logger.info("Stato inconsistente: ngrok service inattivo ma tunnel trovati")
                
                # Trova il tunnel che corrisponde alla nostra porta
                for tunnel in tunnels:
                    if str(self.http_port) in tunnel.config['addr']:
                        self.tunnel = tunnel
                        self.public_url = tunnel.public_url
                        self.is_running = True
                        
                        # Converti da http a https se necessario
                        if self.public_url.startswith("http://"):
                            self.public_url = "https://" + self.public_url[7:]
                        
                        logger.info(f"Tunnel ripristinato: {self.public_url}")
                        self.tunnel_started.emit(self.public_url)
                        break
        
        except Exception as e:
            logger.error(f"Errore nella verifica dello stato del tunnel: {e}")
    
    def _handle_tunnel_closed(self):
        """Gestisce la chiusura inaspettata del tunnel"""
        logger.warning("Tunnel chiuso inaspettatamente")
        
        # Resetta lo stato
        self.tunnel = None
        self.public_url = None
        self.is_running = False
        
        # Emetti il segnale
        self.tunnel_stopped.emit()
    
    def _create_config_file(self, authtoken=None):
        """
        Crea un file di configurazione temporaneo per ngrok
        
        Args:
            authtoken: Token di autenticazione ngrok
        
        Returns:
            str: Percorso del file di configurazione
        """
        config = {
            "version": "2",
            "log_level": "info",
            "log_format": "json"
        }
        
        if authtoken:
            config["authtoken"] = authtoken
        
        # Aggiunta impostazioni specifiche per i tunnel HTTP
        config["tunnels"] = {
            "poker_timer_http": {
                "proto": "http",
                "addr": f"http://localhost:{self.http_port}",
                "inspect": False
            }
        }
        
        # Crea il file di configurazione
        config_path = os.path.join(self.temp_dir, 'ngrok_config.yml')
        
        try:
            with open(config_path, 'w') as f:
                # Per il formato YAML
                f.write("version: 2\n")
                f.write(f"authtoken: {authtoken}\n") if authtoken else None
                f.write("log_level: info\n")
                f.write("log_format: json\n")
                f.write("tunnels:\n")
                f.write("  poker_timer_http:\n")
                f.write("    proto: http\n")
                f.write(f"    addr: http://localhost:{self.http_port}\n")
                f.write("    inspect: false\n")
            
            logger.info(f"File di configurazione ngrok creato: {config_path}")
            return config_path
        
        except Exception as e:
            logger.error(f"Errore nella creazione del file di configurazione: {e}")
            return None
    
    def start_tunnel(self, authtoken=None):
        """
        Avvia il tunnel ngrok
        
        Args:
            authtoken: Token di autenticazione ngrok
        
        Returns:
            bool: True se l'avvio è stato avviato con successo, False altrimenti
        """
        if not HAS_NGROK:
            self.tunnel_error.emit("Pacchetto pyngrok non installato. Esegui: pip install pyngrok")
            return False
        
        # Se il tunnel è già attivo, non fare nulla
        if self.is_running:
            logger.info("Il tunnel è già attivo")
            return True
        
        # Crea un file di configurazione personalizzato
        self.config_file = self._create_config_file(authtoken)
        
        # Avvia in un thread separato per non bloccare l'UI
        self.ngrok_thread = threading.Thread(target=self._start_tunnel_thread)
        self.ngrok_thread.daemon = True
        self.ngrok_thread.start()
        
        # Avvia il monitor se non è già attivo
        if self.monitor and not self.monitor.isRunning():
            self.monitor.start()
        
        return True
    
    def _start_tunnel_thread(self):
        """Thread interno per avviare ngrok"""
        try:
            # Configura il token di autenticazione se fornito
            if self.config_file:
                # Carica la configurazione dal file
                conf.get_default().config_path = self.config_file
                conf.get_default().log_format = "json"
                logger.info(f"Utilizzo configurazione da file: {self.config_file}")
            
            # Chiudi eventuali tunnel esistenti
            ngrok.kill()
            
            # Attendi che i tunnel siano effettivamente chiusi
            time.sleep(1)
            
            # Avvia un nuovo tunnel
            logger.info(f"Avvio tunnel ngrok sulla porta {self.http_port}")
            
            # Usa connect con nome specifico
            self.tunnel = ngrok.connect(
                addr=f"http://localhost:{self.http_port}",
                proto="http",
                name="poker_timer_http"
            )
            
            self.public_url = self.tunnel.public_url
            
            # Converti da http a https se necessario
            if self.public_url.startswith("http://"):
                self.public_url = "https://" + self.public_url[7:]
            
            logger.info(f"Tunnel ngrok avviato: {self.public_url}")
            self.is_running = True
            
            # Emetti il segnale con l'URL pubblico
            self.tunnel_started.emit(self.public_url)
            
        except exception.PyngrokNgrokError as e:
            # Errore specifico di ngrok
            error_msg = f"Errore ngrok: {str(e)}"
            logger.error(error_msg)
            self.tunnel_error.emit(error_msg)
            self.is_running = False
            
        except Exception as e:
            # Errore generico
            error_msg = f"Errore nell'avvio del tunnel ngrok: {str(e)}"
            logger.error(error_msg)
            self.tunnel_error.emit(error_msg)
            self.is_running = False
    
    def stop_tunnel(self):
        """
        Ferma il tunnel ngrok
        
        Returns:
            bool: True se l'operazione di arresto è stata avviata, False altrimenti
        """
        if not HAS_NGROK:
            return False
        
        # Se il tunnel non è attivo, non fare nulla
        if not self.is_running:
            logger.info("Il tunnel non è attivo")
            return True
        
        # Esegui in un thread separato per non bloccare l'UI
        threading.Thread(target=self._stop_tunnel_thread).start()
        return True
    
    def _stop_tunnel_thread(self):
        """Thread interno per fermare ngrok"""
        try:
            self.is_running = False
            logger.info("Chiusura tunnel ngrok in corso")
            
            # Ferma il monitor
            if self.monitor and self.monitor.isRunning():
                self.monitor.stop()
                self.monitor.wait()
            
            # Disconnetti il tunnel specifico
            if self.tunnel:
                try:
                    ngrok.disconnect(self.tunnel.public_url)
                except:
                    pass
                self.tunnel = None
                self.public_url = None
            
            # Per sicurezza, termina tutti i processi ngrok
            ngrok.kill()
            
            logger.info("Tunnel ngrok fermato")
            
            # Emetti il segnale
            self.tunnel_stopped.emit()
            
        except Exception as e:
            logger.error(f"Errore nella chiusura del tunnel ngrok: {e}")
            self.tunnel_error.emit(f"Errore nella chiusura del tunnel: {str(e)}")
    
    def get_status(self):
        """
        Restituisce lo stato corrente del tunnel
        
        Returns:
            dict: Stato completo del tunnel
        """
        if not HAS_NGROK:
            return {
                "running": False,
                "error": "pyngrok non installato"
            }
        
        try:
            # Controlla lo stato effettivo dei tunnel
            tunnels = ngrok.get_tunnels()
            
            # Se non ci sono tunnel ma pensiamo di essere attivi, correggi lo stato
            if not tunnels and self.is_running:
                self._handle_tunnel_closed()
            
            status = {
                "running": self.is_running,
                "public_url": self.public_url,
                "tunnels_count": len(tunnels),
                "tunnels": []
            }
            
            # Aggiungi informazioni sui tunnel attivi
            for tunnel in tunnels:
                status["tunnels"].append({
                    "public_url": tunnel.public_url,
                    "proto": tunnel.proto,
                    "name": tunnel.name
                })
            
            return status
            
        except Exception as e:
            logger.error(f"Errore nel recupero dello stato: {e}")
            
            return {
                "running": self.is_running,
                "public_url": self.public_url,
                "error": str(e)
            }
    
    def restart_tunnel(self, authtoken=None):
        """
        Riavvia il tunnel ngrok
        
        Args:
            authtoken: Token di autenticazione ngrok (opzionale)
        
        Returns:
            bool: True se l'operazione di riavvio è stata avviata, False altrimenti
        """
        # Ferma il tunnel
        if self.is_running:
            self.stop_tunnel()
            
            # Attendi che il tunnel sia effettivamente fermato
            for _ in range(10):  # Massimo 5 secondi di attesa
                if not self.is_running:
                    break
                time.sleep(0.5)
        
        # Avvia un nuovo tunnel
        return self.start_tunnel(authtoken)
    
    def cleanup(self):
        """
        Pulisce le risorse del servizio
        Da chiamare quando l'applicazione viene chiusa
        """
        # Ferma il tunnel
        if self.is_running:
            self.stop_tunnel()
        
        # Ferma il monitor
        if self.monitor and self.monitor.isRunning():
            self.monitor.stop()
            self.monitor.wait()
        
        # Rimuovi i file temporanei
        try:
            if self.config_file and os.path.exists(self.config_file):
                os.remove(self.config_file)
                logger.info(f"File di configurazione rimosso: {self.config_file}")
        except Exception as e:
            logger.error(f"Errore nella rimozione del file di configurazione: {e}")


class NgrokTunnelInfo:
    """Classe per analizzare e formattare le informazioni sul tunnel ngrok"""
    
    @staticmethod
    def get_readable_url(url):
        """
        Estrae il dominio dall'URL del tunnel in un formato leggibile
        
        Args:
            url: URL completo del tunnel
        
        Returns:
            str: Dominio leggibile
        """
        if not url:
            return "N/A"
        
        # Rimuovi il protocollo
        domain = url.replace("https://", "").replace("http://", "")
        
        # Rimuovi la porta e il percorso
        domain = domain.split(":")[0].split("/")[0]
        
        return domain
    
    @staticmethod
    def get_tunnel_info(tunnel):
        """
        Estrae le informazioni principali dal tunnel
        
        Args:
            tunnel: Oggetto tunnel ngrok
        
        Returns:
            dict: Informazioni principali sul tunnel
        """
        if not tunnel:
            return None
            
        return {
            "url": tunnel.public_url,
            "domain": NgrokTunnelInfo.get_readable_url(tunnel.public_url),
            "proto": tunnel.proto,
            "name": tunnel.name
        }
    
    @staticmethod
    def format_url_for_qr(url):
        """
        Formatta l'URL per il QR code
        
        Args:
            url: URL del tunnel
        
        Returns:
            str: URL formattato
        """
        if not url:
            return None
            
        # Assicurati che l'URL sia https
        if url.startswith("http://"):
            url = "https://" + url[7:]
            
        # Rimuovi eventuali slash finali
        if url.endswith("/"):
            url = url[:-1]
            
        return url