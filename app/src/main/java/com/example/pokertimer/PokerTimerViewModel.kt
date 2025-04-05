// PokerTimerViewModel.kt
package com.example.pokertimer

import android.app.Application
import android.media.AudioAttributes
import android.media.SoundPool
import android.os.CountDownTimer
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import android.os.Handler
import android.os.Looper
import com.example.pokertimer.NetworkManager.Command
import android.util.Log


class PokerTimerViewModel(application: Application) : AndroidViewModel(application) {
    private var serverPollingJob: Job? = null
    private val preferences = PokerTimerPreferences(application)
    private val networkManager = NetworkManager(application)


    // Stato del timer osservabile
    private val _timerState = MutableLiveData<PokerTimerState>()
    val timerState: LiveData<PokerTimerState> = _timerState

    // Gestione dei suoni
    private val soundPool: SoundPool
    private val soundTick: Int
    private val soundPause: Int
    private val soundEnd: Int

    // Timer
    private var timerHandler: Handler? = null
    private var timerRunnable: Runnable? = null

    init {
        // Inizializzo il SoundPool
        val audioAttributes = AudioAttributes.Builder()
            .setUsage(AudioAttributes.USAGE_GAME)
            .setContentType(AudioAttributes.CONTENT_TYPE_SONIFICATION)
            .build()

        soundPool = SoundPool.Builder()
            .setMaxStreams(3)
            .setAudioAttributes(audioAttributes)
            .build()

        // Carico i suoni dalle risorse
        soundTick = soundPool.load(application, R.raw.tick, 1)
        soundPause = soundPool.load(application, R.raw.pause, 1)
        soundEnd = soundPool.load(application, R.raw.ending, 1)

        // Inizializza stato del timer dalle preferenze
        _timerState.value = preferences.loadTimerSettings()

        // Avvia il polling se è configurato un URL del server
        if (_timerState.value?.serverUrl?.isNotEmpty() == true) {
            startServerPolling()
        }
    }

    /**
     * Gestione del pulsante Start/Pause
     */
    fun onStartPausePressed() {
        val currentState = _timerState.value ?: return

        when {
            // Se il timer è in pausa, lo riprende
            currentState.isPaused && !currentState.isExpired -> {
                resumeTimer()
            }
            // Se il timer è in esecuzione, lo mette in pausa
            currentState.isRunning && !currentState.isPaused -> {
                pauseTimer()
            }
            // Se il timer è fermo o è terminato, lo avvia
            !currentState.isRunning || currentState.isExpired -> {
                startTimer()
            }
        }
    }

    /**
     * Gestione del pulsante Reset
     */
    fun onResetPressed() {
        val currentState = _timerState.value ?: return

        if (currentState.isAutoStartMode) {
            // Nelle modalità 1 e 3, resetta e riparte subito
            resetTimer(true)
        } else {
            // Nelle modalità 2 e 4, resetta e rimane fermo
            resetTimer(false)
        }
    }

    fun updateState(newState: PokerTimerState) {
        _timerState.value = newState
        // Invia lo stato aggiornato al server
        sendTimerStatusToServer()
    }

    fun refreshFromServer() {
        val currentState = _timerState.value ?: return
        if (currentState.serverUrl.isNotEmpty()) {
            CoroutineScope(Dispatchers.Main).launch {
                // Invia una richiesta al server per ottenere lo stato aggiornato
                sendTimerStatusToServer()

                // Attendi un breve momento per dare tempo al server di elaborare
                delay(500)

                // Richiedi nuovamente lo stato per assicurarsi di avere le info più recenti
                sendTimerStatusToServer()
            }
        }
    }

    /**
     * Gestione del pulsante Switch
     */
    fun onSwitchPressed() {
        val currentState = _timerState.value ?: return

        // Solo per le modalità 1 e 2 (quelle che permettono T1/T2)
        if (currentState.isT1OnlyMode) return

        // Interrompi il timer se è in esecuzione
        timerHandler?.removeCallbacks(timerRunnable ?: return)

        // Passa all'altro timer e mette in pausa se era in esecuzione
        val newState = currentState.copy(
            isT1Active = !currentState.isT1Active,
            currentTimer = if (currentState.isT1Active) currentState.timerT2 else currentState.timerT1,
            isRunning = false,
            isPaused = false,
            isExpired = false
        )

        _timerState.value = newState
    }

    /**
     * Avvia il timer
     */
    private fun startTimer() {
        val currentState = _timerState.value ?: return

        // Determina il timer da avviare (attuale o predefinito)
        val startTimeSeconds = if (currentState.isExpired || (!currentState.isRunning && !currentState.isPaused)) {
            // Se il timer è scaduto o non è mai stato avviato, usa T1 o T2 in base allo stato
            if (currentState.isT1Active) currentState.timerT1 else currentState.timerT2
        } else {
            // Altrimenti usa il valore corrente
            currentState.currentTimer
        }

        // Aggiorna lo stato
        _timerState.value = currentState.copy(
            currentTimer = startTimeSeconds,
            isRunning = true,
            isPaused = false,
            isExpired = false
        )

        // Avvia il countdown
        startCountdown(startTimeSeconds)

        // Invia lo stato al server
        sendTimerStatusToServer()
    }

    /**
     * Mette in pausa il timer
     */
    private fun pauseTimer() {
        timerHandler?.removeCallbacks(timerRunnable ?: return)

        val currentState = _timerState.value ?: return

        if (currentState.buzzerEnabled) {
            soundPool.play(soundPause, 1.0f, 1.0f, 1, 0, 1.0f)
        }

        _timerState.value = currentState.copy(
            isRunning = true,
            isPaused = true
        )

        // Invia lo stato al server
        sendTimerStatusToServer()
    }

    /**
     * Riprende il timer dalla pausa
     */
    private fun resumeTimer() {
        val currentState = _timerState.value ?: return

        _timerState.value = currentState.copy(
            isRunning = true,
            isPaused = false
        )

        startCountdown(currentState.currentTimer)

        // Invia lo stato al server
        sendTimerStatusToServer()
    }

    /**
     * Resetta il timer
     * @param autoStart Se true, il timer viene avviato subito dopo il reset
     */
    private fun resetTimer(autoStart: Boolean) {
        timerHandler?.removeCallbacks(timerRunnable ?: return)

        val currentState = _timerState.value ?: return
        val resetToSeconds = if (currentState.isT1Active) currentState.timerT1 else currentState.timerT2

        _timerState.value = currentState.copy(
            currentTimer = resetToSeconds,
            isRunning = autoStart,
            isPaused = false,
            isExpired = false
        )

        if (autoStart) {
            startCountdown(resetToSeconds)
        }

        // Invia lo stato al server
        sendTimerStatusToServer()
    }



    /**
     * Gestisce un comando SEAT_OPEN ricevuto dal server o da un'azione dell'utente
     */
    fun handleSeatOpenCommand(seats: String) {
        // Poiché PokerTimerState non ha un campo pendingCommand,
        // dobbiamo utilizzare un approccio diverso.
        // L'informazione sui posti liberi sarà gestita lato server,
        // e refreshFromServer() recupererà queste informazioni.

        // Invia subito una richiesta al server per aggiornare lo stato
        refreshFromServer()

        // Mostra un messaggio di conferma
        // Nota: questo non è il modo ideale di mostrare messaggi UI dal ViewModel
        // ma per semplicità lo facciamo qui. In un'implementazione migliore,
        // si utilizzerebbe un LiveData<Event<String>> per gli eventi UI.
        Log.d("PokerTimerViewModel", "Posti liberi aggiornati: $seats")
    }

    /**
     * Avvia il countdown effettivo
     */
    private fun startCountdown(timeSeconds: Int) {
        // Ferma eventuali timer in esecuzione
        timerHandler?.removeCallbacks(timerRunnable ?: return)

        // Inizializza lo stato
        var secondsRemaining = timeSeconds

        // Crea un nuovo handler
        timerHandler = Handler(Looper.getMainLooper())

        // Crea il runnable che aggiornerà il timer ogni secondo
        timerRunnable = object : Runnable {
            override fun run() {
                val currentState = _timerState.value ?: return

                if (secondsRemaining >= 0) {
                    // Aggiorna lo stato con i secondi rimanenti
                    _timerState.value = currentState.copy(currentTimer = secondsRemaining)

                    // Riproduci suono tick a 10, 5, 4, 3, 2, 1 secondi
                    if ((secondsRemaining <= 5 || secondsRemaining == 10) && currentState.buzzerEnabled) {
                        soundPool.play(soundTick, 1.0f, 1.0f, 1, 0, 1.0f)
                    }

                    // Invia lo stato al server ogni 5 secondi
                    if (secondsRemaining % 5 == 0 || secondsRemaining <= 5) {
                        sendTimerStatusToServer()
                    }

                    // Decrementa il contatore
                    secondsRemaining--

                    // Pianifica la prossima esecuzione tra 1 secondo
                    timerHandler?.postDelayed(this, 1000)
                } else {
                    // Timer terminato
                    if (currentState.buzzerEnabled) {
                        soundPool.play(soundEnd, 1.0f, 1.0f, 1, 0, 1.0f)
                    }

                    _timerState.value = currentState.copy(
                        currentTimer = 0,
                        isRunning = false,
                        isPaused = false,
                        isExpired = true
                    )

                    // Invia lo stato al server
                    sendTimerStatusToServer()
                }
            }
        }

        // Avvia immediatamente il timer
        timerRunnable?.run()
    }
    /**
     * Invia lo stato del timer al server
     */
    private fun sendTimerStatusToServer() {
        val currentState = _timerState.value ?: return

        if (currentState.serverUrl.isNotEmpty()) {
            CoroutineScope(Dispatchers.Main).launch {
                try {
                    val (success, command) = networkManager.sendTimerStatus(currentState.serverUrl, currentState)

                    // Aggiorna lo stato di connessione
                    _timerState.value = currentState.copy(isConnectedToServer = success)

                    // Gestisci il comando ricevuto dal server
                    if (success && command != null) {
                        when (command) {
                            is Command.START -> {
                                if (!currentState.isRunning || currentState.isPaused) {
                                    startTimer()
                                }
                            }
                            is Command.PAUSE -> {
                                if (currentState.isRunning && !currentState.isPaused) {
                                    pauseTimer()
                                }
                            }
                            is Command.RESET -> {
                                resetTimer(currentState.isAutoStartMode)
                            }
                            // MODIFICA QUESTO CASO:
                            is Command.SEAT_OPEN -> {
                                // Invece di cercare di aggiornare direttamente lo stato,
                                // aggiorniamo i dati dal server
                                refreshFromServer()
                                Log.d("PokerTimerViewModel", "Ricevuto comando SEAT_OPEN: ${command.seats}")
                            }
                            is Command.SETTINGS -> {
                                // Aggiorna le impostazioni
                                saveSettings(
                                    timerT1 = command.t1,
                                    timerT2 = command.t2,
                                    operationMode = command.mode,
                                    buzzerEnabled = command.buzzerEnabled,
                                    tableNumber = command.tableNumber,
                                    serverUrl = currentState.serverUrl
                                )
                            }
                        }
                    }
                } catch (e: Exception) {
                    _timerState.value = currentState.copy(isConnectedToServer = false)
                }
            }
        }
    }

    /**
     * Testa la connessione al server
     */
    fun testServerConnection(serverUrl: String, callback: (Boolean) -> Unit) {
        CoroutineScope(Dispatchers.Main).launch {
            try {
                val success = networkManager.testConnection(serverUrl)
                callback(success)
            } catch (e: Exception) {
                callback(false)
            }
        }
    }

    /**
     * Gestione del pulsante Stop
     */
    /**
     * Gestione del pulsante Stop
     */
    fun onStopPressed() {
        timerHandler?.removeCallbacks(timerRunnable ?: return)

        val currentState = _timerState.value ?: return

        // Resetta al valore iniziale del timer attivo
        val resetToSeconds = if (currentState.isT1Active) currentState.timerT1 else currentState.timerT2

        _timerState.value = currentState.copy(
            currentTimer = resetToSeconds, // Imposta al valore iniziale
            isRunning = false,
            isPaused = false,
            isExpired = false
        )

        // Invia lo stato al server
        sendTimerStatusToServer()
    }

    /**
     * Salva le impostazioni del timer
     */
    /**
     * Salva le impostazioni del timer
     */
    /**
     * Salva le impostazioni del timer
     */
    fun saveSettings(timerT1: Int, timerT2: Int, operationMode: Int, buzzerEnabled: Boolean,
                     tableNumber: Int, serverUrl: String) {

        preferences.saveTimerSettings(
            timerT1,
            timerT2,
            operationMode,
            buzzerEnabled,
            tableNumber,
            serverUrl
        )

        val currentState = _timerState.value ?: return

        // Controlla se dobbiamo avviare o fermare il polling
        if (serverUrl.isNotEmpty() && (currentState.serverUrl.isEmpty() || currentState.serverUrl != serverUrl)) {
            // Nuovo URL del server o URL cambiato, avvia il polling
            startServerPolling()
        } else if (serverUrl.isEmpty() && currentState.serverUrl.isNotEmpty()) {
            // URL del server rimosso, ferma il polling
            stopServerPolling()
        }

        // Aggiorna lo stato con le nuove impostazioni
        _timerState.value = currentState.copy(
            timerT1 = timerT1,
            timerT2 = timerT2,
            operationMode = operationMode,
            buzzerEnabled = buzzerEnabled,
            tableNumber = tableNumber,
            serverUrl = serverUrl,
            // Aggiorna anche il timer corrente se necessario
            currentTimer = if (!currentState.isRunning && !currentState.isPaused) {
                if (currentState.isT1Active) timerT1 else timerT2
            } else {
                currentState.currentTimer
            }
        )

        // Invia IMMEDIATAMENTE il nuovo stato al server, indipendentemente dall'URL precedente
        if (serverUrl.isNotEmpty()) {
            CoroutineScope(Dispatchers.Main).launch {
                sendTimerStatusToServer()
            }
        }
    }


    override fun onCleared() {
        super.onCleared()
        timerHandler?.removeCallbacks(timerRunnable ?: return)
        stopServerPolling()
        soundPool.release()
    }

    /**
     * Avvia il polling del server per ricevere aggiornamenti
     */
    private fun startServerPolling() {
        // Ferma eventuali job in corso
        stopServerPolling()

        // Avvia un nuovo job per il polling
        serverPollingJob = CoroutineScope(Dispatchers.Main).launch {
            while (true) {
                // Invia lo stato al server e gestisci eventuali comandi
                sendTimerStatusToServer()

                // Attendi prima del prossimo polling
                delay(2000) // Polling ogni 2 secondi
            }
        }
    }

    /**
     * Ferma il polling del server
     */
    private fun stopServerPolling() {
        serverPollingJob?.cancel()
        serverPollingJob = null
    }
}


