#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script per configurare l'ambiente Poker Timer Monitor
Copia i file necessari dall'implementazione originale
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def print_colored(text, color_code):
    """Stampa testo colorato nella console"""
    print(f"\033[{color_code}m{text}\033[0m")

def print_success(text):
    """Stampa messaggio di successo in verde"""
    print_colored(text, 92)

def print_error(text):
    """Stampa messaggio di errore in rosso"""
    print_colored(text, 91)

def print_warning(text):
    """Stampa avviso in giallo"""
    print_colored(text, 93)

def print_info(text):
    """Stampa informazione in blu"""
    print_colored(text, 94)

def find_original_dir():
    """Cerca la directory originale poker-timer-monitor"""
    # Directory corrente
    current_dir = Path(os.getcwd())
    
    # Controlla se siamo nella cartella python_conversion
    if current_dir.name == "python_conversion":
        parent_dir = current_dir.parent
        if os.path.exists(os.path.join(parent_dir, "public", "index.html")):
            return parent_dir
    
    # Cerca nella directory parent
    parent_dir = current_dir.parent
    if os.path.exists(os.path.join(parent_dir, "public", "index.html")):
        return parent_dir
    
    # Cerca direttamente in una directory chiamata poker-timer-monitor
    if os.path.exists(os.path.join(current_dir, "../poker-timer-monitor/public/index.html")):
        return os.path.join(current_dir, "../poker-timer-monitor")
    
    return None

def copy_web_files(src_dir, dest_dir):
    """Copia i file web dalla directory originale a quella di destinazione"""
    src_public = os.path.join(src_dir, "public")
    
    # Crea la directory public se non esiste
    os.makedirs(dest_dir, exist_ok=True)
    
    # Copia tutti i file dalla directory public
    if os.path.exists(src_public):
        files_copied = 0
        for item in os.listdir(src_public):
            src_item = os.path.join(src_public, item)
            dest_item = os.path.join(dest_dir, item)
            
            if os.path.isfile(src_item):
                shutil.copy2(src_item, dest_item)
                files_copied += 1
                print(f"  Copiato: {item}")
            elif os.path.isdir(src_item):
                shutil.copytree(src_item, dest_item, dirs_exist_ok=True)
                files_copied += 1
                print(f"  Copiata directory: {item}")
        
        return files_copied
    else:
        print_error(f"Directory public non trovata in: {src_dir}")
        return 0

def install_dependencies():
    """Installa le dipendenze necessarie"""
    print_info("\nInstallazione delle dipendenze...")
    
    try:
        # Prova con pip3
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print_success("Dipendenze installate con successo!")
        return True
    except Exception as e:
        print_error(f"Errore nell'installazione delle dipendenze: {e}")
        
        print_warning("\nProvo a installare Flask direttamente...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "flask"], check=True)
            print_success("Flask installato con successo!")
            return True
        except Exception as e:
            print_error(f"Errore nell'installazione di Flask: {e}")
            return False

def main():
    print_info("=== Configurazione Poker Timer Monitor ===")
    
    # Crea directory public
    public_dir = os.path.join(os.getcwd(), "public")
    
    # Trova la directory originale
    print_info("\nRicerca dei file web originali...")
    original_dir = find_original_dir()
    
    if original_dir:
        print_success(f"Trovata directory originale: {original_dir}")
        
        # Copia i file web
        print_info("\nCopia dei file web...")
        files_copied = copy_web_files(original_dir, public_dir)
        
        if files_copied > 0:
            print_success(f"Copiati {files_copied} file/directory nella directory public")
        else:
            print_error("Nessun file copiato. Controlla i permessi e la struttura delle directory.")
            return False
    else:
        print_warning("Directory originale non trovata automaticamente.")
        while True:
            user_path = input("\nInserisci il percorso alla directory poker-timer-monitor originale\n(o premi Invio per creare una configurazione minimale): ")
            
            if not user_path.strip():
                print_warning("\nCreazione di una configurazione minimale...")
                break
            
            if os.path.exists(os.path.join(user_path, "public", "index.html")):
                print_success(f"Directory valida trovata: {user_path}")
                files_copied = copy_web_files(user_path, public_dir)
                
                if files_copied > 0:
                    print_success(f"Copiati {files_copied} file/directory nella directory public")
                    break
                else:
                    print_error("Nessun file copiato. Riprova con un altro percorso.")
            else:
                print_error(f"Directory non valida o 'index.html' non trovato in {os.path.join(user_path, 'public')}")
    
    # Installa le dipendenze
    install_ok = install_dependencies()
    
    # Riepilogo finale
    print_info("\n=== Configurazione completata ===")
    print(f"- Directory web: {public_dir}")
    print(f"- Dipendenze installate: {'Sì' if install_ok else 'No (installazione manuale richiesta)'}")
    
    print_info("\nPer avviare l'applicazione esegui:")
    print("python3 poker_timer_app.py")
    
    print_info("\nPer avviare solo il server (senza interfaccia grafica):")
    print("python3 poker_timer_server.py")
    
    return True

if __name__ == "__main__":
    main()