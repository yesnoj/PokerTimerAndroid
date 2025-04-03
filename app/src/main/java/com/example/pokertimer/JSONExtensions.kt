package com.example.pokertimer

import org.json.JSONObject

/**
 * Funzione di estensione per convertire i dati JSON in una lista di TimerItem
 */
fun JSONObject.parseTimers(): List<TimerItem> {
    val timerList = mutableListOf<TimerItem>()

    // Itera su tutte le chiavi nel JSON, ogni chiave è un ID del timer
    this.keys().forEach { key ->
        try {
            val timerJson = this.getJSONObject(key)

            // Estrai i dati dal JSON con gestione dei tipi e valori predefiniti
            val deviceId = timerJson.optString("device_id", key)
            val tableNumber = timerJson.optInt("table_number", 0)

            // Gestione dei valori booleani che potrebbero essere 0/1 invece di true/false
            val isRunning = when (val runVal = timerJson.opt("is_running")) {
                is Boolean -> runVal
                is Int -> runVal == 1
                is Double -> runVal == 1.0
                is String -> runVal.equals("true", ignoreCase = true) || runVal == "1"
                else -> false
            }

            val isPaused = when (val pauseVal = timerJson.opt("is_paused")) {
                is Boolean -> pauseVal
                is Int -> pauseVal == 1
                is Double -> pauseVal == 1.0
                is String -> pauseVal.equals("true", ignoreCase = true) || pauseVal == "1"
                else -> false
            }

            val currentTimer = timerJson.optInt("current_timer", 0)

            val isExpired = when (val expiredVal = timerJson.opt("time_expired")) {
                is Boolean -> expiredVal
                is Int -> expiredVal == 1
                is Double -> expiredVal == 1.0
                is String -> expiredVal.equals("true", ignoreCase = true) || expiredVal == "1"
                else -> false
            }

            val operationMode = timerJson.optInt("mode", 1)
            val timerT1 = timerJson.optInt("t1_value", 20)
            val timerT2 = timerJson.optInt("t2_value", 30)
            val batteryLevel = timerJson.optInt("battery_level", 100)
            val voltage = timerJson.optDouble("voltage", 5.0).toFloat()

            // Alcuni campi potrebbero non essere presenti in tutti i dispositivi
            val wifiSignal = if (timerJson.has("wifi_signal")) timerJson.optInt("wifi_signal") else null
            val lastUpdateTimestamp = timerJson.optString("last_update", "")

            // Fix per l'errore di tipo - gestione corretta dei valori nulli
            val ipAddress = if (timerJson.has("ip_address") && !timerJson.isNull("ip_address"))
                timerJson.optString("ip_address")
            else
                null

            val buzzerEnabled = when (val buzzerVal = timerJson.opt("buzzer")) {
                is Boolean -> buzzerVal
                is Int -> buzzerVal == 1
                is Double -> buzzerVal == 1.0
                is String -> buzzerVal.equals("true", ignoreCase = true) || buzzerVal == "1"
                else -> true
            }

            // Fix per l'errore di tipo - gestione corretta dei valori nulli
            val pendingCommand = if (timerJson.has("pending_command") && !timerJson.isNull("pending_command")) {
                val cmd = timerJson.optString("pending_command")
                if (cmd.isEmpty()) null else cmd
            } else {
                null
            }

            // Estrai informazioni sui posti liberi, se presenti
            val seatInfo = if (timerJson.has("seat_info") && !timerJson.isNull("seat_info")) {
                val seatInfoJson = timerJson.getJSONObject("seat_info")

                // Estrai la lista dei posti aperti
                val openSeatsArray = seatInfoJson.optJSONArray("open_seats")
                val openSeats = if (openSeatsArray != null) {
                    val seatList = mutableListOf<Int>()
                    for (i in 0 until openSeatsArray.length()) {
                        seatList.add(openSeatsArray.optInt(i))
                    }
                    seatList
                } else {
                    emptyList()
                }

                // Crea l'oggetto SeatInfo
                if (openSeats.isNotEmpty()) {
                    // Imposta needsNotification true solo se è una nuova notifica
                    val needsNotification = seatInfoJson.optBoolean("needs_web_notification", false)
                    SeatInfo(openSeats, needsNotification)
                } else {
                    null
                }
            } else {
                null
            }

            // Crea un oggetto TimerItem e aggiungilo alla lista
            val timerItem = TimerItem(
                deviceId = deviceId,
                tableNumber = tableNumber,
                isRunning = isRunning,
                isPaused = isPaused,
                currentTimer = currentTimer,
                isExpired = isExpired,
                operationMode = operationMode,
                timerT1 = timerT1,
                timerT2 = timerT2,
                batteryLevel = batteryLevel,
                voltage = voltage,
                wifiSignal = wifiSignal,
                lastUpdateTimestamp = lastUpdateTimestamp,
                ipAddress = ipAddress,
                buzzerEnabled = buzzerEnabled,
                pendingCommand = pendingCommand,
                seatInfo = seatInfo
            )

            timerList.add(timerItem)
        } catch (e: Exception) {
            // Log dell'errore ma continua con gli altri timer
            android.util.Log.e("TimerParser", "Errore nel parsing del timer $key: ${e.message}")
        }
    }

    // Ordina i timer per numero di tavolo
    return timerList.sortedBy { it.tableNumber }
}