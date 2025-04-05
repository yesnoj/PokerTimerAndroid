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

            // Gestione delle informazioni sui posti liberi
            // Inizializza a null e poi cerca in vari campi possibili
            var seatOpenInfo: String? = null

            // Cerca nel campo seat_open
            if (timerJson.has("seat_open") && !timerJson.isNull("seat_open")) {
                seatOpenInfo = timerJson.optString("seat_open")
                android.util.Log.d("JSONExtensions", "Found seat_open: $seatOpenInfo for timer $deviceId")
            }

            // Cerca nel campo seat_open_info
            else if (timerJson.has("seat_open_info") && !timerJson.isNull("seat_open_info")) {
                seatOpenInfo = timerJson.optString("seat_open_info")
                android.util.Log.d("JSONExtensions", "Found seat_open_info: $seatOpenInfo for timer $deviceId")
            }

            // Verifica se il seat_info è stato resettato
            var seatOpenInfoIsReset = false
            if (timerJson.has("seat_info_reset") && !timerJson.isNull("seat_info_reset")) {
                seatOpenInfoIsReset = timerJson.optBoolean("seat_info_reset", false)
            }

            // Se il seat_info è stato esplicitamente resettato, forza un valore null
            if (seatOpenInfoIsReset) {
                seatOpenInfo = null
                android.util.Log.d("JSONExtensions", "seat_info explicitly reset for timer $deviceId")
            }

            // Cerca nel campo seat_info che è un oggetto con array open_seats
            if (timerJson.has("seat_info") && !timerJson.isNull("seat_info")) {
                val seatInfoObj = timerJson.optJSONObject("seat_info")
                if (seatInfoObj != null) {
                    if (!seatInfoObj.has("open_seats") || seatInfoObj.isNull("open_seats") ||
                        seatInfoObj.getJSONArray("open_seats").length() == 0) {
                        seatOpenInfo = null
                        android.util.Log.d("JSONExtensions", "seat_info has no open_seats for timer $deviceId")
                    } else {
                        // Se c'è open_seats, estrai i valori
                        val openSeatsArray = seatInfoObj.getJSONArray("open_seats")
                        val seatsStringBuilder = StringBuilder()
                        for (i in 0 until openSeatsArray.length()) {
                            if (i > 0) seatsStringBuilder.append(", ")
                            seatsStringBuilder.append(openSeatsArray.get(i))
                        }
                        seatOpenInfo = seatsStringBuilder.toString()
                        android.util.Log.d("JSONExtensions", "Extracted seat_info.open_seats: $seatOpenInfo for timer $deviceId")
                    }
                }
            }

            // Cerca nel campo timer_data
            else if (timerJson.has("timer_data") && !timerJson.isNull("timer_data")) {
                val timerData = timerJson.optJSONObject("timer_data")
                if (timerData != null && timerData.has("seat_open") && !timerData.isNull("seat_open")) {
                    seatOpenInfo = timerData.optString("seat_open")
                    android.util.Log.d("JSONExtensions", "Found timer_data.seat_open: $seatOpenInfo for timer $deviceId")
                }
            }

            // Cerca nel pendingCommand per seat_open:
            if (seatOpenInfo == null && pendingCommand != null && pendingCommand.startsWith("seat_open:")) {
                seatOpenInfo = pendingCommand.substringAfter("seat_open:").trim()
                android.util.Log.d("JSONExtensions", "Extracted seat info from pendingCommand: $seatOpenInfo for timer $deviceId")
            }

            // Verifica se è una stringa vuota e in tal caso usa null
            if (seatOpenInfo != null && seatOpenInfo.isEmpty()) {
                seatOpenInfo = null
            }

            // Verifica se dobbiamo forzare i dati per il tavolo 2 (solo per debug)
            // Rimuovi questa parte in produzione
            if (tableNumber == 2 && seatOpenInfo == null && !seatOpenInfoIsReset) {
                // Non forzare più il valore per tavolo 2 se era già stato resettato
                // seatOpenInfo = "1, 2, 3" // Forza i posti come nel log
                // android.util.Log.d("JSONExtensions", "Forcing seat info for table 2: $seatOpenInfo")
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
                seatOpenInfo = seatOpenInfo
            )

            // Log per debug se ci sono informazioni sui posti
            if (timerItem.hasSeatOpenInfo()) {
                android.util.Log.d("JSONExtensions", "Timer $deviceId (table $tableNumber) has seat info: ${timerItem.getFormattedSeatInfo()}")
            }

            timerList.add(timerItem)
        } catch (e: Exception) {
            // Log dell'errore ma continua con gli altri timer
            android.util.Log.e("TimerParser", "Errore nel parsing del timer $key: ${e.message}")
        }
    }

    // Ordina i timer per numero di tavolo
    return timerList.sortedBy { it.tableNumber }
}