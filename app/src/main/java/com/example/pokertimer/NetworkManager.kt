package com.example.pokertimer

import android.content.Context
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.net.HttpURLConnection
import java.net.URL
import com.google.gson.Gson
import java.util.Random
import kotlinx.coroutines.delay
import org.json.JSONObject

class NetworkManager(private val context: Context) {

    /**
     * Ottiene un identificatore univoco per il dispositivo in un formato compatibile col server
     * Genera un ID nel formato "android_XXXX" dove XXXX è un numero casuale fisso
     */
    private fun getUniqueDeviceId(): String {
        // Recupera un ID base univoco dalle preferenze
        val prefs = context.getSharedPreferences("device_id_prefs", Context.MODE_PRIVATE)
        var baseId = prefs.getString("unique_device_id_base", null)

        if (baseId == null) {
            // Genera un numero casuale fisso a 4 cifre come base
            baseId = (1000 + Random().nextInt(9000)).toString()
            prefs.edit().putString("unique_device_id_base", baseId).apply()
            android.util.Log.d("NetworkManager", "Generated new base ID: $baseId")
        }

        // Formatta l'ID nel formato che il server si aspetta
        return "android_$baseId"
    }

    /**
     * Invia lo stato del timer al server e riceve eventuali comandi
     * @return Coppia (successo, comando)
     */
    suspend fun sendTimerStatus(serverUrl: String, timerState: PokerTimerState): Pair<Boolean, Command?> {
        return withContext(Dispatchers.IO) {
            try {
                val url = URL("$serverUrl/api/status")
                android.util.Log.d("NetworkManager", "Sending status to: $url")

                val connection = url.openConnection() as HttpURLConnection
                connection.requestMethod = "POST"
                connection.doOutput = true
                connection.setRequestProperty("Content-Type", "application/json; charset=UTF-8")

                // Payload con il formato corretto, usando l'ID univoco
                val deviceId = getUniqueDeviceId()
                android.util.Log.d("NetworkManager", "Using device ID: $deviceId")

                val jsonPayload = """
                {
                    "device_id": "$deviceId",
                    "table_number": ${timerState.tableNumber},
                    "is_running": ${timerState.isRunning},
                    "is_paused": ${timerState.isPaused},
                    "current_timer": ${timerState.currentTimer},
                    "time_expired": ${timerState.isExpired},
                    "mode": ${timerState.operationMode},
                    "t1_value": ${timerState.timerT1},
                    "t2_value": ${timerState.timerT2},
                    "battery_level": 100,
                    "voltage": 5.0
                }
                """.trimIndent()

                android.util.Log.d("NetworkManager", "Sending payload: $jsonPayload")

                // Invia i dati
                val outputStream = connection.outputStream
                outputStream.write(jsonPayload.toByteArray())
                outputStream.close()

                val responseCode = connection.responseCode
                android.util.Log.d("NetworkManager", "Response code: $responseCode")

                // Elabora la risposta del server per verificare eventuali comandi pendenti
                if (responseCode == HttpURLConnection.HTTP_OK) {
                    val inputStream = connection.inputStream
                    val responseBody = inputStream.bufferedReader().use { it.readText() }
                    android.util.Log.d("NetworkManager", "Response body: $responseBody")

                    // Elabora il comando nella risposta
                    try {
                        val gson = Gson()
                        val response = gson.fromJson(responseBody, ServerResponse::class.java)

                        if (response.command != null) {
                            android.util.Log.d("NetworkManager", "Received command: ${response.command}")

                            // Gestisci i diversi comandi
                            when (response.command) {
                                "start" -> return@withContext Pair(true, Command.START)
                                "pause" -> return@withContext Pair(true, Command.PAUSE)
                                "reset" -> return@withContext Pair(true, Command.RESET)
                                "settings", "apply_settings" -> {  // Aggiungi "apply_settings" qui
                                    // Elabora le nuove impostazioni
                                    if (response.settings != null) {
                                        val settings = response.settings
                                        android.util.Log.d("NetworkManager", "Received settings: $settings")

                                        val t1 = settings.t1 ?: timerState.timerT1
                                        val t2 = settings.t2 ?: timerState.timerT2
                                        val mode = settings.mode ?: timerState.operationMode
                                        val tableNumber = settings.tableNumber ?: timerState.tableNumber

                                        // Gestione migliorata del buzzer
                                        val buzzerEnabled = when {
                                            settings.buzzer == null -> timerState.buzzerEnabled
                                            settings.buzzer is Boolean -> settings.buzzer as Boolean
                                            settings.buzzer is Double -> (settings.buzzer as Double).toInt() == 1
                                            settings.buzzer is Int -> (settings.buzzer as Int) == 1
                                            settings.buzzer is String -> {
                                                val buzzerStr = settings.buzzer as String
                                                buzzerStr.equals("true", ignoreCase = true) ||
                                                        buzzerStr == "1"
                                            }
                                            else -> {
                                                // Conversione di sicurezza: prova a convertire in stringa
                                                val buzzerStr = settings.buzzer.toString()
                                                buzzerStr.equals("true", ignoreCase = true) ||
                                                        buzzerStr == "1"
                                            }
                                        }

                                        android.util.Log.d("NetworkManager", "Buzzer setting: ${settings.buzzer} (${settings.buzzer?.javaClass?.simpleName}), parsed as: $buzzerEnabled")

                                        return@withContext Pair(true, Command.SETTINGS(
                                            t1, t2, mode, tableNumber, buzzerEnabled
                                        ))
                                    }
                                }
                            }
                        }
                    } catch (e: Exception) {
                        android.util.Log.e("NetworkManager", "Error parsing response: ${e.message}", e)
                    }
                }

                connection.disconnect()

                // Ritorna true e nessun comando se tutto è andato bene ma non ci sono comandi
                return@withContext Pair(true, null)
            } catch (e: Exception) {
                android.util.Log.e("NetworkManager", "Send status error: ${e.message}", e)
                return@withContext Pair(false, null)
            }
        }
    }

    // Classe per rappresentare la risposta del server
    data class ServerResponse(
        val status: String,
        val command: String? = null,
        val settings: TimerSettings? = null
    )

    // Classe per rappresentare le impostazioni del timer
    data class TimerSettings(
        val t1: Int? = null,
        val t2: Int? = null,
        val mode: Int? = null,
        val tableNumber: Int? = null,
        val buzzer: Any? = null  // Cambiato da Boolean? a Any? per gestire sia Int che Boolean
    )

    // Enum per rappresentare i comandi
    sealed class Command {
        object START : Command()
        object PAUSE : Command()
        object RESET : Command()
        data class SETTINGS(
            val t1: Int,
            val t2: Int,
            val mode: Int,
            val tableNumber: Int,
            val buzzerEnabled: Boolean
        ) : Command()

        // Aggiungi questa nuova classe di comando:
        data class SEAT_OPEN(val seats: String) : Command()
    }

    /**
     * Invia una richiesta di posti liberi al server
     */
    suspend fun sendSeatRequest(serverUrl: String, seatRequest: PlayerSeatRequest): Boolean {
        return withContext(Dispatchers.IO) {
            try {
                val url = URL("$serverUrl/api/seat_request")
                android.util.Log.d("NetworkManager", "Sending seat request to: $url")

                val connection = url.openConnection() as HttpURLConnection
                connection.requestMethod = "POST"
                connection.doOutput = true
                connection.setRequestProperty("Content-Type", "application/json; charset=UTF-8")

                // Log più dettagliato che mostra esattamente i posti selezionati
                android.util.Log.d("NetworkManager", "Selected seats: ${seatRequest.selectedSeats.joinToString(", ")}")

                // Costruisci il payload JSON
                val deviceId = getUniqueDeviceId()
                val jsonPayload = """
            {
                "device_id": "$deviceId",
                "table_number": ${seatRequest.tableNumber},
                "seats": [${seatRequest.selectedSeats.joinToString(",")}],
                "action": "seat_open"
            }
            """.trimIndent()

                android.util.Log.d("NetworkManager", "Sending payload: $jsonPayload")

                // Invia i dati
                val outputStream = connection.outputStream
                outputStream.write(jsonPayload.toByteArray())
                outputStream.close()

                val responseCode = connection.responseCode
                android.util.Log.d("NetworkManager", "Response code: $responseCode")

                // Leggi anche la risposta del server
                if (responseCode == HttpURLConnection.HTTP_OK) {
                    val inputStream = connection.inputStream
                    val responseBody = inputStream.bufferedReader().use { it.readText() }
                    android.util.Log.d("NetworkManager", "Server response: $responseBody")
                }

                connection.disconnect()

                // Se la richiesta è andata a buon fine, facciamo una richiesta di refresh
                if (responseCode == HttpURLConnection.HTTP_OK) {
                    // Aspetta un po' per dare tempo al server di elaborare
                    delay(500)

                    // Fai una richiesta per ottenere lo stato aggiornato dal server
                    val statusUrl = URL("$serverUrl/api/timers")
                    val statusConn = statusUrl.openConnection() as HttpURLConnection
                    statusConn.requestMethod = "GET"
                    val statusCode = statusConn.responseCode
                    android.util.Log.d("NetworkManager", "Status refresh response: $statusCode")
                    statusConn.disconnect()
                }

                return@withContext responseCode == HttpURLConnection.HTTP_OK
            } catch (e: Exception) {
                android.util.Log.e("NetworkManager", "Send seat request error: ${e.message}", e)
                return@withContext false
            }
        }
    }

    /**
     * Invia una richiesta per resettare i posti liberi di un tavolo
     */
    suspend fun resetSeatInfo(serverUrl: String, tableNumber: Int): Boolean {
        return withContext(Dispatchers.IO) {
            try {
                // Prima, dobbiamo trovare il deviceId corrispondente a questo tavolo
                // Facciamo una richiesta per ottenere tutti i timer
                val timersUrl = URL("$serverUrl/api/timers")
                val timersConnection = timersUrl.openConnection() as HttpURLConnection
                timersConnection.requestMethod = "GET"

                val responseCode = timersConnection.responseCode
                var deviceId: String? = null

                if (responseCode == HttpURLConnection.HTTP_OK) {
                    val inputStream = timersConnection.inputStream
                    val responseBody = inputStream.bufferedReader().use { it.readText() }

                    // Parsifichiamo il JSON per trovare il deviceId del timer con questo numero di tavolo
                    try {
                        val jsonObject = JSONObject(responseBody)
                        val keys = jsonObject.keys()

                        while (keys.hasNext()) {
                            val key = keys.next()
                            val timerObject = jsonObject.getJSONObject(key)
                            if (timerObject.optInt("table_number") == tableNumber) {
                                deviceId = key
                                break
                            }
                        }
                    } catch (e: Exception) {
                        android.util.Log.e("NetworkManager", "Error parsing timers JSON: ${e.message}")
                    }
                }

                timersConnection.disconnect()

                if (deviceId == null) {
                    android.util.Log.e("NetworkManager", "No device found for table $tableNumber")
                    return@withContext false
                }

                // Ora usiamo il comando reset_seat_info
                val commandUrl = URL("$serverUrl/api/command/$deviceId")
                android.util.Log.d("NetworkManager", "Sending reset_seat_info command to: $commandUrl")

                val connection = commandUrl.openConnection() as HttpURLConnection
                connection.requestMethod = "POST"
                connection.doOutput = true
                connection.setRequestProperty("Content-Type", "application/json; charset=UTF-8")

                // Payload JSON con il comando reset_seat_info
                val jsonPayload = """
            {
                "command": "reset_seat_info"
            }
            """.trimIndent()

                android.util.Log.d("NetworkManager", "Sending payload: $jsonPayload")

                val outputStream = connection.outputStream
                outputStream.write(jsonPayload.toByteArray())
                outputStream.close()

                val cmdResponseCode = connection.responseCode
                android.util.Log.d("NetworkManager", "Response code: $cmdResponseCode")

                if (cmdResponseCode == HttpURLConnection.HTTP_OK) {
                    val cmdInputStream = connection.inputStream
                    val cmdResponseBody = cmdInputStream.bufferedReader().use { it.readText() }
                    android.util.Log.d("NetworkManager", "Server response: $cmdResponseBody")
                }

                connection.disconnect()

                return@withContext cmdResponseCode == HttpURLConnection.HTTP_OK
            } catch (e: Exception) {
                android.util.Log.e("NetworkManager", "Reset seats error: ${e.message}", e)
                return@withContext false
            }
        }
    }

    /**
     * Elabora i comandi dal server, tra cui le informazioni sui posti liberi
     */
    private fun processServerCommand(responseBody: String): Command? {
        try {
            val gson = Gson()
            val response = gson.fromJson(responseBody, ServerResponse::class.java)

            if (response.command != null) {
                android.util.Log.d("NetworkManager", "Received command: ${response.command}")

                // Gestisci i diversi comandi
                when {
                    response.command == "start" -> return Command.START
                    response.command == "pause" -> return Command.PAUSE
                    response.command == "reset" -> return Command.RESET
                    response.command.startsWith("seat_open:") -> {
                        // Estrai i posti dalla stringa del comando
                        val seats = response.command.substringAfter("seat_open:")
                        return Command.SEAT_OPEN(seats)
                    }
                    response.command == "settings" || response.command == "apply_settings" -> {
                        // Elabora le nuove impostazioni
                        // ... (codice esistente)
                    }
                }
            }
        } catch (e: Exception) {
            android.util.Log.e("NetworkManager", "Error parsing command: ${e.message}", e)
        }
        return null
    }

    /**
     * Testa la connessione al server
     */
    suspend fun testConnection(serverUrl: String): Boolean {
        return withContext(Dispatchers.IO) {
            try {
                // Prova prima con l'endpoint /api/timers
                val url = URL("$serverUrl/api/timers")
                android.util.Log.d("NetworkManager", "Testing connection to: $url")

                val connection = url.openConnection() as HttpURLConnection
                connection.requestMethod = "GET"
                connection.connectTimeout = 5000

                val responseCode = connection.responseCode
                android.util.Log.d("NetworkManager", "Response code: $responseCode")
                connection.disconnect()

                return@withContext responseCode == HttpURLConnection.HTTP_OK
            } catch (e: Exception) {
                android.util.Log.e("NetworkManager", "Connection error: ${e.message}", e)
                return@withContext false
            }
        }
    }
}