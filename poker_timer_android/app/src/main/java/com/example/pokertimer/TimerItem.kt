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
    val seatOpenInfo: String? = null,
    val playersCount: Int,
    val floormanCallTimestamp: Long? = null,  // NUOVO CAMPO
    val barServiceTimestamp: Long? = null     // NUOVO CAMPO per futuro supporto bar
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

    /**
     * Verifica se c'è una chiamata floorman attiva
     */
    fun hasActiveFloormanCall(): Boolean {
        return floormanCallTimestamp != null &&
                (System.currentTimeMillis() - floormanCallTimestamp) < 300000 // 5 minuti
    }

    /**
     * Verifica se c'è una richiesta bar attiva
     */
    fun hasActiveBarRequest(): Boolean {
        return barServiceTimestamp != null &&
                (System.currentTimeMillis() - barServiceTimestamp) < 600000 // 10 minuti
    }
}

/**
 * Data class per le richieste floorman
 */
data class FloormanRequest(
    val active: Boolean,
    val timestamp: String,
    val tableNumber: Int
)

/**
 * Data class per le richieste bar
 */
data class BarRequestInfo(
    val active: Boolean,
    val timestamp: String,
    val tableNumber: Int,
    val requestId: String
)