#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Poker Timer Monitor - Applicazione Desktop
Versione Python con interfaccia PyQt6
"""

import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from ui.main_window import MainWindow

def main():
    """Funzione principale dell'applicazione"""
    # Crea l'applicazione Qt
    app = QApplication(sys.argv)
    app.setApplicationName("Poker Timer Monitor")
    
    # Imposta lo stile
    style_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                             'resources', 'styles.qss')
    
    if os.path.exists(style_path):
        with open(style_path, 'r') as f:
            style = f.read()
            app.setStyleSheet(style)
    
    # Carica l'icona se disponibile
    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                            'resources', 'icon.png')
    
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    # Crea e mostra la finestra principale
    window = MainWindow()
    window.show()
    
    # Esecuzione del ciclo principale
    sys.exit(app.exec())

if __name__ == "__main__":
    main()