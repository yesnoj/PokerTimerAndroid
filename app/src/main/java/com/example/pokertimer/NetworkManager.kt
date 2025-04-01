package com.example.pokertimer

import android.content.Context
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.net.HttpURLConnection
import java.net.URL
import com.google.gson.Gson
import java.util.Random

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