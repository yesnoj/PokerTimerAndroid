#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Poker Timer App - Interfaccia grafica per il Poker Timer Server
Compatibile con Windows e macOS
"""

import os
import sys
import threading
import time
import webbrowser
import logging
from pathlib import Path
import json
import shutil

# Gestione dei moduli necessari
required_modules = ["flask", "tkinter"]
for module in required_modules:
    try:
        if module == "tkinter":
            import tkinter as tk
            from tkinter import ttk, messagebox, filedialog
        else:
            __import__(module)
    except ImportError:
        print(f"{module} non trovato. Installazione in corso...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", module])

import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# Importa il server
from poker_timer_server import PokerTimerServer

# Configurazione logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('poker_timer_app.log')
    ]
)
logger = logging.getLogger('poker_timer_app')

class PokerTimerApp:
    def __init__(self, root):
        self.root = root
        self.server = None
        self.server_thread = None
        self.is_server_running = False
        
        # Directory per i file statici
        self.static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'public')
        
        # Verifica se esiste la directory public e contiene index.html
        self.check_static_files()
        
        # Configurazione della finestra
        self.root.title("Poker Timer Monitor")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # Icona dell'applicazione (se disponibile)
        icon_path = os.path.join(self.static_dir, 'favicon.ico')
        if os.path.exists(icon_path):
            try:
                self.root.iconbitmap(icon_path)
            except Exception as e:
                logger.warning(f"Impossibile impostare l'icona: {e}")
        
        # Stile
        style = ttk.Style()
        style.configure("TButton", padding=6, relief="flat", background="#ccc")
        style.configure("Green.TButton", foreground="white", background="green")
        style.configure("Red.TButton", foreground="white", background="red")
        
        # Frame principale
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Titolo
        title_label = ttk.Label(
            main_frame, 
            text="Poker Timer Monitor", 
            font=("Arial", 18, "bold")
        )
        title_label.pack(pady=10)
        
        # Frame per le impostazioni del server
        settings_frame = ttk.LabelFrame(main_frame, text="Impostazioni Server", padding="10")
        settings_frame.pack(fill=tk.X, pady=10)
        
        # Porta HTTP
        http_port_frame = ttk.Frame(settings_frame)
        http_port_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(http_port_frame, text="Porta HTTP:").pack(side=tk.LEFT, padx=5)
        self.http_port_var = tk.StringVar(value="3000")
        http_port_entry = ttk.Entry(http_port_frame, textvariable=self.http_port_var, width=6)
        http_port_entry.pack(side=tk.LEFT, padx=5)
        
        # Porta Discovery
        udp_port_frame = ttk.Frame(settings_frame)
        udp_port_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(udp_port_frame, text="Porta Discovery:").pack(side=tk.LEFT, padx=5)
        self.udp_port_var = tk.StringVar(value="8888")
        udp_port_entry = ttk.Entry(udp_port_frame, textvariable=self.udp_port_var, width=6)
        udp_port_entry.pack(side=tk.LEFT, padx=5)
        
        # Directory per i file statici
        static_dir_frame = ttk.Frame(settings_frame)
        static_dir_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(static_dir_frame, text="Directory Web:").pack(side=tk.LEFT, padx=5)
        self.static_dir_var = tk.StringVar(value=self.static_dir)
        static_dir_entry = ttk.Entry(static_dir_frame, textvariable=self.static_dir_var, width=30)
        static_dir_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        browse_btn = ttk.Button(static_dir_frame, text="...", width=3, command=self.browse_static_dir)
        browse_btn.pack(side=tk.LEFT, padx=5)
        
        # Frame per i controlli del server
        controls_frame = ttk.Frame(main_frame)
        controls_frame.pack(fill=tk.X, pady=10)
        
        # Pulsante per avviare/fermare il server
        self.start_btn = ttk.Button(
            controls_frame, 
            text="Avvia Server", 
            command=self.toggle_server,
            style="Green.TButton",
            width=20
        )
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        # Pulsante per aprire l'interfaccia web
        self.open_browser_btn = ttk.Button(
            controls_frame, 
            text="Apri nel Browser", 
            command=self.open_browser,
            state=tk.DISABLED,
            width=20
        )
        self.open_browser_btn.pack(side=tk.LEFT, padx=5)
        
        # Frame per lo stato del server
        status_frame = ttk.LabelFrame(main_frame, text="Stato Server", padding="10")
        status_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Area di log
        self.log_text = tk.Text(status_frame, height=10, width=60, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        # Scrollbar per il log
        scrollbar = ttk.Scrollbar(status_frame, command=self.log_text.yview)
        scrollbar.pack(fill=tk.Y, side=tk.RIGHT)
        self.log_text.config(yscrollcommand=scrollbar.set)
        
        # Stato connessione
        conn_frame = ttk.Frame(main_frame)
        conn_frame.pack(fill=tk.X, pady=5)
        
        self.conn_label = ttk.Label(
            conn_frame, 
            text="Server: Non attivo", 
            foreground="red"
        )
        self.conn_label.pack(side=tk.LEFT, padx=5)
        
        self.timer_count_label = ttk.Label(
            conn_frame, 
            text="Timer connessi: 0", 
        )
        self.timer_count_label.pack(side=tk.RIGHT, padx=5)
        
        # Aggiungi un messaggio iniziale al log
        self.log("Poker Timer Monitor avviato")
        self.log(f"Directory Web: {self.static_dir}")
        
        # Rendi la finestra responsive
        for i in range(6):
            self.root.grid_rowconfigure(i, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Gestione della chiusura della finestra
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Timer per aggiornare la UI
        self.update_timer = None
        
        # Avvia il timer per aggiornare l'UI
        self.start_update_timer()

    def check_static_files(self):
        """Verifica se esiste la directory public e contiene index.html"""
        if not os.path.exists(self.static_dir):
            logger.warning(f"Directory {self.static_dir} non trovata. Creazione in corso...")
            os.makedirs(self.static_dir, exist_ok=True)
        
        index_html_path = os.path.join(self.static_dir, 'index.html')
        if not os.path.exists(index_html_path):
            logger.warning("File index.html non trovato nella directory public")
            
            # Cerca il file index.html nella directory del programma
            bundled_index_html = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'index.html')
            if os.path.exists(bundled_index_html):
                logger.info(f"Copia del file index.html bundled nella directory public")
                shutil.copy2(bundled_index_html, index_html_path)
            else:
                self.create_default_html()
    
    def create_default_html(self):
        """Crea un file index.html predefinito se non esiste"""
        logger.info("Creazione di un file index.html predefinito")
        default_html = """<!DOCTYPE html>
<html lang="it">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Poker Timer Monitor</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      margin: 0;
      padding: 20px;
      background-color: #f5f5f5;
      text-align: center;
    }
    
    h1 {
      color: #333;
      margin-bottom: 30px;
    }
    
    .message {
      background-color: #fff;
      border-radius: 8px;
      padding: 20px;
      max-width: 600px;
      margin: 0 auto;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .error {
      color: #721c24;
      background-color: #f8d7da;
      border: 1px solid #f5c6cb;
      padding: 10px;
      border-radius: 4px;
      margin-top: 20px;
    }
    
    .note {
      font-size: 0.9rem;
      color: #6c757d;
      margin-top: 20px;
    }
  </style>
</head>
<body>
  <h1>Poker Timer Monitor</h1>
  
  <div class="message">
    <p>Il server Poker Timer è in esecuzione, ma l'interfaccia web completa non è stata trovata.</p>
    
    <div class="error">
      <strong>File index.html non trovato nella directory public.</strong>
      <p>Per utilizzare l'interfaccia completa, copiare i file dell'interfaccia web nella directory:</p>
      <code>%s</code>
    </div>
    
    <p class="note">Questa è una pagina segnaposto. Il server è attivo e può essere utilizzato dalle app Poker Timer.</p>
  </div>
</body>
</html>""" % self.static_dir
        
        try:
            with open(os.path.join(self.static_dir, 'index.html'), 'w', encoding='utf-8') as f:
                f.write(default_html)
            logger.info("File index.html predefinito creato con successo")
        except Exception as e:
            logger.error(f"Errore nella creazione del file index.html: {e}")

    def browse_static_dir(self):
        """Apre un dialog per selezionare la directory dei file statici"""
        dir_path = filedialog.askdirectory(
            initialdir=self.static_dir,
            title="Seleziona Directory Web"
        )
        if dir_path:
            self.static_dir_var.set(dir_path)
            self.static_dir = dir_path

    def log(self, message):
        """Aggiunge un messaggio all'area di log"""
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)  # Scroll to the end
        logger.info(message)

    def toggle_server(self):
        """Avvia o ferma il server"""
        if self.is_server_running:
            self.stop_server()
        else:
            self.start_server()

    def start_server(self):
        """Avvia il server"""
        try:
            http_port = int(self.http_port_var.get())
            udp_port = int(self.udp_port_var.get())
            static_dir = self.static_dir_var.get()
            
            # Crea il server
            self.server = PokerTimerServer(
                port=http_port,
                discovery_port=udp_port,
                static_folder=static_dir
            )
            
            # Avvia il server in un thread separato
            self.server_thread = self.server.start_in_background()
            
            # Aggiorna lo stato
            self.is_server_running = True
            self.start_btn.config(text="Ferma Server", style="Red.TButton")
            self.open_browser_btn.config(state=tk.NORMAL)
            self.conn_label.config(text="Server: Attivo", foreground="green")
            
            # Log
            self.log(f"Server avviato su http://localhost:{http_port}")
            self.log(f"Servizio discovery avviato su porta UDP {udp_port}")
            
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile avviare il server: {e}")
            logger.error(f"Errore nell'avvio del server: {e}")

    def stop_server(self):
        """Ferma il server"""
        try:
            # Ferma il servizio di discovery
            if self.server:
                self.server.stop_discovery_service()
            
            # Il thread del server terminerà automaticamente quando l'applicazione si chiude
            
            # Aggiorna lo stato
            self.is_server_running = False
            self.start_btn.config(text="Avvia Server", style="Green.TButton")
            self.open_browser_btn.config(state=tk.DISABLED)
            self.conn_label.config(text="Server: Non attivo", foreground="red")
            
            # Log
            self.log("Server fermato")
            
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile fermare il server: {e}")
            logger.error(f"Errore nell'arresto del server: {e}")

    def open_browser(self):
        """Apre l'interfaccia web nel browser predefinito"""
        if self.is_server_running:
            http_port = self.http_port_var.get()
            url = f"http://localhost:{http_port}"
            webbrowser.open(url)
            self.log(f"Browser aperto all'indirizzo {url}")

    def update_ui(self):
        """Aggiorna l'interfaccia utente con le informazioni del server"""
        if self.is_server_running and self.server:
            # Aggiorna il conteggio dei timer
            timer_count = len(self.server.timers)
            self.timer_count_label.config(text=f"Timer connessi: {timer_count}")

    def start_update_timer(self):
        """Avvia il timer per aggiornare l'UI periodicamente"""
        self.update_ui()
        self.update_timer = self.root.after(1000, self.start_update_timer)

    def on_close(self):
        """Gestisce la chiusura dell'applicazione"""
        if self.is_server_running:
            if messagebox.askyesno("Conferma", "Il server è ancora in esecuzione. Vuoi fermarlo e uscire?"):
                self.stop_server()
                self.root.destroy()
        else:
            self.root.destroy()
        
        # Cancella il timer
        if self.update_timer:
            self.root.after_cancel(self.update_timer)

def main():
    """Funzione principale"""
    root = tk.Tk()
    app = PokerTimerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()