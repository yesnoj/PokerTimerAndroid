#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Modulo per l'installazione automatica dei pacchetti mancanti
"""

import sys
import os
import logging
import subprocess
from PyQt6.QtWidgets import QMessageBox

# Configura logger
logger = logging.getLogger('package_installer')
logger.setLevel(logging.INFO)

def check_and_install_package(package_name, parent_widget=None):
    """
    Verifica se un pacchetto è installato e offre di installarlo se manca
    
    Args:
        package_name: Nome del pacchetto da verificare/installare
        parent_widget: Widget genitore per mostrare i messaggi (opzionale)
        
    Returns:
        bool: True se il pacchetto è (o è stato) installato con successo, False altrimenti
    """
    try:
        # Prova a importare il pacchetto
        __import__(package_name)
        logger.info(f"Pacchetto {package_name} già installato")
        return True
    except ImportError:
        logger.warning(f"Pacchetto {package_name} non trovato")
        
        # Se non c'è un widget genitore, installa senza chiedere
        if parent_widget is None:
            return install_package(package_name)
        
        # Chiedi all'utente se vuole installare il pacchetto
        reply = QMessageBox.question(
            parent_widget,
            "Pacchetto mancante",
            f"Il pacchetto '{package_name}' è richiesto per questa funzionalità ma non è installato.\n\n"
            f"Vuoi installarlo ora?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            return install_package(package_name, parent_widget)
        else:
            return False

def install_package(package_name, parent_widget=None):
    """
    Installa un pacchetto Python usando pip
    
    Args:
        package_name: Nome del pacchetto da installare
        parent_widget: Widget genitore per mostrare i messaggi (opzionale)
        
    Returns:
        bool: True se l'installazione è riuscita, False altrimenti
    """
    try:
        logger.info(f"Tentativo di installazione di {package_name}")
        
        # Comando pip da eseguire
        pip_cmd = [sys.executable, "-m", "pip", "install", package_name]
        
        # Mostra un messaggio di stato se c'è un widget genitore
        if parent_widget:
            QMessageBox.information(
                parent_widget,
                "Installazione in corso",
                f"Installazione di {package_name} in corso...\n"
                "Questo potrebbe richiedere qualche istante.",
                QMessageBox.StandardButton.Ok
            )
        
        # Esegui il comando di installazione
        result = subprocess.run(
            pip_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False  # Non sollevare eccezioni se il comando fallisce
        )
        
        # Verifica il risultato
        if result.returncode == 0:
            logger.info(f"Installazione di {package_name} completata con successo")
            
            if parent_widget:
                QMessageBox.information(
                    parent_widget,
                    "Installazione completata",
                    f"Il pacchetto {package_name} è stato installato con successo.",
                    QMessageBox.StandardButton.Ok
                )
            
            # Riprova a importare il pacchetto per verificare l'installazione
            try:
                __import__(package_name)
                return True
            except ImportError:
                # Caso strano: l'installazione è riuscita ma l'importazione fallisce
                logger.error(f"Pacchetto {package_name} installato ma non importabile")
                
                if parent_widget:
                    QMessageBox.warning(
                        parent_widget,
                        "Errore di importazione",
                        f"Il pacchetto {package_name} è stato installato ma non può essere importato.\n"
                        "Potrebbe essere necessario riavviare l'applicazione.",
                        QMessageBox.StandardButton.Ok
                    )
                
                return False
        else:
            # L'installazione è fallita
            error_msg = result.stderr or "Errore sconosciuto"
            logger.error(f"Errore nell'installazione di {package_name}: {error_msg}")
            
            if parent_widget:
                QMessageBox.critical(
                    parent_widget,
                    "Errore di installazione",
                    f"Impossibile installare {package_name}. Dettagli dell'errore:\n\n{error_msg}",
                    QMessageBox.StandardButton.Ok
                )
            
            return False
    
    except Exception as e:
        # Errore generico
        logger.error(f"Eccezione durante l'installazione di {package_name}: {str(e)}")
        
        if parent_widget:
            QMessageBox.critical(
                parent_widget,
                "Errore",
                f"Si è verificato un errore durante l'installazione di {package_name}:\n\n{str(e)}",
                QMessageBox.StandardButton.Ok
            )
        
        return False

def check_multiple_packages(package_list, parent_widget=None):
    """
    Verifica e installa più pacchetti in sequenza
    
    Args:
        package_list: Lista di nomi di pacchetti da verificare/installare
        parent_widget: Widget genitore per mostrare i messaggi (opzionale)
        
    Returns:
        dict: Dizionario con i nomi dei pacchetti come chiavi e lo stato di installazione come valori
    """
    results = {}
    
    for package in package_list:
        results[package] = check_and_install_package(package, parent_widget)
    
    return results