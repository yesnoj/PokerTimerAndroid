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
    val pendingCommand: String? = null
)