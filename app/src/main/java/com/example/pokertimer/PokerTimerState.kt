package com.example.pokertimer

/**
 * Rappresenta lo stato attuale del timer da poker
 */
data class PokerTimerState(
    val currentTimer: Int = 0,       // Timer attuale in secondi
    val timerT1: Int = 20,           // Valore del timer T1 (default 20s)
    val timerT2: Int = 30,           // Valore del timer T2 (default 30s)
    val isT1Active: Boolean = true,  // Se true, T1 è attivo, altrimenti T2
    val isRunning: Boolean = false,  // Se il timer è in esecuzione
    val isPaused: Boolean = false,   // Se il timer è in pausa
    val isExpired: Boolean = false,  // Se il timer è scaduto
    val operationMode: Int = 1,      // Modalità operativa (1-4)
    val buzzerEnabled: Boolean = true, // Se i suoni sono abilitati
    val tableNumber: Int = 1,        // Numero del tavolo
    val serverUrl: String = "http://192.168.4.1", // URL del server
    val isConnectedToServer: Boolean = false // Stato connessione
) {
    // Costanti per le modalità operative
    companion object {
        const val MODE_1 = 1  // T1/T2 switchabile, con tap torna a T1/T2 e parte subito a contare
        const val MODE_2 = 2  // T1/T2 switchabile, con tap riparte a contare da T1/T2
        const val MODE_3 = 3  // Solo T1, con tap torna a T1 e parte subito a contare
        const val MODE_4 = 4  // Solo T1, con tap resetta a T1 e rimane fermo
    }

    /**
     * Indica se l'interfaccia deve mostrare solo T1 (modalità 3 o 4)
     */
    val isT1OnlyMode: Boolean
        get() = operationMode == MODE_3 || operationMode == MODE_4

    /**
     * Indica se il reset deve far ripartire immediatamente il timer (modalità 1 o 3)
     */
    val isAutoStartMode: Boolean
        get() = operationMode == MODE_1 || operationMode == MODE_3
}