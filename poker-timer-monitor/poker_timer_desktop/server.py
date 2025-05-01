#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Poker Timer Server - Backend per l'applicazione desktop
"""

import os
import sys
import time
import datetime
import threading
import socket
import logging
import json
from PyQt6.QtCore import QObject, pyqtSignal

# Configura il logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('poker_timer')

# Cerca di importare Flask
try:
    from flask import Flask, request, jsonify, send_from_directory, Response
except ImportError:
    print("Flask non trovato. Installazione in corso...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "flask"])
    from flask import Flask, request, jsonify, send_from_directory, Response

class PokerTimerServer(QObject):
    """Server per il Poker Timer con segnali Qt"""
    # Segnali per la comunicazione con l'interfaccia
    timer_updated = pyqtSignal(str)  # Emesso quando un timer viene aggiornato
    timer_connected = pyqtSignal(str)  # Emesso quando un nuovo timer si connette
    seat_notification = pyqtSignal(str, list)  # Emesso quando arriva una notifica di posti
    
    def __init__(self, port=3000, discovery_port=8888):
        super().__init__()
        self.port = port
        self.discovery_port = discovery_port
        self.start_time = time.time()
        
        # Inizializza l'app Flask
        self.app = Flask(__name__)
        
        # Memorizza lo stato dei timer
        self.timers = {}
        
        # Thread per il servizio di discovery UDP
        self.discovery_thread = None
        self.discovery_running = False
        self.udp_socket = None
        
        # Thread per il server HTTP
        self.server_thread = None
        
        # Configurazione delle route per l'API
        self.setup_routes()
        
        logger.info(f"Poker Timer Server inizializzato (porta HTTP: {port}, porta discovery: {discovery_port})")
    
    def setup_routes(self):
        """Configura le route API del server Flask"""
        
        # API per ottenere informazioni sul server
        @self.app.route('/api/server-info')
        def server_info():
            uptime = time.time() - self.start_time
            return jsonify({
                "name": "Poker Timer Server (Python)",
                "version": "1.0",
                "port": self.port,
                "uptime": uptime
            })
        
        # API per ottenere tutti i timer
        @self.app.route('/api/timers')
        def get_timers():
            return jsonify(self.timers)
        
        # API per cancellare tutti i timer
        @self.app.route('/api/timers', methods=['DELETE'])
        def delete_timers():
            timer_count = len(self.timers)
            self.timers.clear()
            logger.info(f"Cancellati {timer_count} timer")
            return jsonify({
                "status": "success",
                "message": f"{timer_count} timer cancellati con successo"
            })
        
        # API per aggiornare lo stato di un timer
        @self.app.route('/api/status', methods=['POST'])
        def update_status():
            timer_data = request.json
            device_id = timer_data.get('device_id')
            
            if not device_id:
                return jsonify({"error": "Missing device_id"}), 400
            
            logger.info(f"Ricevuto aggiornamento da {device_id}")
            
            # Aggiorna timestamp e indirizzo IP
            timer_data['last_update'] = datetime.datetime.now().isoformat()
            timer_data['ip_address'] = request.remote_addr
            
            # Verifica se è un nuovo timer
            is_new = device_id not in self.timers
            
            # Memorizza lo stato aggiornato
            if device_id in self.timers:
                self.timers[device_id].update(timer_data)
            else:
                self.timers[device_id] = timer_data
                logger.info(f"Nuovo timer registrato: {device_id}")
            
            # Emetti il segnale appropriato
            if is_new:
                self.timer_connected.emit(device_id)
            else:
                self.timer_updated.emit(device_id)
            
            # Controlla se ci sono comandi in sospeso
            response_data = {"status": "ok"}
            
            if 'pending_command' in self.timers[device_id]:
                response_data['command'] = self.timers[device_id]['pending_command']
                
                if self.timers[device_id]['pending_command'] in ['settings', 'apply_settings']:
                    if 'pending_settings' in self.timers[device_id]:
                        response_data['settings'] = self.timers[device_id]['pending_settings']
                        logger.info(f"Invio nuove impostazioni a {device_id}: {self.timers[device_id]['pending_settings']}")
                
                # Rimuovi il comando pendente
                logger.info(f"Inviato comando {self.timers[device_id]['pending_command']} a {device_id}")
                del self.timers[device_id]['pending_command']
                if 'pending_settings' in self.timers[device_id]:
                    del self.timers[device_id]['pending_settings']
            
            # Controlla se c'è una richiesta di posti da comunicare
            if 'seat_info' in self.timers[device_id] and self.timers[device_id].get('seat_info', {}).get('needs_web_notification'):
                seats = self.timers[device_id]['seat_info']['open_seats']
                table_num = self.timers[device_id].get('table_number', 0)
                
                # Emetti segnale per notifica desktop
                self.seat_notification.emit(str(table_num), seats)
                
                response_data['seat_request'] = {
                    "open_seats": seats,
                    "action": self.timers[device_id]['seat_info'].get('action', 'seat_open')
                }
                
                # Resetta il flag
                self.timers[device_id]['seat_info']['needs_web_notification'] = False
            
            return jsonify(response_data)
        
        # API per salvare le impostazioni di un timer
        @self.app.route('/api/settings/<device_id>', methods=['POST'])
        def save_settings(device_id):
            settings = request.json
            
            logger.info(f"Ricevute impostazioni per {device_id}: {settings}")
            
            # Crea il timer se non esiste
            if device_id not in self.timers:
                self.timers[device_id] = {}
            
            # Aggiorna i valori specifici del timer
            self.timers[device_id]['mode'] = settings.get('mode')
            self.timers[device_id]['t1_value'] = settings.get('t1')
            self.timers[device_id]['t2_value'] = settings.get('t2')
            self.timers[device_id]['table_number'] = settings.get('tableNumber')
            self.timers[device_id]['buzzer'] = settings.get('buzzer')
            self.timers[device_id]['players_count'] = settings.get('playersCount')
            
            # Imposta il comando in sospeso
            self.timers[device_id]['pending_command'] = "settings"
            self.timers[device_id]['pending_settings'] = settings
            
            # Emetti il segnale per aggiornare l'interfaccia
            self.timer_updated.emit(device_id)
            
            return jsonify({
                "status": "settings_queued",
                "settings": settings
            })
        
        # API per inviare comandi a un timer
        @self.app.route('/api/command/<device_id>', methods=['POST'])
        def send_command_api(device_id):
            command_data = request.json
            command = command_data.get('command')
            
            logger.info(f"Ricevuto comando {command} per {device_id}")
            
            if not command:
                return jsonify({"error": "Missing command"}), 400
            
            if device_id not in self.timers:
                return jsonify({"error": "Timer not found"}), 404
            
            # Gestisci il comando reset_seat_info
            if command == "reset_seat_info":
                logger.info(f"Reset seat info per device {device_id}")
                
                if 'seat_info' in self.timers[device_id]:
                    del self.timers[device_id]['seat_info']
                    logger.info(f"Informazioni sui posti rimosse per device {device_id}")
                
                # Emetti il segnale per aggiornare l'interfaccia
                self.timer_updated.emit(device_id)
                
                return jsonify({"status": "success", "command": command})
            
            # Imposta il comando in sospeso
            self.timers[device_id]['pending_command'] = command
            
            return jsonify({"status": "command_queued", "command": command})
        
        # API per gestire le richieste di posti liberi
        @self.app.route('/api/seat_request', methods=['POST'])
        def seat_request():
            request_data = request.json
            table_number = request_data.get('table_number')
            seats = request_data.get('seats', [])
            
            logger.info(f"Ricevuta richiesta posti per tavolo {table_number}")
            logger.info(f"Posti: {', '.join(map(str, seats))}")
            
            # Cerca il dispositivo corrispondente a questo tavolo
            target_device_id = None
            for device_id, timer in self.timers.items():
                if timer.get('table_number') == table_number:
                    target_device_id = device_id
                    break
            
            if target_device_id:
                # Memorizza i dati dei posti nella struttura del timer
                if 'seat_info' not in self.timers[target_device_id]:
                    self.timers[target_device_id]['seat_info'] = {}
                
                self.timers[target_device_id]['seat_info'] = {
                    'open_seats': seats,
                    'timestamp': datetime.datetime.now().isoformat(),
                    'action': request_data.get('action', 'seat_open'),
                    'needs_web_notification': True
                }
                
                # Emetti il segnale per la notifica
                self.seat_notification.emit(str(table_number), seats)
                
                # Emetti il segnale per aggiornare l'interfaccia
                self.timer_updated.emit(target_device_id)
                
                return jsonify({
                    "status": "success",
                    "message": f"Seat request for table {table_number} processed successfully"
                })
            else:
                return jsonify({
                    "status": "error",
                    "message": f"No device found for table {table_number}"
                }), 404
    
    def run_discovery_service(self):
        """Esegue il servizio di discovery UDP per consentire ai client di trovare il server"""
        self.discovery_running = True
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            self.udp_socket.bind(('', self.discovery_port))
            logger.info(f"Servizio discovery in ascolto sulla porta UDP {self.discovery_port}")
            
            # Imposta il socket per il broadcast
            self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            
            while self.discovery_running:
                try:
                    data, addr = self.udp_socket.recvfrom(1024)
                    message = data.decode('utf-8').strip()
                    
                    logger.info(f"Richiesta discovery ricevuta: {message} da {addr[0]}:{addr[1]}")
                    
                    # Verifica che sia una richiesta di discovery del Poker Timer
                    if message == "POKER_TIMER_DISCOVERY":
                        logger.info(f"Invio risposta discovery a {addr[0]}:{addr[1]}")
                        
                        # Invia una risposta con le informazioni del server
                        response = "POKER_TIMER_SERVER".encode('utf-8')
                        
                        # Prima risposta immediata
                        self.udp_socket.sendto(response, addr)
                        logger.info(f"Prima risposta discovery inviata con successo a {addr[0]}:{addr[1]}")
                        
                        # Seconda risposta dopo 100ms per aumentare le probabilità di ricezione
                        time.sleep(0.1)
                        self.udp_socket.sendto(response, addr)
                        logger.info(f"Seconda risposta discovery inviata con successo a {addr[0]}:{addr[1]}")
                        
                except Exception as e:
                    logger.error(f"Errore nel servizio discovery: {e}")
                    # Continua l'esecuzione anche in caso di errore
        
        except Exception as e:
            logger.error(f"Errore nell'inizializzazione del servizio discovery: {e}")
        finally:
            if self.udp_socket:
                self.udp_socket.close()
                logger.info("Socket discovery chiuso")
    
    def start_discovery_service(self):
        """Avvia il servizio di discovery in un thread separato"""
        self.discovery_thread = threading.Thread(target=self.run_discovery_service)
        self.discovery_thread.daemon = True
        self.discovery_thread.start()
        logger.info("Thread del servizio discovery avviato")
    
    def stop_discovery_service(self):
        """Ferma il servizio di discovery"""
        self.discovery_running = False
        if self.udp_socket:
            try:
                # Chiudi il socket per interrompere il recvfrom
                self.udp_socket.close()
            except Exception as e:
                logger.error(f"Errore nella chiusura del socket discovery: {e}")
        
        if self.discovery_thread and self.discovery_thread.is_alive():
            try:
                self.discovery_thread.join(timeout=1.0)  # Attendi al massimo 1 secondo
            except Exception as e:
                logger.error(f"Errore nell'arresto del thread discovery: {e}")
        
        logger.info("Servizio discovery fermato")
    
    def start_server(self):
        """Avvia il server Flask in un thread separato"""
        def run_flask():
            self.app.run(host='0.0.0.0', port=self.port, debug=False, use_reloader=False)
        
        self.server_thread = threading.Thread(target=run_flask)
        self.server_thread.daemon = True
        self.server_thread.start()
        logger.info(f"Server Flask avviato su porta {self.port}")
    
    def start(self):
        """Avvia il server e il servizio di discovery"""
        self.start_time = time.time()
        self.start_discovery_service()
        self.start_server()
        logger.info("Server Poker Timer avviato completamente")
    
    def stop(self):
        """Ferma il server"""
        self.stop_discovery_service()
        # Il server Flask non può essere fermato facilmente, ma essendo in un thread
        # demone, terminerà quando l'applicazione si chiude
        logger.info("Server Poker Timer fermato")
    
    def send_command(self, device_id, command):
        """Invia un comando a un timer specifico"""
        if device_id not in self.timers:
            logger.error(f"Timer {device_id} non trovato")
            return False
        
        logger.info(f"Invio comando {command} a {device_id}")
        self.timers[device_id]['pending_command'] = command
        
        # La risposta effettiva avverrà quando il timer invierà la prossima richiesta
        return True
    
    def reset_seat_info(self, device_id):
        """Resetta le informazioni sui posti per un timer"""
        if device_id not in self.timers:
            return False
        
        if 'seat_info' in self.timers[device_id]:
            del self.timers[device_id]['seat_info']
            logger.info(f"Informazioni sui posti rimosse per device {device_id}")
            self.timer_updated.emit(device_id)
            return True
        
        return False
    
    def update_settings(self, device_id, settings):
        """Aggiorna le impostazioni di un timer"""
        if device_id not in self.timers:
            self.timers[device_id] = {}
        
        # Aggiorna i valori specifici del timer
        self.timers[device_id]['mode'] = settings.get('mode')
        self.timers[device_id]['t1_value'] = settings.get('t1')
        self.timers[device_id]['t2_value'] = settings.get('t2')
        self.timers[device_id]['table_number'] = settings.get('tableNumber')
        self.timers[device_id]['buzzer'] = settings.get('buzzer')
        self.timers[device_id]['players_count'] = settings.get('playersCount')
        
        # Imposta il comando in sospeso
        self.timers[device_id]['pending_command'] = "settings"
        self.timers[device_id]['pending_settings'] = settings
        
        # Emetti il segnale per aggiornare l'interfaccia
        self.timer_updated.emit(device_id)
        
        return True
    
    def is_timer_online(self, timer_data):
        """Controlla se un timer è considerato online in base al timestamp"""
        try:
            last_update = datetime.datetime.fromisoformat(timer_data.get('last_update', ''))
            now = datetime.datetime.now()
            # Timer considerato online se aggiornato negli ultimi 10 secondi
            return (now - last_update).total_seconds() < 10
        except Exception:
            return False