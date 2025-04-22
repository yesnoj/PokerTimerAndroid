package com.example.pokertimer

import android.app.AlertDialog
import android.app.Dialog
import android.app.ProgressDialog
import android.content.Context
import android.content.Intent
import android.content.res.Configuration
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.util.Log
import android.view.GestureDetector
import android.view.LayoutInflater
import android.view.MotionEvent
import android.view.View
import android.view.WindowManager
import android.widget.Button
import android.widget.EditText
import android.widget.ImageButton
import android.widget.LinearLayout
import android.widget.RadioButton
import android.widget.RadioGroup
import android.widget.Switch
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.core.view.GestureDetectorCompat
import androidx.lifecycle.Observer
import androidx.lifecycle.ViewModelProvider
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import java.net.DatagramPacket
import java.net.DatagramSocket
import java.net.InetAddress
import java.net.SocketTimeoutException
import kotlin.math.abs
import androidx.core.content.ContextCompat
import android.graphics.Color
import android.graphics.drawable.ColorDrawable
import android.os.Vibrator
import android.os.VibrationEffect
import android.os.Build
import android.view.Window
import kotlinx.coroutines.delay
import kotlinx.coroutines.withContext
import java.net.HttpURLConnection
import java.net.URL
import android.content.pm.ActivityInfo


class MainActivity : AppCompatActivity(), GestureDetector.OnGestureListener, GestureDetector.OnDoubleTapListener {

    private lateinit var binding: MainActivityBinding
    private lateinit var viewModel: PokerTimerViewModel
    private val selectedPlayerSeats = mutableListOf<Int>()
    private lateinit var gestureDetector: GestureDetectorCompat
    private var isActionBarVisible = true

    // Costanti per la gestione dei gesti
    companion object {
        private const val SWIPE_THRESHOLD = 100
        private const val SWIPE_VELOCITY_THRESHOLD = 100
        private const val DISCOVERY_PORT = 8888
        private const val DISCOVERY_TIMEOUT_MS = 3000
        private const val TAG = "MainActivity"
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        // Forza l'orientamento landscape
        requestedOrientation = ActivityInfo.SCREEN_ORIENTATION_LANDSCAPE

        super.onCreate(savedInstanceState)

        // Nascondi la barra delle notifiche (status bar)
        window.setFlags(
            WindowManager.LayoutParams.FLAG_FULLSCREEN,
            WindowManager.LayoutParams.FLAG_FULLSCREEN
        )

        // Nascondi l'action bar
        supportActionBar?.hide()

        // Usa sempre il layout landscape
        setContentView(R.layout.activity_main_landscape)

        // Inizializza il binding personalizzato
        binding = MainActivityBinding.bind(this)

        // Inizializza il ViewModel
        viewModel = ViewModelProvider(this)[PokerTimerViewModel::class.java]

        // Osserva i cambiamenti di stato del timer
        observeTimerState()

        // Inizializza il detector dei gesti
        gestureDetector = GestureDetectorCompat(this, this)
        gestureDetector.setOnDoubleTapListener(this)

        // Configura il gestore dei tocchi sul layout principale
        val mainContainer = findViewById<View>(R.id.main_container)
        mainContainer.setOnTouchListener { _, event ->
            gestureDetector.onTouchEvent(event)
        }

        // Imposta il long press per accedere alle impostazioni
        setupLongPressForSettings()

        // Bottone per selezionare i giocatori (l'unico bottone che rimane)
        binding.btnPlayersSelection.setOnClickListener {
            showPlayerSelectionDialog()
        }
    }

    private fun observeTimerState() {
        viewModel.timerState.observe(this) { state ->
            updateTimerDisplay(state)
        }
    }

    private fun updateTimerDisplay(state: PokerTimerState) {
        // Aggiorna il contatore del timer
        binding.tvTimer.text = state.currentTimer.toString()
        binding.tvTableNumber.text = getString(R.string.table_format, state.tableNumber)

        // Aggiorna quale timer è attivo (T1/T2)
        binding.tvActiveTimer.text = getString(
            if (state.isT1Active) R.string.timer_t1 else R.string.timer_t2
        )

        // Aggiorna lo stato del timer
        val statusText = when {
            state.isExpired -> getString(R.string.status_expired)
            state.isPaused -> getString(R.string.status_paused)
            state.isRunning -> getString(R.string.status_running)
            else -> getString(R.string.status_stopped)
        }
        binding.tvTimerStatus.text = statusText

        // Colore dello stato
        val statusColor = when {
            state.isExpired -> getColor(R.color.error_color)
            state.isPaused -> getColor(R.color.secondary_color)
            state.isRunning -> getColor(R.color.status_color)
            else -> getColor(R.color.white)
        }
        binding.tvTimerStatus.setTextColor(statusColor)
    }

    override fun onConfigurationChanged(newConfig: Configuration) {
        super.onConfigurationChanged(newConfig)

        // Manteniamo sempre il layout landscape, quindi non è necessario cambiare layout
        // Ma dobbiamo reinizializzare alcuni elementi

        // Re-inizializza il binding
        binding = MainActivityBinding.bind(this)

        // Ricollega il gestore dei tocchi
        val mainContainer = findViewById<View>(R.id.main_container)
        mainContainer.setOnTouchListener { _, event ->
            gestureDetector.onTouchEvent(event)
        }

        // Configura il pulsante per i giocatori
        binding.btnPlayersSelection.setOnClickListener {
            showPlayerSelectionDialog()
        }

        // Se il viewModel e lo stato sono già inizializzati, aggiorna la UI
        viewModel.timerState.value?.let {
            updateTimerDisplay(it)
        }
    }

    // Implementazione dei metodi di GestureDetector.OnGestureListener
    override fun onDown(e: MotionEvent): Boolean {
        return true
    }

    override fun onShowPress(e: MotionEvent) {
        // Non facciamo nulla qui
    }

    override fun onSingleTapUp(e: MotionEvent): Boolean {
        val currentState = viewModel.timerState.value ?: return false

        // Se il timer è in pausa, lo riprende
        if (currentState.isPaused) {
            viewModel.onStartPausePressed()
            return true
        }

        // Se il timer è fermo o scaduto, lo avvia
        if (!currentState.isRunning || currentState.isExpired) {
            viewModel.onStartPausePressed()
            return true
        }

        // Se il timer è in esecuzione, lo resetta e lo riavvia immediatamente
        if (currentState.isRunning && !currentState.isPaused) {
            // Resetta e avvia immediatamente dopo
            viewModel.resetAndStartTimer()
            return true
        }

        return false
    }

    override fun onScroll(e1: MotionEvent?, e2: MotionEvent, distanceX: Float, distanceY: Float): Boolean {
        return false
    }

    override fun onLongPress(e: MotionEvent) {
        val currentState = viewModel.timerState.value ?: return

        // Aggiungi vibrazione
        val vibrator = getSystemService(Context.VIBRATOR_SERVICE) as Vibrator
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            vibrator.vibrate(VibrationEffect.createOneShot(50, VibrationEffect.DEFAULT_AMPLITUDE))
        } else {
            // Per API inferiori a 26
            @Suppress("DEPRECATION")
            vibrator.vibrate(50)
        }

        // Se il timer è in esecuzione, lo mette in pausa
        if (currentState.isRunning && !currentState.isPaused) {
            viewModel.onStartPausePressed()
        }

        // Mostra il dialog delle impostazioni
        showSettingsDialog()
    }

    override fun onFling(e1: MotionEvent?, e2: MotionEvent, velocityX: Float, velocityY: Float): Boolean {
        val diffX = e2.x - (e1?.x ?: 0f)
        val diffY = e2.y - (e1?.y ?: 0f)

        // Verifica che sia uno swipe orizzontale
        if (abs(diffX) > abs(diffY) &&
            abs(diffX) > SWIPE_THRESHOLD &&
            abs(velocityX) > SWIPE_VELOCITY_THRESHOLD) {

            val currentState = viewModel.timerState.value ?: return false

            // Switcha tra T1 e T2
            viewModel.onSwitchPressed()

            // Se è in esecuzione, lo ferma
            if (currentState.isRunning) {
                viewModel.stopTimer()
            }

            return true
        }

        return false
    }

    // Implementazione dei metodi di GestureDetector.OnDoubleTapListener
    override fun onSingleTapConfirmed(e: MotionEvent): Boolean {
        // Già gestito in onSingleTapUp
        return false
    }

    override fun onDoubleTap(e: MotionEvent): Boolean {
        // Con doppio tap, torna a T1 o T2 e rimane fermo
        viewModel.resetTimerWithoutAutostart()
        return true
    }

    override fun onDoubleTapEvent(e: MotionEvent): Boolean {
        return false
    }

    private fun setupLongPressForSettings() {
        // Già gestito in onLongPress del GestureDetector
    }

    private fun showPlayerSelectionDialog() {
        // Crea il dialogo
        val dialog = Dialog(this)
        dialog.setContentView(R.layout.dialog_player_selection)

        // Imposta la larghezza del dialogo
        val window = dialog.window
        window?.setLayout(WindowManager.LayoutParams.MATCH_PARENT, WindowManager.LayoutParams.WRAP_CONTENT)

        // Ottieni il numero del tavolo corrente
        val currentState = viewModel.timerState.value
        val tableNumber = currentState?.tableNumber ?: 1

        // Verifica se ci sono posti già selezionati
        val existingSeats = viewModel.getExistingSeats()

        // Resetta e carica le selezioni precedenti
        selectedPlayerSeats.clear()
        selectedPlayerSeats.addAll(existingSeats)

        // Lista dei bottoni dei giocatori
        val playerButtons = listOf(
            dialog.findViewById<Button>(R.id.playerButton1),
            dialog.findViewById<Button>(R.id.playerButton2),
            dialog.findViewById<Button>(R.id.playerButton3),
            dialog.findViewById<Button>(R.id.playerButton4),
            dialog.findViewById<Button>(R.id.playerButton5),
            dialog.findViewById<Button>(R.id.playerButton6),
            dialog.findViewById<Button>(R.id.playerButton7),
            dialog.findViewById<Button>(R.id.playerButton8),
            dialog.findViewById<Button>(R.id.playerButton9),
            dialog.findViewById<Button>(R.id.playerButton10)
        )

        // Configura i listener per i bottoni dei giocatori e preseleziona posti esistenti
        playerButtons.forEachIndexed { index, button ->
            val playerNumber = index + 1

            // Preseleziona posti esistenti
            if (selectedPlayerSeats.contains(playerNumber)) {
                button.isSelected = true
            }

            button.setOnClickListener {
                togglePlayerSelection(playerNumber, button)
            }
        }

        // Configura i listener per i pulsanti di azione
        val sendButton = dialog.findViewById<Button>(R.id.sendButton)
        val cancelButton = dialog.findViewById<Button>(R.id.cancelButton)

        sendButton.setOnClickListener {
            // Verifica se ci sono posti selezionati
            if (selectedPlayerSeats.isEmpty()) {
                Toast.makeText(this, "Nessun posto selezionato", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }

            // Crea l'oggetto richiesta
            val seatRequest = PlayerSeatRequest(tableNumber, selectedPlayerSeats)

            // Invia la richiesta al server
            sendSeatRequestToServer(seatRequest)

            // MODIFICA: Salva una copia vuota nel ViewModel per deselezionare tutti i posti
            viewModel.saveSelectedSeats(emptyList())

            // MODIFICA: Svuota la lista locale
            selectedPlayerSeats.clear()

            // Chiudi il dialogo
            dialog.dismiss()

            // MODIFICA: Mostra una conferma all'utente
            //Toast.makeText(this, "Posti inviati e deselezionati", Toast.LENGTH_SHORT).show()
        }

        cancelButton.setOnClickListener {
            // Ripristina la lista originale
            selectedPlayerSeats.clear()
            selectedPlayerSeats.addAll(existingSeats)

            // Chiudi il dialogo senza inviare nulla
            dialog.dismiss()
        }

        dialog.show()

        // Cambia il colore del pulsante Cancel a bianco
        cancelButton.setTextColor(Color.WHITE)
    }

    private fun showSettingsDialog() {
        val dialogView = layoutInflater.inflate(R.layout.dialog_settings, null)
        val currentState = viewModel.timerState.value ?: return

        // Creiamo un dialog completamente personalizzato invece di un AlertDialog
        val dialog = Dialog(this)
        dialog.requestWindowFeature(Window.FEATURE_NO_TITLE)
        dialog.setContentView(dialogView)
        dialog.window?.setBackgroundDrawable(ColorDrawable(Color.TRANSPARENT))

        // Imposta le dimensioni del dialogo
        val layoutParams = WindowManager.LayoutParams()
        layoutParams.copyFrom(dialog.window?.attributes)
        layoutParams.width = WindowManager.LayoutParams.MATCH_PARENT
        layoutParams.height = WindowManager.LayoutParams.WRAP_CONTENT
        dialog.window?.attributes = layoutParams

        // Inizializza le viste del dialogo
        val timerT1Value = dialogView.findViewById<TextView>(R.id.tv_t1_value)
        val timerT2Value = dialogView.findViewById<TextView>(R.id.tv_t2_value)

        val decreaseT1Button = dialogView.findViewById<Button>(R.id.btn_decrease_t1)
        val increaseT1Button = dialogView.findViewById<Button>(R.id.btn_increase_t1)
        val decreaseT2Button = dialogView.findViewById<Button>(R.id.btn_decrease_t2)
        val increaseT2Button = dialogView.findViewById<Button>(R.id.btn_increase_t2)

        val buzzerSwitch = dialogView.findViewById<Switch>(R.id.switch_buzzer)

        // Valori per table_number
        val tableNumberText = dialogView.findViewById<TextView>(R.id.tv_table_number)
        var tableNumber = currentState.tableNumber
        tableNumberText.text = tableNumber.toString()

        val decreaseTableButton = dialogView.findViewById<Button>(R.id.btn_decrease_table)
        val increaseTableButton = dialogView.findViewById<Button>(R.id.btn_increase_table)

        // Nuovo: Valori per players_number
        val playersNumberText = dialogView.findViewById<TextView>(R.id.tv_players_number)
        var playersCount = currentState.playersCount
        playersNumberText.text = playersCount.toString()

        val decreasePlayersButton = dialogView.findViewById<Button>(R.id.btn_decrease_players)
        val increasePlayersButton = dialogView.findViewById<Button>(R.id.btn_increase_players)

        // Server URL e pulsanti di connessione
        val serverUrlInput = dialogView.findViewById<EditText>(R.id.et_server_url)
        val connectButton = dialogView.findViewById<Button>(R.id.btn_connect)
        val disconnectButton = dialogView.findViewById<Button>(R.id.btn_disconnect)

        // Pulsanti personalizzati
        val saveButton = dialogView.findViewById<Button>(R.id.custom_save_button)
        val cancelButton = dialogView.findViewById<Button>(R.id.custom_cancel_button)

        // Header dello stato del server
        val serverStatusHeader = dialogView.findViewById<TextView>(R.id.server_status_header)
        updateServerStatusHeader(serverStatusHeader, currentState.isConnectedToServer)

        // Riferimento al pulsante di discovery
        val discoverButton = dialogView.findViewById<Button>(R.id.btn_discover_server)

        // Valori T1 e T2
        var t1Value = currentState.timerT1
        var t2Value = currentState.timerT2
        timerT1Value.text = "${t1Value}s"
        timerT2Value.text = "${t2Value}s"

        // Stato buzzer
        buzzerSwitch.isChecked = currentState.buzzerEnabled

        // Imposta l'URL del server nel campo di testo
        serverUrlInput.setText(currentState.serverUrl)

        // Listener per i pulsanti di incremento/decremento di table_number
        decreaseTableButton.setOnClickListener {
            if (tableNumber > 0) {
                tableNumber--
                tableNumberText.text = tableNumber.toString()
            }
        }

        increaseTableButton.setOnClickListener {
            if (tableNumber < 99) {
                tableNumber++
                tableNumberText.text = tableNumber.toString()
            }
        }

        // Listener per i pulsanti di incremento/decremento del numero di giocatori
        decreasePlayersButton.setOnClickListener {
            if (playersCount > 1) {
                playersCount--
                playersNumberText.text = playersCount.toString()
            }
        }

        increasePlayersButton.setOnClickListener {
            if (playersCount < 10) {
                playersCount++
                playersNumberText.text = playersCount.toString()
            }
        }

        // Listener per i pulsanti di incremento/decremento di T1
        decreaseT1Button.setOnClickListener {
            if (t1Value > 5) {
                t1Value -= 5
                timerT1Value.text = "${t1Value}s"
            }
        }

        increaseT1Button.setOnClickListener {
            if (t1Value < 95) {
                t1Value += 5
                timerT1Value.text = "${t1Value}s"
            }
        }

        // Listener per i pulsanti di incremento/decremento di T2
        decreaseT2Button.setOnClickListener {
            if (t2Value > 5) {
                t2Value -= 5
                timerT2Value.text = "${t2Value}s"
            }
        }

        increaseT2Button.setOnClickListener {
            if (t2Value < 95) {
                t2Value += 5
                timerT2Value.text = "${t2Value}s"
            }
        }

        // Listener per il pulsante Connetti
        connectButton.setOnClickListener {
            val serverUrl = serverUrlInput.text.toString()
            if (serverUrl.isNotEmpty()) {
                // Disabilita temporaneamente i pulsanti durante il test
                connectButton.isEnabled = false
                disconnectButton.isEnabled = false
                connectButton.text = getString(R.string.testing)

                // Log aggiunto
                Log.d("MainActivity", "Avvio test connessione su URL: $serverUrl")

                viewModel.testServerConnection(serverUrl) { success ->
                    // Torna al thread principale
                    runOnUiThread {
                        // Log aggiunto
                        Log.d("MainActivity", "Risultato test connessione: $success")

                        // Aggiorna i pulsanti in base al risultato
                        updateConnectionButtonsState(disconnectButton, connectButton, success)

                        // Mostra il risultato del test
                        val message = if (success) R.string.connection_success else R.string.connection_failed
                        Toast.makeText(this, message, Toast.LENGTH_SHORT).show()

                        // Se la connessione è riuscita, aggiorna lo stato
                        if (success) {
                            // Log aggiunto
                            Log.d("MainActivity", "Aggiornamento stato connessione a true")

                            // Aggiorna l'header dello stato
                            updateServerStatusHeader(serverStatusHeader, true)
                        }
                    }
                }
            } else {
                Toast.makeText(this, R.string.enter_server_url, Toast.LENGTH_SHORT).show()
            }
        }

        // Listener per il pulsante Disconnetti
        disconnectButton.setOnClickListener {
            // Aggiorna lo stato di connessione nel ViewModel
            viewModel.stopServerPolling()

            // Aggiorna i pulsanti e l'header
            updateConnectionButtonsState(disconnectButton, connectButton, false)
            updateServerStatusHeader(serverStatusHeader, false)

            // Mostra un messaggio di conferma
            Toast.makeText(this, "Disconnesso dal server", Toast.LENGTH_SHORT).show()
        }

        // Listener per il pulsante di discovery
        discoverButton.setOnClickListener {
            discoverServers(serverUrlInput)
        }

        // Listener per il pulsante Salva
        saveButton.setOnClickListener {
            // Salva le impostazioni usando sempre la modalità 1 (l'unica disponibile ora)
            viewModel.saveSettings(
                timerT1 = t1Value,
                timerT2 = t2Value,
                operationMode = 1, // Manteniamo solo la modalità 1
                buzzerEnabled = buzzerSwitch.isChecked,
                tableNumber = tableNumber,
                serverUrl = serverUrlInput.text.toString(),
                playersCount = playersCount
            )
            dialog.dismiss()
        }

        // Listener per il pulsante Annulla
        cancelButton.setOnClickListener {
            dialog.dismiss()
        }

        // Osserva cambiamenti nello stato del timer mentre il dialogo è aperto
        val serverStatusObserver = Observer<PokerTimerState> { state ->
            // Aggiorna lo stato del server quando cambia
            updateServerStatusHeader(serverStatusHeader, state.isConnectedToServer)
            updateConnectionButtonsState(disconnectButton, connectButton, state.isConnectedToServer)
        }

        // Registra l'observer
        viewModel.timerState.observe(this, serverStatusObserver)

        // Rimuovi l'observer quando il dialogo si chiude
        dialog.setOnDismissListener {
            viewModel.timerState.removeObserver(serverStatusObserver)
        }

        // Mostra il dialogo
        dialog.show()
    }


    private fun updateServerStatusHeader(headerView: TextView, isConnected: Boolean) {
        if (isConnected) {
            headerView.text = "Server: Connesso"
            headerView.setTextColor(getColor(R.color.status_color))
        } else {
            headerView.text = "Server: Disconnesso"
            headerView.setTextColor(getColor(R.color.error_color))
        }
    }

    /**
     * Seleziona/deseleziona un posto giocatore
     */
    private fun togglePlayerSelection(playerNumber: Int, button: Button) {
        if (selectedPlayerSeats.contains(playerNumber)) {
            // Deseleziona
            selectedPlayerSeats.remove(playerNumber)
            button.isSelected = false

            // Ottengo il numero del tavolo corrente
            val currentState = viewModel.timerState.value
            val tableNumber = currentState?.tableNumber ?: 1

            // Invia immediatamente la nuova lista di posti al server
            val seatRequest = PlayerSeatRequest(tableNumber, selectedPlayerSeats)

            // Inviamo la richiesta solo se ci sono posti, altrimenti facciamo un reset
            if (selectedPlayerSeats.isNotEmpty()) {
                // Aggiorna i posti selezionati sul server senza chiudere il dialog
                sendSeatRequestToServerSilent(seatRequest)
            } else {
                // Se non ci sono più posti selezionati, possiamo fare una richiesta di reset
                resetSeatInfoSilent(tableNumber)
            }
        } else {
            // Seleziona
            selectedPlayerSeats.add(playerNumber)
            button.isSelected = true
        }
    }

    /**
     * Invia una richiesta di posti liberi al server senza dialoghi
     */
    private fun sendSeatRequestToServerSilent(seatRequest: PlayerSeatRequest) {
        val currentState = viewModel.timerState.value
        val serverUrl = currentState?.serverUrl ?: return

        // Utilizza una coroutine per la chiamata di rete
        CoroutineScope(Dispatchers.Main).launch {
            try {
                // NetworkManager è già presente nel progetto
                val networkManager = NetworkManager(applicationContext)

                // Invia la richiesta usando il NetworkManager
                val success = networkManager.sendSeatRequest(serverUrl, seatRequest)

                if (success) {
                    // Salva i posti selezionati nel ViewModel
                    viewModel.saveSelectedSeats(seatRequest.selectedSeats)

                    // Aggiungi un ritardo prima di refreshare per dare tempo al server di elaborare
                    delay(500)

                    // Forza un refresh della dashboard
                    val refreshUrl = URL("$serverUrl/api/timers")
                    withContext(Dispatchers.IO) {
                        try {
                            val connection = refreshUrl.openConnection() as HttpURLConnection
                            connection.requestMethod = "GET"
                            val responseCode = connection.responseCode
                            Log.d("MainActivity", "Force refresh response: $responseCode")
                            connection.disconnect()
                        } catch (e: Exception) {
                            Log.e("MainActivity", "Error forcing refresh: ${e.message}")
                        }
                    }
                }
            } catch (e: Exception) {
                Log.e("MainActivity", "Errore: ${e.message}", e)
            }
        }
    }

    /**
     * Invia una richiesta di reset posti al server senza dialoghi
     */
    private fun resetSeatInfoSilent(tableNumber: Int) {
        val currentState = viewModel.timerState.value
        val serverUrl = currentState?.serverUrl ?: return

        // Utilizza una coroutine per la chiamata di rete
        CoroutineScope(Dispatchers.Main).launch {
            try {
                // NetworkManager è già presente nel progetto
                val networkManager = NetworkManager(applicationContext)

                // Invia la richiesta di reset
                val success = networkManager.resetSeatInfo(serverUrl, tableNumber)

                if (success) {
                    // Resetta i posti selezionati nel ViewModel
                    viewModel.saveSelectedSeats(emptyList())
                }
            } catch (e: Exception) {
                Log.e("MainActivity", "Errore reset posti: ${e.message}", e)
            }
        }
    }
    /**
     * Aggiorna lo stato dei pulsanti di connessione in base allo stato attuale
     */
    private fun updateConnectionButtonsState(disconnectButton: Button, connectButton: Button, isConnected: Boolean) {
        if (isConnected) {
            // Se connesso:
            // 1. Abilita il pulsante Disconnetti
            disconnectButton.isEnabled = true

            // 2. Modifica l'aspetto del pulsante Connetti per sembrare premuto:
            // - Cambia il testo
            connectButton.text = "Connesso"
            // - Disabilitalo per evitare interazioni
            connectButton.isEnabled = false
            // - Cambia il colore di sfondo a un colore più scuro per sembrare premuto
            connectButton.backgroundTintList = ContextCompat.getColorStateList(connectButton.context, R.color.primary_dark_color)
            // - Aggiunge una leggera elevazione "interna" (valore negativo)
            connectButton.elevation = 0f
            // - Opzionalmente, aggiungi un'icona di spunta accanto al testo
            connectButton.setCompoundDrawablesWithIntrinsicBounds(R.drawable.ic_check, 0, 0, 0)
            connectButton.compoundDrawablePadding = 8
        } else {
            // Se disconnesso:
            // 1. Disabilita il pulsante Disconnetti
            disconnectButton.isEnabled = false

            // 2. Ripristina l'aspetto normale del pulsante Connetti:
            connectButton.text = "Connetti"
            connectButton.isEnabled = true
            // - Ripristina il colore di sfondo originale
            connectButton.backgroundTintList = ContextCompat.getColorStateList(connectButton.context, R.color.status_color)
            // - Ripristina l'elevazione normale
            connectButton.elevation = 4f
            // - Rimuovi icone
            connectButton.setCompoundDrawablesWithIntrinsicBounds(0, 0, 0, 0)
        }
    }

    /**
     * Invia una richiesta di posti liberi al server
     */
    private fun sendSeatRequestToServer(seatRequest: PlayerSeatRequest) {
        // Mostra un toast per indicare che la richiesta è in corso
        val message = "Invio richiesta posti: ${seatRequest.getFormattedSeats()}"
        Toast.makeText(this, message, Toast.LENGTH_SHORT).show()

        val currentState = viewModel.timerState.value
        val serverUrl = currentState?.serverUrl ?: return

        // Utilizza una coroutine per la chiamata di rete
        CoroutineScope(Dispatchers.Main).launch {
            try {
                // NetworkManager è già presente nel progetto
                val networkManager = NetworkManager(applicationContext)

                // Invia la richiesta usando il NetworkManager
                val success = networkManager.sendSeatRequest(serverUrl, seatRequest)

                // Gestisci la risposta
                if (success) {
                    Toast.makeText(applicationContext, "Richiesta inviata con successo", Toast.LENGTH_SHORT).show()

                    // Salva i posti selezionati nel ViewModel
                    viewModel.saveSelectedSeats(seatRequest.selectedSeats)

                    // Aggiorna le informazioni localmente
                    if (currentState != null) {
                        val newState = currentState.copy()
                        viewModel.updateState(newState)
                    }
                } else {
                    Toast.makeText(applicationContext, "Errore nell'invio della richiesta", Toast.LENGTH_SHORT).show()
                }
            } catch (e: Exception) {
                Log.e("MainActivity", "Errore: ${e.message}", e)
                Toast.makeText(applicationContext, "Errore: ${e.message}", Toast.LENGTH_SHORT).show()
            }
        }
    }
    /**
     * Cerca server disponibili sulla rete locale tramite UDP broadcast
     */
    private fun discoverServers(serverUrlField: EditText) {
        // Mostra un indicatore di progresso
        val progressDialog = ProgressDialog(this).apply {
            setMessage("Ricerca server in corso...")
            setCancelable(false)
            show()
        }

        Thread {
            try {
                // Crea un socket per il broadcast
                val socket = DatagramSocket()
                socket.broadcast = true

                // Crea il messaggio di discovery
                val message = "POKER_TIMER_DISCOVERY".toByteArray()
                val packet = DatagramPacket(
                    message,
                    message.size,
                    InetAddress.getByName("255.255.255.255"),
                    DISCOVERY_PORT
                )

                Log.d(TAG, "Sending discovery broadcast")

                // Invia il broadcast
                socket.send(packet)

                // Prepara per ricevere le risposte
                val buffer = ByteArray(1024)
                val responsePacket = DatagramPacket(buffer, buffer.size)

                // Imposta un timeout
                socket.soTimeout = DISCOVERY_TIMEOUT_MS

                // Lista dei server trovati
                val discoveredServers = mutableListOf<String>()

                try {
                    // Ricezione delle risposte fino al timeout
                    while (true) {
                        socket.receive(responsePacket)
                        val serverResponse = String(responsePacket.data, 0, responsePacket.length)
                        val serverIp = responsePacket.address.hostAddress

                        Log.d(TAG, "Received response: '$serverResponse' from $serverIp")

                        // Verifica la risposta
                        if (serverResponse.trim() == "POKER_TIMER_SERVER") {
                            // Aggiunge l'indirizzo IP e la porta del server Express
                            val serverUrl = "http://$serverIp:3000"
                            Log.d(TAG, "Found server: $serverUrl")

                            // Aggiunge il server alla lista se non è già presente
                            if (!discoveredServers.contains(serverUrl)) {
                                discoveredServers.add(serverUrl)
                            }
                        }
                    }
                } catch (e: SocketTimeoutException) {
                    // Timeout raggiunto, abbiamo finito la discovery
                    Log.d(TAG, "Discovery timeout reached")
                }

                // Chiudi il socket
                socket.close()

                // Aggiorna l'UI sul thread principale
                runOnUiThread {
                    progressDialog.dismiss()

                    if (discoveredServers.isEmpty()) {
                        Toast.makeText(this, "Nessun server trovato", Toast.LENGTH_SHORT).show()
                    } else {
                        showDiscoveredServers(discoveredServers, serverUrlField)
                    }
                }
            } catch (e: Exception) {
                Log.e(TAG, "Error during server discovery", e)

                runOnUiThread {
                    progressDialog.dismiss()
                    Toast.makeText(
                        this,
                        "Errore durante la ricerca: ${e.message}",
                        Toast.LENGTH_SHORT
                    ).show()
                }
            }
        }.start()
    }

    /**
     * Mostra un dialogo con i server scoperti
     */
    private fun showDiscoveredServers(servers: List<String>, serverUrlField: EditText) {
        if (servers.size == 1) {
            // Se è stato trovato un solo server, selezionalo automaticamente
            val serverUrl = servers[0]
            serverUrlField.setText(serverUrl)
            Toast.makeText(this, "Server trovato: $serverUrl", Toast.LENGTH_SHORT).show()
        } else {
            // Mostra una lista di selezione
            val builder = AlertDialog.Builder(this)
            builder.setTitle("Server trovati")

            builder.setItems(servers.toTypedArray()) { _, which ->
                val selectedServer = servers[which]
                serverUrlField.setText(selectedServer)
            }

            builder.setNegativeButton("Annulla", null)
            builder.show()
        }
    }
}