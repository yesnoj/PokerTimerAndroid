// PokerTimerState.kt
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
    val operationMode: Int = 1,      // Manteniamo un solo valore di modalità
    val buzzerEnabled: Boolean = true, // Se i suoni sono abilitati
    val tableNumber: Int = 1,        // Numero del tavolo
    val serverUrl: String = "http://192.168.4.1", // URL del server
    val isConnectedToServer: Boolean = false, // Stato connessione
    val playersCount: Int = 10,      // Numero di giocatori (default a 10)
    val batteryLevel: Int = 100,     // Livello della batteria (%)
    val batteryVoltage: Float = 5.0f // Voltaggio della batteria (V)
) {
    // Manteniamo questa costante per compatibilità con il codice esistente
    companion object {
        const val MODE_1 = 1
    }
}