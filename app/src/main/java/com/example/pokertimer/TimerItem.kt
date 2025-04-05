package com.example.pokertimer

/**
 * Modello dati che rappresenta un timer ricevuto dal server
 */
data class TimerItem(
    val deviceId: String,
    val tableNumber: Int,
    val isRunning: Boolean,
    val isPaused: Boolean,
    val currentTimer: Int,
    val isExpired: Boolean,
    val operationMode: Int,
    val timerT1: Int,
    val timerT2: Int,
    val batteryLevel: Int,
    val voltage: Float,
    val wifiSignal: Int? = null,
    val lastUpdateTimestamp: String,
    val ipAddress: String? = null,
    val buzzerEnabled: Boolean = true,
    val pendingCommand: String? = null,
    val seatOpenInfo: String? = null  // Nuova proprietà per i posti liberi
) {
    /**
     * Verifica se ci sono posti liberi da visualizzare
     */
    fun hasSeatOpenInfo(): Boolean {
        return !seatOpenInfo.isNullOrEmpty() ||
                (pendingCommand != null && pendingCommand.startsWith("seat_open:"))
    }
    /**
     * Ottiene la stringa formattata dei posti liberi
     */
    fun getFormattedSeatInfo(): String {
        return when {
            !seatOpenInfo.isNullOrEmpty() -> "SEAT OPEN: $seatOpenInfo"
            pendingCommand != null && pendingCommand.startsWith("seat_open:") ->
                "SEAT OPEN: ${pendingCommand.substringAfter("seat_open:")}"
            else -> ""
        }
    }
}