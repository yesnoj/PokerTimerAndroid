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
    floorman_notification = pyqtSignal(int)  # Emesso quando arriva una chiamata floorman
    bar_service_notification = pyqtSignal(int)  # Emesso quando arriva una richiesta servizio bar
    
    def __init__(self, port=3000, discovery_port=8888):
        super().__init__()
        self.port = port
        self.discovery_port = discovery_port
        self.start_time = time.time()
        
        # Inizializza l'app Flask
        self.app = Flask(__name__)
        
        # Memorizza lo stato dei timer
        self.timers = {}
        
        # Memorizza le richieste bar
        self.bar_requests = []
        
        # Thread per il servizio di discovery UDP
        self.discovery_thread = None
        self.discovery_running = False
        self.udp_socket = None
        
        # Thread per il server HTTP
        self.server_thread = None
        
        # Configurazione delle route per l'API
        self.setup_routes()
        
        logger.info(f"Poker Timer Server inizializzato (porta HTTP: {port}, porta discovery: {discovery_port})")
    

    def calculate_wifi_quality(self, wifi_signal):
        """Converte il valore wifi_signal in una percentuale di qualità"""
        if wifi_signal is None:
            return 100  # Default alto per i dispositivi Android
        
        # Per i segnali WiFi, tipicamente:
        # -30 dBm è eccellente (100%)
        # -67 dBm è il limite per applicazioni affidabili (~70%)
        # -70 dBm è il minimo per connessioni di base (~40%)
        # -80 dBm è il minimo utilizzabile (~20%)
        # -90 dBm è praticamente inutilizzabile (0%)
        
        signal = abs(wifi_signal)  # Usiamo il valore assoluto per facilitare il calcolo
        if signal <= 30:
            return 100
        elif signal >= 90:
            return 0
        else:
            # Calcolo lineare tra -30 e -90 dBm
            return max(0, min(100, 100 - ((signal - 30) * 100 / 60)))

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
        
        @self.app.route('/api/floorman_request', methods=['POST'])
        def floorman_request():
            request_data = request.json
            table_number = request_data.get('table_number')
            
            logger.info(f"Ricevuta chiamata floorman dal tavolo {table_number}")
            
            # Trova il dispositivo corrispondente a questo tavolo
            target_device_id = None
            for device_id, timer in self.timers.items():
                if timer.get('table_number') == table_number:
                    target_device_id = device_id
                    break
            
            if target_device_id:
                # Aggiungi il timestamp della chiamata floorman
                self.timers[target_device_id]['floorman_call_timestamp'] = int(time.time() * 1000)  # timestamp in millisecondi
                
                # Emetti il segnale per aggiornare l'interfaccia
                self.timer_updated.emit(target_device_id)
            
            # Emetti il segnale per la notifica
            self.floorman_notification.emit(table_number)
            
            return jsonify({
                "status": "success",
                "message": f"Floorman chiamato per tavolo {table_number}"
            })

        # API per cancellare una richiesta floorman
        @self.app.route('/api/floorman_request/<int:table_number>', methods=['DELETE'])
        def clear_floorman_request(table_number):
            """Cancella una richiesta floorman per un tavolo specifico"""
            logger.info(f"Richiesta cancellazione floorman per tavolo {table_number}")
            
            # Trova il timer corrispondente
            cleared = False
            for device_id, timer in self.timers.items():
                if timer.get('table_number') == table_number:
                    if 'floorman_request' in timer:
                        del timer['floorman_request']
                        cleared = True
                        # Emetti segnale di aggiornamento
                        self.timer_updated.emit(device_id)
                        logger.info(f"Richiesta floorman cancellata per tavolo {table_number}")
                        break
            
            if cleared:
                return jsonify({
                    "status": "success",
                    "message": f"Richiesta floorman cancellata per tavolo {table_number}"
                })
            else:
                return jsonify({
                    "status": "error",
                    "message": f"Nessuna richiesta floorman trovata per tavolo {table_number}"
                }), 404

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
            
            # Calcola wifi_quality se wifi_signal è disponibile
            if 'wifi_signal' in timer_data:
                timer_data['wifi_quality'] = self.calculate_wifi_quality(timer_data['wifi_signal'])
                logger.info(f"Calcolato wifi_quality={timer_data['wifi_quality']} da wifi_signal={timer_data['wifi_signal']} per {device_id}")
            elif device_id.startswith('android_'):
                # Per i dispositivi Android, aggiungiamo una qualità WiFi variabile
                import random
                quality = random.randint(60, 100)
                timer_data['wifi_quality'] = quality
                logger.info(f"Impostato wifi_quality simulato={quality} per dispositivo Android {device_id}")
            
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
        
        @self.app.route('/api/command/<device_id>', methods=['POST'])
        def send_command_api(device_id):
            command_data = request.json
            command = command_data.get('command')
            
            logger.info(f"Ricevuto comando {command} per {device_id}")
            
            if not command:
                return jsonify({"error": "Missing command"}), 400
            
            if device_id not in self.timers:
                return jsonify({"error": "Timer not found"}), 404
            
            # Gestisci il comando clear_floorman
            if command == "clear_floorman":
                logger.info(f"Cancellazione chiamata floorman per device {device_id}")
                
                if 'floorman_call_timestamp' in self.timers[device_id]:
                    del self.timers[device_id]['floorman_call_timestamp']
                    logger.info(f"Timestamp floorman rimosso per device {device_id}")
                
                # Emetti il segnale per aggiornare l'interfaccia
                self.timer_updated.emit(device_id)
                
                return jsonify({"status": "success", "command": command})
            
            # Gestisci il comando reset_seat_info (già esistente)
            elif command == "reset_seat_info":
                logger.info(f"Reset seat info per device {device_id}")
                
                if 'seat_info' in self.timers[device_id]:
                    del self.timers[device_id]['seat_info']
                    logger.info(f"Informazioni sui posti rimosse per device {device_id}")
                
                # Emetti il segnale per aggiornare l'interfaccia
                self.timer_updated.emit(device_id)
                
                return jsonify({"status": "success", "command": command})
            
            # Altri comandi standard
            else:
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
                # Inizializza la struttura dei posti se non esiste
                if 'seat_info' not in self.timers[target_device_id]:
                    self.timers[target_device_id]['seat_info'] = {
                        'open_seats': [],
                        'timestamp': datetime.datetime.now().isoformat(),
                        'action': 'seat_open',
                        'needs_web_notification': False
                    }
                
                # Aggiungi i nuovi posti in coda all'elenco esistente (senza duplicati)
                for seat in seats:
                    if seat not in self.timers[target_device_id]['seat_info']['open_seats']:
                        self.timers[target_device_id]['seat_info']['open_seats'].append(seat)
                
                # Aggiorna le informazioni
                self.timers[target_device_id]['seat_info'].update({
                    'timestamp': datetime.datetime.now().isoformat(),
                    'action': request_data.get('action', 'seat_open'),
                })
                
                # Imposta il flag di notifica solo se non è già attivo
                # Questa modifica evita che vengano emessi più segnali in rapida successione
                if not self.timers[target_device_id]['seat_info'].get('needs_web_notification', False):
                    self.timers[target_device_id]['seat_info']['needs_web_notification'] = True
                    
                    # Emetti il segnale per la notifica
                    self.seat_notification.emit(str(table_number), self.timers[target_device_id]['seat_info']['open_seats'])
                
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
        

        @self.app.route('/bar-manager')
        def bar_manager_interface():
            """Fornisce un'interfaccia web per la gestione delle richieste bar"""
            
            # Recupera la lista delle richieste bar attive
            active_requests = self.bar_requests.copy()
            
            # Ordina le richieste per timestamp (più recenti in cima)
            active_requests.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
            
            # Crea la pagina HTML
            html_content = """
            <!DOCTYPE html>
            <html lang="it">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Gestione Richieste Bar</title>
                <style>
                    * {
                        box-sizing: border-box;
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    }
                    body {
                        background-color: #f5f5f5;
                        padding: 20px;
                        max-width: 1200px;
                        margin: 0 auto;
                        color: #333;
                    }
                    h1, h2 {
                        color: #2196F3;
                        text-align: center;
                    }
                    .dashboard {
                        display: grid;
                        grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
                        gap: 20px;
                        margin-top: 30px;
                    }
                    .request-card {
                        background-color: white;
                        border-radius: 10px;
                        padding: 20px;
                        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                        transition: all 0.3s ease;
                        position: relative;
                    }
                    .request-card:hover {
                        transform: translateY(-5px);
                        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
                    }
                    .table-number {
                        font-size: 24px;
                        font-weight: bold;
                        color: #FF9800;
                        margin-bottom: 15px;
                    }
                    .timestamp {
                        color: #757575;
                        font-size: 14px;
                        margin-bottom: 20px;
                    }
                    .source-tag {
                        position: absolute;
                        top: 15px;
                        right: 15px;
                        background-color: #E3F2FD;
                        color: #1976D2;
                        padding: 5px 10px;
                        border-radius: 15px;
                        font-size: 12px;
                        font-weight: bold;
                    }
                    .source-tag.qr {
                        background-color: #E8F5E9;
                        color: #388E3C;
                    }
                    .source-tag.app {
                        background-color: #FFF3E0;
                        color: #F57C00;
                    }
                    .complete-btn {
                        background-color: #4CAF50;
                        color: white;
                        border: none;
                        padding: 10px 15px;
                        border-radius: 5px;
                        cursor: pointer;
                        width: 100%;
                        font-size: 16px;
                        font-weight: bold;
                        transition: background-color 0.3s;
                    }
                    .complete-btn:hover {
                        background-color: #388E3C;
                    }
                    .empty-state {
                        text-align: center;
                        padding: 40px;
                        background-color: white;
                        border-radius: 10px;
                        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                    }
                    .empty-state-icon {
                        font-size: 60px;
                        margin-bottom: 20px;
                    }
                    .refresh-section {
                        text-align: center;
                        margin: 20px 0;
                    }
                    .refresh-btn {
                        background-color: #2196F3;
                        color: white;
                        border: none;
                        padding: 10px 20px;
                        border-radius: 5px;
                        cursor: pointer;
                        font-size: 16px;
                        transition: background-color 0.3s;
                    }
                    .refresh-btn:hover {
                        background-color: #1976D2;
                    }
                    .auto-refresh {
                        margin-top: 10px;
                        font-size: 14px;
                        color: #757575;
                    }
                    @media (max-width: 600px) {
                        .dashboard {
                            grid-template-columns: 1fr;
                        }
                    }
                </style>
            </head>
            <body>
                <h1>Gestione Richieste Bar</h1>
                
                <div class="refresh-section">
                    <button class="refresh-btn" onclick="window.location.reload()">Aggiorna</button>
                    <div class="auto-refresh">La pagina si aggiorna automaticamente ogni 15 secondi</div>
                </div>
            """
            
            # Aggiungi script per aggiornamento automatico
            html_content += """
                <script>
                    // Auto-refresh every 15 seconds
                    setTimeout(function() {
                        window.location.reload();
                    }, 15000);
                    
                    // Function to mark a request as complete
                    function completeRequest(requestId) {
                        fetch('/api/bar_requests/' + requestId + '/complete', {
                            method: 'POST'
                        })
                        .then(response => {
                            if (response.ok) {
                                // Remove the card
                                document.getElementById('request-' + requestId).remove();
                                
                                // Check if there are no more requests
                                if (document.querySelectorAll('.request-card').length === 0) {
                                    // Show empty state
                                    const dashboard = document.querySelector('.dashboard');
                                    dashboard.innerHTML = `
                                        <div class="empty-state">
                                            <div class="empty-state-icon">🍹</div>
                                            <h2>Nessuna richiesta attiva</h2>
                                            <p>Non ci sono richieste bar in attesa.</p>
                                        </div>
                                    `;
                                }
                            } else {
                                alert('Errore nel completamento della richiesta');
                            }
                        })
                        .catch(error => {
                            console.error('Error:', error);
                            alert('Errore di rete');
                        });
                    }
                </script>
            """
            
            # Sezione richieste
            html_content += '<div class="dashboard">'
            
            # Se non ci sono richieste, mostra lo stato vuoto
            if not active_requests:
                html_content += """
                    <div class="empty-state">
                        <div class="empty-state-icon">🍹</div>
                        <h2>Nessuna richiesta attiva</h2>
                        <p>Non ci sono richieste bar in attesa.</p>
                    </div>
                """
            else:
                # Aggiungi una card per ogni richiesta attiva
                for request in active_requests:
                    request_id = request.get('id', 'unknown')
                    table_number = request.get('table_number', 'N/A')
                    timestamp = request.get('timestamp', 0)
                    source = request.get('source', 'app')  # Default to 'app' if not specified
                    
                    # Converti il timestamp in formato leggibile
                    from datetime import datetime
                    readable_time = datetime.fromtimestamp(timestamp / 1000).strftime('%H:%M:%S')
                    
                    # Tag della sorgente
                    source_class = "qr" if source == "qr_code" else "app"
                    source_text = "QR Code" if source == "qr_code" else "App"
                    
                    html_content += f"""
                        <div class="request-card" id="request-{request_id}">
                            <div class="source-tag {source_class}">{source_text}</div>
                            <div class="table-number">Tavolo {table_number}</div>
                            <div class="timestamp">Richiesta alle {readable_time}</div>
                            <button class="complete-btn" onclick="completeRequest('{request_id}')">Completata</button>
                        </div>
                    """
            
            html_content += '</div></body></html>'
            
            return Response(html_content, mimetype='text/html')


        # Endpoint per gestire le richieste bar tramite scansione QR
        @self.app.route('/qr/bar-request/<int:table_number>')
        def qr_bar_request(table_number):
            """Gestisce le richieste bar provenienti dalla scansione di un codice QR"""
            
            # Log della richiesta
            logger.info(f"Ricevuta richiesta bar via QR per il tavolo {table_number}")
            
            # Trova il dispositivo corrispondente a questo tavolo
            target_device_id = None
            for device_id, timer in self.timers.items():
                if timer.get('table_number') == table_number:
                    target_device_id = device_id
                    break
            
            if target_device_id:
                # Aggiorna il timestamp della richiesta bar
                self.timers[target_device_id]['bar_service_timestamp'] = int(time.time() * 1000)  # timestamp in millisecondi
                
                # Emetti il segnale per aggiornare l'interfaccia
                self.timer_updated.emit(target_device_id)
            
            # Genera un ID univoco per la richiesta
            request_id = f"bar_qr_{table_number}_{int(time.time())}"
            
            # Aggiungi alla lista delle richieste
            bar_request = {
                "id": request_id,
                "table_number": table_number,
                "timestamp": int(time.time() * 1000),
                "source": "qr_code"  # Indica che la richiesta proviene da un codice QR
            }
            self.bar_requests.append(bar_request)
            
            # Emetti il segnale per la notifica
            #self.bar_service_notification.emit(table_number)
            
            # Determina se la richiesta proviene da un browser mobile
            user_agent = request.headers.get('User-Agent', '').lower()
            is_mobile = 'mobile' in user_agent or 'android' in user_agent or 'iphone' in user_agent or 'ipad' in user_agent
            
            # Pagina HTML di conferma migliorata (senza il bottone Stato Server)
            html_response = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Richiesta Bar Inviata</title>
                <style>
                    body {{
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        padding: 20px;
                        max-width: 500px;
                        margin: 0 auto;
                        text-align: center;
                        background-color: #f5f5f5;
                        color: #333;
                    }}
                    .container {{
                        background-color: white;
                        border-radius: 10px;
                        padding: 30px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    }}
                    h1 {{
                        color: #4CAF50;
                        margin-top: 0;
                    }}
                    .icon {{
                        font-size: 60px;
                        margin-bottom: 20px;
                        animation: bounce 1.5s ease infinite;
                    }}
                    .message {{
                        font-size: 18px;
                        margin-bottom: 30px;
                        line-height: 1.5;
                    }}
                    .table-number {{
                        font-weight: bold;
                        font-size: 24px;
                        color: #FF9800;
                    }}
                    .timer {{
                        margin-top: 20px;
                        font-size: 14px;
                        color: #777;
                    }}
                    .count {{
                        font-weight: bold;
                        color: #2196F3;
                    }}
                    .success-badge {{
                        display: inline-block;
                        background-color: #4CAF50;
                        color: white;
                        padding: 8px 16px;
                        border-radius: 20px;
                        font-weight: bold;
                        margin-bottom: 20px;
                        animation: fadeIn 0.5s ease;
                    }}
                    @keyframes fadeIn {{
                        from {{ opacity: 0; transform: translateY(-10px); }}
                        to {{ opacity: 1; transform: translateY(0); }}
                    }}
                    @keyframes bounce {{
                        0%, 20%, 50%, 80%, 100% {{ transform: translateY(0); }}
                        40% {{ transform: translateY(-20px); }}
                        60% {{ transform: translateY(-10px); }}
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="success-badge">Richiesta Inviata</div>
                    <div class="icon">🍹</div>
                    <h1>Il servizio bar è in arrivo!</h1>
                    <div class="message">
                        La tua richiesta per il tavolo <span class="table-number">{table_number}</span> è stata registrata.
                        <br><br>
                        Un addetto al servizio bar sarà da te al più presto.
                    </div>
                    <div class="timer">
                        Richiesta inviata alle <span class="count">{time.strftime('%H:%M:%S')}</span>
                    </div>
                </div>
                <script>
                    // Vibra il dispositivo mobile se supportato
                    if ('vibrate' in navigator) {{
                        navigator.vibrate(200);
                    }}
                    
                    // Auto-chiusura dopo 10 secondi per dispositivi mobili
                    if ({str(is_mobile).lower()}) {{
                        setTimeout(function() {{
                            // Mostra messaggio di chiusura
                            document.querySelector('.timer').innerHTML += '<br>Questa pagina si chiuderà automaticamente...';
                            
                            // Chiudi dopo un ulteriore secondo
                            setTimeout(function() {{
                                window.close();
                            }}, 1000);
                        }}, 10000);
                    }}
                </script>
            </body>
            </html>
            """
            
            return Response(html_response, mimetype='text/html')

        # Endpoint per la verifica dello stato del server (utile per testare che tutto funzioni)
        @self.app.route('/qr/status')
        def qr_status():
            """Mostra lo stato del server per il servizio QR"""
            
            # Conta le richieste bar attive
            active_requests = len(self.bar_requests)
            
            # Conta i timer online
            online_timers = 0
            for device_id, timer in self.timers.items():
                if self.is_timer_online(timer):
                    online_timers += 1
            
            uptime = time.time() - self.start_time
            uptime_hours = int(uptime // 3600)
            uptime_minutes = int((uptime % 3600) // 60)
            
            # Pagina HTML di stato
            html_response = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Stato Server QR Bar</title>
                <style>
                    body {{
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        padding: 20px;
                        max-width: 600px;
                        margin: 0 auto;
                        text-align: center;
                        background-color: #f5f5f5;
                        color: #333;
                    }}
                    .container {{
                        background-color: white;
                        border-radius: 10px;
                        padding: 30px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    }}
                    h1 {{
                        color: #2196F3;
                        margin-top: 0;
                    }}
                    .status-item {{
                        margin: 15px 0;
                        font-size: 18px;
                    }}
                    .status-value {{
                        font-weight: bold;
                        color: #4CAF50;
                    }}
                    .footer {{
                        margin-top: 30px;
                        font-size: 14px;
                        color: #666;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Stato Server QR Bar</h1>
                    <div class="status-item">
                        Stato: <span class="status-value">Attivo</span>
                    </div>
                    <div class="status-item">
                        Timer connessi: <span class="status-value">{online_timers}</span>
                    </div>
                    <div class="status-item">
                        Richieste bar attive: <span class="status-value">{active_requests}</span>
                    </div>
                    <div class="status-item">
                        Uptime: <span class="status-value">{uptime_hours}h {uptime_minutes}m</span>
                    </div>
                    <div class="footer">
                        Poker Timer QR Bar Service
                    </div>
                </div>
            </body>
            </html>
            """
            
            return Response(html_response, mimetype='text/html')

        @self.app.route('/api/bar_service_request', methods=['POST'])
        def bar_service_request():
            request_data = request.json
            table_number = request_data.get('table_number')
            timestamp = request_data.get('timestamp')
            
            logger.info(f"Ricevuta richiesta servizio bar dal tavolo {table_number}")
            
            # Trova il dispositivo corrispondente a questo tavolo
            target_device_id = None
            for device_id, timer in self.timers.items():
                if timer.get('table_number') == table_number:
                    target_device_id = device_id
                    break
            
            if target_device_id:
                # Aggiungi il timestamp della richiesta bar
                self.timers[target_device_id]['bar_service_timestamp'] = int(time.time() * 1000)  # timestamp in millisecondi
                
                # Emetti il segnale per aggiornare l'interfaccia
                self.timer_updated.emit(target_device_id)
            
            # Genera un ID univoco per la richiesta
            request_id = f"bar_{table_number}_{timestamp}"
            
            # Aggiungi alla lista delle richieste
            bar_request = {
                "id": request_id,
                "table_number": table_number,
                "timestamp": timestamp
            }
            self.bar_requests.append(bar_request)
            
            # Emetti il segnale per la notifica
            #self.bar_service_notification.emit(table_number)
            
            return jsonify({
                "status": "success",
                "message": f"Richiesta bar registrata per tavolo {table_number}",
                "request_id": request_id
            })

        
        # API per ottenere le richieste bar
        @self.app.route('/api/bar_requests', methods=['GET'])
        def get_bar_requests():
            return jsonify(self.bar_requests)
        
        # API per completare una richiesta bar
        @self.app.route('/api/bar_requests/<request_id>/complete', methods=['POST'])
        def complete_bar_request(request_id):
            # Trova e rimuovi la richiesta
            self.bar_requests = [r for r in self.bar_requests if r['id'] != request_id]
            
            logger.info(f"Richiesta bar {request_id} completata")
            
            return jsonify({
                "status": "success",
                "message": "Richiesta completata"
            })
    
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
            # Timer considerato online se aggiornato negli ultimi 3 minuti
            return (now - last_update).total_seconds() < 180  # 3 minuti = 180 secondi
        except Exception:
            return False