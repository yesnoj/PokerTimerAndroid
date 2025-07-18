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
import androidx.constraintlayout.widget.ConstraintLayout
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

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
        private const val DISCOVERY_TIMEOUT_MS = 8000
        private const val TAG = "MainActivity"
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        // Forza l'orientamento landscape ma permetti la rotazione di 180 gradi
        requestedOrientation = ActivityInfo.SCREEN_ORIENTATION_SENSOR_LANDSCAPE

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

        // Ottieni l'URL del server dall'intent se presente
        val serverUrl = intent.getStringExtra("server_url")
        if (!serverUrl.isNullOrEmpty()) {
            // Se abbiamo un URL del server, connettiti automaticamente
            connectToServerOnStartup(serverUrl)
        }

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

        // Bottone per chiamare il floorman
        binding.btnCallFloorman.setOnClickListener {
            callFloorman()
        }

        // Bottone per servizio bar
        binding.btnBarService.setOnClickListener {
            requestBarService()
        }
    }

    /**
     * Connette automaticamente al server all'avvio se viene fornito un URL
     */
    private fun connectToServerOnStartup(serverUrl: String) {
        Log.d("MainActivity", "Tentativo di connessione automatica al server: $serverUrl")

        // Salva l'URL del server nelle impostazioni
        val currentState = viewModel.timerState.value ?: return

        // Test la connessione
        viewModel.testServerConnection(serverUrl) { success ->
            runOnUiThread {
                if (success) {
                    Log.d("MainActivity", "Connessione automatica riuscita")
                    Toast.makeText(this, "Connesso al server", Toast.LENGTH_SHORT).show()

                    // Salva le impostazioni con il nuovo URL
                    viewModel.saveSettings(
                        timerT1 = currentState.timerT1,
                        timerT2 = currentState.timerT2,
                        operationMode = currentState.operationMode,
                        buzzerEnabled = currentState.buzzerEnabled,
                        tableNumber = currentState.tableNumber,
                        serverUrl = serverUrl,
                        playersCount = currentState.playersCount
                    )
                } else {
                    Log.e("MainActivity", "Connessione automatica fallita")
                    Toast.makeText(this, "Impossibile connettersi al server", Toast.LENGTH_SHORT).show()
                }
            }
        }
    }

    /**
     * Chiama il floorman inviando una notifica al server
     */
    private fun callFloorman() {
        val currentState = viewModel.timerState.value ?: return
        val serverUrl = currentState.serverUrl

        if (serverUrl.isEmpty() || !currentState.isConnectedToServer) {
            Toast.makeText(this, "Non connesso al server", Toast.LENGTH_SHORT).show()
            return
        }

        // Crea il dialog personalizzato
        val dialog = Dialog(this)
        dialog.requestWindowFeature(Window.FEATURE_NO_TITLE)
        dialog.setContentView(R.layout.dialog_floorman)
        dialog.window?.setBackgroundDrawable(ColorDrawable(Color.TRANSPARENT))

        // Imposta le dimensioni del dialogo
        val layoutParams = WindowManager.LayoutParams()
        layoutParams.copyFrom(dialog.window?.attributes)
        layoutParams.width = WindowManager.LayoutParams.WRAP_CONTENT
        layoutParams.height = WindowManager.LayoutParams.WRAP_CONTENT
        dialog.window?.attributes = layoutParams

        // Aggiorna il messaggio con il numero del tavolo
        val messageText = dialog.findViewById<TextView>(R.id.floorman_message)
        messageText.text = "Vuoi chiamare il floorman al tavolo ${currentState.tableNumber}?"

        // Configura i pulsanti
        val cancelButton = dialog.findViewById<Button>(R.id.floorman_cancel_button)
        val callButton = dialog.findViewById<Button>(R.id.floorman_call_button)

        cancelButton.setOnClickListener {
            dialog.dismiss()
        }

        callButton.setOnClickListener {
            dialog.dismiss()
            sendFloormanRequest()
        }

        dialog.show()
    }

    /**
     * Invia la richiesta di floorman al server
     */
    private fun sendFloormanRequest() {
        val currentState = viewModel.timerState.value ?: return
        val serverUrl = currentState.serverUrl

        // Mostra un dialogo di progresso
        val progressDialog = ProgressDialog(this).apply {
            setMessage("Invio richiesta in corso...")
            setCancelable(false)
            show()
        }

        CoroutineScope(Dispatchers.Main).launch {
            try {
                val success = withContext(Dispatchers.IO) {
                    try {
                        val url = URL("$serverUrl/api/floorman_request")
                        val connection = url.openConnection() as HttpURLConnection
                        connection.requestMethod = "POST"
                        connection.doOutput = true
                        connection.setRequestProperty("Content-Type", "application/json; charset=UTF-8")
                        connection.connectTimeout = 5000
                        connection.readTimeout = 5000

                        // Il server si aspetta timestamp come numero, non stringa
                        val jsonPayload = """
                    {
                        "table_number": ${currentState.tableNumber},
                        "timestamp": ${System.currentTimeMillis()}
                    }
                    """.trimIndent()

                        Log.d("MainActivity", "Invio richiesta floorman: $jsonPayload")

                        val outputStream = connection.outputStream
                        outputStream.write(jsonPayload.toByteArray())
                        outputStream.close()

                        val responseCode = connection.responseCode
                        Log.d("MainActivity", "Response code floorman: $responseCode")

                        // Leggi la risposta per debug
                        if (responseCode == HttpURLConnection.HTTP_OK) {
                            val inputStream = connection.inputStream
                            val response = inputStream.bufferedReader().use { it.readText() }
                            Log.d("MainActivity", "Response body floorman: $response")
                        }

                        connection.disconnect()

                        responseCode == HttpURLConnection.HTTP_OK
                    } catch (e: Exception) {
                        Log.e("MainActivity", "Errore chiamata floorman: ${e.message}", e)
                        false
                    }
                }

                progressDialog.dismiss()

                if (success) {
                    Toast.makeText(this@MainActivity, "Floorman chiamato con successo", Toast.LENGTH_SHORT).show()

                    // Effetto visivo sul bottone
                    animateButton(binding.btnCallFloorman)

                    // Vibrazione di conferma
                    val vibrator = getSystemService(Context.VIBRATOR_SERVICE) as Vibrator
                    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                        vibrator.vibrate(VibrationEffect.createOneShot(200, VibrationEffect.DEFAULT_AMPLITUDE))
                    } else {
                        @Suppress("DEPRECATION")
                        vibrator.vibrate(200)
                    }

                    // IMPORTANTE: Aggiorna localmente il pending_command per mostrare subito l'icona
                    viewModel.handleFloormanCallCommand()

                } else {
                    Toast.makeText(this@MainActivity, "Errore nella chiamata al floorman", Toast.LENGTH_SHORT).show()
                }
            } catch (e: Exception) {
                progressDialog.dismiss()
                Log.e("MainActivity", "Errore chiamata floorman: ${e.message}", e)
                Toast.makeText(this@MainActivity, "Errore: ${e.message}", Toast.LENGTH_SHORT).show()
            }
        }
    }
    /**
     * Richiede il servizio bar
     */
    private fun requestBarService() {
        val currentState = viewModel.timerState.value ?: return
        val serverUrl = currentState.serverUrl

        if (serverUrl.isEmpty() || !currentState.isConnectedToServer) {
            Toast.makeText(this, "Non connesso al server", Toast.LENGTH_SHORT).show()
            return
        }

        // Crea il dialog personalizzato
        val dialog = Dialog(this)
        dialog.requestWindowFeature(Window.FEATURE_NO_TITLE)
        dialog.setContentView(R.layout.dialog_bar_service)
        dialog.window?.setBackgroundDrawable(ColorDrawable(Color.TRANSPARENT))

        // Imposta le dimensioni del dialogo
        val layoutParams = WindowManager.LayoutParams()
        layoutParams.copyFrom(dialog.window?.attributes)
        layoutParams.width = WindowManager.LayoutParams.WRAP_CONTENT
        layoutParams.height = WindowManager.LayoutParams.WRAP_CONTENT
        dialog.window?.attributes = layoutParams

        // Aggiorna il messaggio con il numero del tavolo
        val messageText = dialog.findViewById<TextView>(R.id.bar_service_message)
        messageText.text = "Vuoi richiedere il servizio bar al tavolo ${currentState.tableNumber}?"

        // Configura i pulsanti
        val cancelButton = dialog.findViewById<Button>(R.id.bar_cancel_button)
        val requestButton = dialog.findViewById<Button>(R.id.bar_request_button)

        cancelButton.setOnClickListener {
            dialog.dismiss()
        }

        requestButton.setOnClickListener {
            dialog.dismiss()
            sendBarServiceRequest()
        }

        dialog.show()
    }

    /**
     * Invia la richiesta di servizio bar al server
     */
    private fun sendBarServiceRequest() {
        val currentState = viewModel.timerState.value ?: return
        val serverUrl = currentState.serverUrl

        // Mostra un dialogo di progresso
        val progressDialog = ProgressDialog(this).apply {
            setMessage("Invio richiesta in corso...")
            setCancelable(false)
            show()
        }

        CoroutineScope(Dispatchers.Main).launch {
            try {
                val success = withContext(Dispatchers.IO) {
                    try {
                        val url = URL("$serverUrl/api/bar_service_request")
                        val connection = url.openConnection() as HttpURLConnection
                        connection.requestMethod = "POST"
                        connection.doOutput = true
                        connection.setRequestProperty("Content-Type", "application/json; charset=UTF-8")
                        connection.connectTimeout = 5000
                        connection.readTimeout = 5000

                        // IMPORTANTE: Il server si aspetta timestamp come numero, non stringa
                        val jsonPayload = """
                        {
                            "table_number": ${currentState.tableNumber},
                            "timestamp": ${System.currentTimeMillis()}
                        }
                    """.trimIndent()

                        Log.d("MainActivity", "Invio richiesta bar service: $jsonPayload")

                        val outputStream = connection.outputStream
                        outputStream.write(jsonPayload.toByteArray())
                        outputStream.close()

                        val responseCode = connection.responseCode
                        Log.d("MainActivity", "Response code bar service: $responseCode")

                        // Leggi la risposta per debug
                        if (responseCode == HttpURLConnection.HTTP_OK) {
                            val inputStream = connection.inputStream
                            val response = inputStream.bufferedReader().use { it.readText() }
                            Log.d("MainActivity", "Response body bar service: $response")
                        }

                        connection.disconnect()

                        responseCode == HttpURLConnection.HTTP_OK
                    } catch (e: Exception) {
                        Log.e("MainActivity", "Errore richiesta servizio bar: ${e.message}", e)
                        false
                    }
                }

                progressDialog.dismiss()

                if (success) {
                    Toast.makeText(this@MainActivity, "Servizio bar richiesto con successo", Toast.LENGTH_SHORT).show()

                    // Effetto visivo sul bottone
                    animateButton(binding.btnBarService)

                    // Vibrazione di conferma
                    val vibrator = getSystemService(Context.VIBRATOR_SERVICE) as Vibrator
                    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                        vibrator.vibrate(VibrationEffect.createOneShot(200, VibrationEffect.DEFAULT_AMPLITUDE))
                    } else {
                        @Suppress("DEPRECATION")
                        vibrator.vibrate(200)
                    }
                } else {
                    Toast.makeText(this@MainActivity, "Errore nella richiesta servizio bar", Toast.LENGTH_SHORT).show()
                }
            } catch (e: Exception) {
                progressDialog.dismiss()
                Log.e("MainActivity", "Errore richiesta servizio bar: ${e.message}", e)
                Toast.makeText(this@MainActivity, "Errore: ${e.message}", Toast.LENGTH_SHORT).show()
            }
        }
    }

    /**
     * Anima un bottone con un effetto di conferma
     */
    private fun animateButton(button: ImageButton) {
        button.animate()
            .scaleX(1.2f)
            .scaleY(1.2f)
            .setDuration(200)
            .withEndAction {
                button.animate()
                    .scaleX(1f)
                    .scaleY(1f)
                    .setDuration(200)
                    .start()
            }
            .start()
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

        // Mostra il dialog di selezione invece di andare direttamente alle impostazioni
        showSettingsSelectionDialog()
    }

    /**
     * Mostra un popup di selezione con due bottoni: Settings e Cancel
     */
    private fun showSettingsSelectionDialog() {
        // Crea il dialog
        val dialog = Dialog(this)
        dialog.requestWindowFeature(Window.FEATURE_NO_TITLE)
        dialog.setContentView(R.layout.dialog_settings_selection)

        // Imposta uno sfondo trasparente per la finestra del dialog
        dialog.window?.setBackgroundDrawable(ColorDrawable(Color.TRANSPARENT))

        // Imposta le dimensioni del dialog
        val layoutParams = WindowManager.LayoutParams()
        layoutParams.copyFrom(dialog.window?.attributes)
        layoutParams.width = WindowManager.LayoutParams.WRAP_CONTENT
        layoutParams.height = WindowManager.LayoutParams.WRAP_CONTENT
        dialog.window?.attributes = layoutParams

        // Ottieni i riferimenti ai bottoni
        val settingsButton = dialog.findViewById<Button>(R.id.settings_button)
        val cancelButton = dialog.findViewById<Button>(R.id.cancel_button)

        // Configura il bottone Settings
        settingsButton.setOnClickListener {
            dialog.dismiss()
            showSettingsDialog()
        }

        // Configura il bottone Cancel
        cancelButton.setOnClickListener {
            dialog.dismiss()
        }

        // Mostra il dialog
        dialog.show()
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

/*
    private fun showPlayerSelectionDialog() {
        // Crea il dialogo
        val dialog = Dialog(this)
        dialog.setContentView(R.layout.dialog_player_selection)

        // Imposta la larghezza del dialogo
        val window = dialog.window
        window?.setLayout(WindowManager.LayoutParams.MATCH_PARENT, WindowManager.LayoutParams.WRAP_CONTENT)

        // CODICE CORRETTO: Ottieni la vista principale del dialogo e ruotala
        val mainContainer = dialog.findViewById<ConstraintLayout>(R.id.dialog_main_container)
        mainContainer.rotation = 180f

        // Ottieni il numero del tavolo corrente e il numero di giocatori
        val currentState = viewModel.timerState.value
        val tableNumber = currentState?.tableNumber ?: 1
        val playersCount = currentState?.playersCount ?: 10 // Usa il numero di giocatori configurato

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

        // Configura la visibilità dei bottoni in base al numero di giocatori
        playerButtons.forEachIndexed { index, button ->
            // Mostra solo i bottoni per il numero di giocatori configurato
            button.visibility = if (index < playersCount) View.VISIBLE else View.GONE
        }

        // Adatta il layout in base al numero di giocatori
        adjustLayoutForPlayerCount(dialog, playersCount)

        // Configura i listener per i bottoni dei giocatori e preseleziona posti esistenti
        playerButtons.forEachIndexed { index, button ->
            val playerNumber = index + 1

            // Preseleziona posti esistenti
            if (selectedPlayerSeats.contains(playerNumber)) {
                button.isSelected = true
            }

            // Aggiungi listener solo ai bottoni visibili
            if (index < playersCount) {
                button.setOnClickListener {
                    togglePlayerSelection(playerNumber, button)
                }
            }
        }

        // Configura i listener per i pulsanti di azione
        val sendButton = dialog.findViewById<Button>(R.id.sendButton)

        sendButton.setOnClickListener {
            // Verifica se ci sono posti selezionati
            if (selectedPlayerSeats.isEmpty()) {
                Toast.makeText(this, "Nessun posto selezionato", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }

            // Log per debug
            Log.d("MainActivity", "Invio posti selezionati: $selectedPlayerSeats")

            // Crea l'oggetto richiesta - fai una copia della lista per sicurezza
            val seatsList = ArrayList(selectedPlayerSeats) // crea una copia sicura
            val seatRequest = PlayerSeatRequest(tableNumber, seatsList)

            // Mostra un dialogo di caricamento
            val progressDialog = ProgressDialog(this).apply {
                setMessage("Invio richiesta posti in corso...")
                setCancelable(false)
                show()
            }

            // Utilizza una coroutine per la chiamata di rete
            CoroutineScope(Dispatchers.Main).launch {
                try {
                    val networkManager = NetworkManager(applicationContext)

                    // Invia la richiesta usando il NetworkManager
                    val success = networkManager.sendSeatRequest(currentState?.serverUrl ?: "", seatRequest)

                    // Nascondi il dialogo di caricamento
                    progressDialog.dismiss()

                    // Gestisci la risposta
                    if (success) {
                        // Solo ora svuota la lista e chiudi il dialogo
                        selectedPlayerSeats.clear()
                        viewModel.saveSelectedSeats(emptyList())
                        dialog.dismiss()

                        Toast.makeText(applicationContext, "Posti inviati con successo", Toast.LENGTH_SHORT).show()
                    } else {
                        Toast.makeText(applicationContext, "Errore nell'invio della richiesta", Toast.LENGTH_SHORT).show()
                    }
                } catch (e: Exception) {
                    // Nascondi il dialogo di caricamento in caso di errore
                    progressDialog.dismiss()

                    Log.e("MainActivity", "Errore nell'invio dei posti: ${e.message}", e)
                    Toast.makeText(applicationContext, "Errore: ${e.message}", Toast.LENGTH_SHORT).show()
                }
            }
        }

        val closeButton = dialog.findViewById<ImageButton>(R.id.closeButton)
        closeButton.setOnClickListener {
            // Ripristina la lista originale
            selectedPlayerSeats.clear()
            selectedPlayerSeats.addAll(existingSeats)

            // Chiudi il dialogo senza inviare nulla
            dialog.dismiss()
        }

        dialog.show()
    }

    */
private fun showPlayerSelectionDialog() {
    // Crea il dialogo
    val dialog = Dialog(this)
    dialog.setContentView(R.layout.dialog_player_selection)

    // Imposta la larghezza del dialogo
    val window = dialog.window
    window?.setLayout(WindowManager.LayoutParams.MATCH_PARENT, WindowManager.LayoutParams.WRAP_CONTENT)

    // CODICE CORRETTO: Ottieni la vista principale del dialogo e ruotala
    val mainContainer = dialog.findViewById<ConstraintLayout>(R.id.dialog_main_container)
    mainContainer.rotation = 180f

    // Ottieni il numero del tavolo corrente e il numero di giocatori
    val currentState = viewModel.timerState.value
    val tableNumber = currentState?.tableNumber ?: 1
    val playersCount = currentState?.playersCount ?: 10 // Usa il numero di giocatori configurato

    // Verifica se ci sono posti già selezionati
    val existingSeats = viewModel.getExistingSeats()

    // Resetta e carica le selezioni precedenti
    selectedPlayerSeats.clear()
    selectedPlayerSeats.addAll(existingSeats)

    // Lista dei bottoni dei giocatori
    val firstRowButtons = listOf(
        dialog.findViewById<Button>(R.id.playerButton1),
        dialog.findViewById<Button>(R.id.playerButton2),
        dialog.findViewById<Button>(R.id.playerButton3),
        dialog.findViewById<Button>(R.id.playerButton4),
        dialog.findViewById<Button>(R.id.playerButton5)
    )

    val secondRowButtons = listOf(
        dialog.findViewById<Button>(R.id.playerButton6),
        dialog.findViewById<Button>(R.id.playerButton7),
        dialog.findViewById<Button>(R.id.playerButton8),
        dialog.findViewById<Button>(R.id.playerButton9),
        dialog.findViewById<Button>(R.id.playerButton10)
    )

    val allButtons = firstRowButtons + secondRowButtons

    // Adatta il layout in base al numero di giocatori
    adjustLayoutForPlayerCount(dialog, playersCount)

    // Configura i listener per i bottoni dei giocatori visibili
    allButtons.forEach { button ->
        if (button.visibility == View.VISIBLE) {
            // Ottieni il numero del giocatore dal tag del bottone
            val playerNumber = button.tag as Int

            // Preseleziona posti esistenti
            if (selectedPlayerSeats.contains(playerNumber)) {
                button.isSelected = true
            }

            button.setOnClickListener {
                togglePlayerSelection(playerNumber, button)
            }
        }
    }

    // Configura i listener per i pulsanti di azione
    val sendButton = dialog.findViewById<Button>(R.id.sendButton)

    sendButton.setOnClickListener {
        // Verifica se ci sono posti selezionati
        if (selectedPlayerSeats.isEmpty()) {
            Toast.makeText(this, "Nessun posto selezionato", Toast.LENGTH_SHORT).show()
            return@setOnClickListener
        }

        // Log per debug
        Log.d("MainActivity", "Invio posti selezionati: $selectedPlayerSeats")

        // Crea l'oggetto richiesta - fai una copia della lista per sicurezza
        val seatsList = ArrayList(selectedPlayerSeats) // crea una copia sicura
        val seatRequest = PlayerSeatRequest(tableNumber, seatsList)

        // Mostra un dialogo di caricamento
        val progressDialog = ProgressDialog(this).apply {
            setMessage("Invio richiesta posti in corso...")
            setCancelable(false)
            show()
        }

        // Utilizza una coroutine per la chiamata di rete
        CoroutineScope(Dispatchers.Main).launch {
            try {
                val networkManager = NetworkManager(applicationContext)

                // Invia la richiesta usando il NetworkManager
                val success = networkManager.sendSeatRequest(currentState?.serverUrl ?: "", seatRequest)

                // Nascondi il dialogo di caricamento
                progressDialog.dismiss()

                // Gestisci la risposta
                if (success) {
                    // Solo ora svuota la lista e chiudi il dialogo
                    selectedPlayerSeats.clear()
                    viewModel.saveSelectedSeats(emptyList())
                    dialog.dismiss()

                    Toast.makeText(applicationContext, "Posti inviati con successo", Toast.LENGTH_SHORT).show()
                } else {
                    Toast.makeText(applicationContext, "Errore nell'invio della richiesta", Toast.LENGTH_SHORT).show()
                }
            } catch (e: Exception) {
                // Nascondi il dialogo di caricamento in caso di errore
                progressDialog.dismiss()

                Log.e("MainActivity", "Errore nell'invio dei posti: ${e.message}", e)
                Toast.makeText(applicationContext, "Errore: ${e.message}", Toast.LENGTH_SHORT).show()
            }
        }
    }

    val closeButton = dialog.findViewById<ImageButton>(R.id.closeButton)
    closeButton.setOnClickListener {
        // Ripristina la lista originale
        selectedPlayerSeats.clear()
        selectedPlayerSeats.addAll(existingSeats)

        // Chiudi il dialogo senza inviare nulla
        dialog.dismiss()
    }

    dialog.show()
}

    /**
     * Adatta il layout del dialogo in base al numero di giocatori
     */
    /*
    private fun adjustLayoutForPlayerCount(dialog: Dialog, playersCount: Int) {
        // Ottieni il container dei bottoni
        val buttonsContainer = dialog.findViewById<ConstraintLayout>(R.id.buttonsContainer)

        // Riferimenti ai bottoni nella prima e seconda fila
        val firstRowButtons = listOf(
            dialog.findViewById<Button>(R.id.playerButton1),
            dialog.findViewById<Button>(R.id.playerButton2),
            dialog.findViewById<Button>(R.id.playerButton3),
            dialog.findViewById<Button>(R.id.playerButton4),
            dialog.findViewById<Button>(R.id.playerButton5)
        )

        val secondRowButtons = listOf(
            dialog.findViewById<Button>(R.id.playerButton6),
            dialog.findViewById<Button>(R.id.playerButton7),
            dialog.findViewById<Button>(R.id.playerButton8),
            dialog.findViewById<Button>(R.id.playerButton9),
            dialog.findViewById<Button>(R.id.playerButton10)
        )

        // Calcola quanti bottoni visualizzare nella prima e seconda fila
        val firstRowCount = minOf(5, playersCount)
        val secondRowCount = maxOf(0, playersCount - 5)

        // Se c'è solo una fila, nascondi completamente la seconda
        if (secondRowCount == 0) {
            secondRowButtons.forEach { it.visibility = View.GONE }

            // Ridimensiona e posiziona i bottoni della prima fila in modo uniforme
            if (firstRowCount < 5) {
                // Calcola lo spazio tra i bottoni per distribuirli uniformemente
                val buttonWidth = 0.18f // width_percent di ogni bottone
                val totalWidth = buttonWidth * firstRowCount
                val spacing = (1f - totalWidth) / (firstRowCount + 1)

                // Aggiorna i vincoli dei bottoni
                for (i in 0 until firstRowCount) {
                    val button = firstRowButtons[i]
                    val params = button.layoutParams as ConstraintLayout.LayoutParams

                    // Imposta nuovi margini per distribuire uniformemente i bottoni
                    val startPercent = spacing + i * (buttonWidth + spacing)
                    val endPercent = 1f - startPercent - buttonWidth

                    // Utilizza i nuovi margini
                    params.leftMargin = (startPercent * buttonsContainer.width).toInt()
                    params.rightMargin = (endPercent * buttonsContainer.width).toInt()

                    button.layoutParams = params
                }
            }
        }
        // Se abbiamo una seconda fila incompleta
        else if (secondRowCount < 5) {
            // Nascondi i bottoni non necessari nella seconda fila
            for (i in secondRowCount until 5) {
                secondRowButtons[i].visibility = View.GONE
            }

            // Calcola lo spazio tra i bottoni per distribuirli uniformemente nella seconda fila
            val buttonWidth = 0.18f // width_percent di ogni bottone
            val totalWidth = buttonWidth * secondRowCount
            val spacing = (1f - totalWidth) / (secondRowCount + 1)

            // Aggiorna i vincoli dei bottoni della seconda fila
            for (i in 0 until secondRowCount) {
                val button = secondRowButtons[i]
                val params = button.layoutParams as ConstraintLayout.LayoutParams

                // Imposta nuovi margini per distribuire uniformemente i bottoni
                val startPercent = spacing + i * (buttonWidth + spacing)
                val endPercent = 1f - startPercent - buttonWidth

                // Utilizza i nuovi margini
                params.leftMargin = (startPercent * buttonsContainer.width).toInt()
                params.rightMargin = (endPercent * buttonsContainer.width).toInt()

                button.layoutParams = params
            }
        }
    }
*/
    /**
     * Adatta il layout del dialogo in base al numero di giocatori secondo la nuova distribuzione
     */
    /**
     * Adatta il layout del dialogo in base al numero di giocatori
     */
    private fun adjustLayoutForPlayerCount(dialog: Dialog, playersCount: Int) {
        // Ottieni il container dei bottoni
        val buttonsContainer = dialog.findViewById<ConstraintLayout>(R.id.buttonsContainer)

        // Riferimenti ai bottoni nella prima e seconda fila
        val firstRowButtons = listOf(
            dialog.findViewById<Button>(R.id.playerButton1),
            dialog.findViewById<Button>(R.id.playerButton2),
            dialog.findViewById<Button>(R.id.playerButton3),
            dialog.findViewById<Button>(R.id.playerButton4),
            dialog.findViewById<Button>(R.id.playerButton5)
        )

        val secondRowButtons = listOf(
            dialog.findViewById<Button>(R.id.playerButton6),
            dialog.findViewById<Button>(R.id.playerButton7),
            dialog.findViewById<Button>(R.id.playerButton8),
            dialog.findViewById<Button>(R.id.playerButton9),
            dialog.findViewById<Button>(R.id.playerButton10)
        )

        // Tutti i bottoni in un'unica lista
        val allButtons = firstRowButtons + secondRowButtons

        // Determina il numero di bottoni in ciascuna riga in base al conteggio totale
        val (firstRowCount, secondRowCount) = when (playersCount) {
            1 -> 1 to 0  // 1 giocatore: 1 nella prima riga
            2 -> 2 to 0  // 2 giocatori: 2 nella prima riga
            3 -> 3 to 0  // 3 giocatori: 3 nella prima riga
            4 -> 2 to 2  // 4 giocatori: 2 per riga
            5 -> 3 to 2  // 5 giocatori: 3 nella prima, 2 nella seconda
            6 -> 3 to 3  // 6 giocatori: 3 per riga
            7 -> 4 to 3  // 7 giocatori: 4 nella prima, 3 nella seconda
            8 -> 4 to 4  // 8 giocatori: 4 per riga
            9 -> 5 to 4  // 9 giocatori: 5 nella prima, 4 nella seconda
            else -> 5 to 5  // 10 giocatori: 5 per riga (layout originale)
        }

        // Nascondi tutti i bottoni inizialmente
        allButtons.forEach { it.visibility = View.GONE }

        // Contatore per i numeri dei bottoni
        var playerNumber = 1

        // Gestisci i bottoni della prima riga
        for (i in 0 until firstRowCount) {
            val button = firstRowButtons[i]
            button.visibility = View.VISIBLE

            // Imposta il numero corretto sul bottone
            button.text = playerNumber.toString()

            // Associa il player number corretto al bottone per l'utilizzo in togglePlayerSelection
            button.tag = playerNumber

            // Incrementa il contatore
            playerNumber++

            // Aggiorna i parametri del layout per distribuire uniformemente
            val layoutParams = button.layoutParams as ConstraintLayout.LayoutParams

            when (firstRowCount) {
                1 -> {
                    // Un solo bottone centrato
                    layoutParams.horizontalBias = 0.5f
                }
                2 -> {
                    // Due bottoni distribuiti (posizioni 1 e 5)
                    if (i == 0) {
                        layoutParams.horizontalBias = 0.25f
                    } else {
                        layoutParams.horizontalBias = 0.75f
                    }
                }
                3 -> {
                    // Tre bottoni distribuiti (posizioni 1, 3, 5)
                    layoutParams.horizontalBias = when (i) {
                        0 -> 0.17f
                        1 -> 0.5f
                        else -> 0.83f
                    }
                }
                4 -> {
                    // Quattro bottoni distribuiti (posizioni 1, 2, 4, 5)
                    layoutParams.horizontalBias = when (i) {
                        0 -> 0.125f
                        1 -> 0.375f
                        2 -> 0.625f
                        else -> 0.875f
                    }
                }
                5 -> {
                    // Cinque bottoni (layout originale - nessuna modifica necessaria)
                }
            }

            button.layoutParams = layoutParams
        }

        // Se ci sono bottoni nella seconda riga
        if (secondRowCount > 0) {
            // Mostra e posiziona i bottoni della seconda riga
            for (i in 0 until secondRowCount) {
                val button = secondRowButtons[i]
                button.visibility = View.VISIBLE

                // Imposta il numero corretto sul bottone
                button.text = playerNumber.toString()

                // Associa il player number corretto al bottone per l'utilizzo in togglePlayerSelection
                button.tag = playerNumber

                // Incrementa il contatore
                playerNumber++

                // Aggiorna i parametri del layout per distribuire uniformemente
                val layoutParams = button.layoutParams as ConstraintLayout.LayoutParams

                when (secondRowCount) {
                    2 -> {
                        // Due bottoni distribuiti (posizioni 1 e 5)
                        if (i == 0) {
                            layoutParams.horizontalBias = 0.25f
                        } else {
                            layoutParams.horizontalBias = 0.75f
                        }
                    }
                    3 -> {
                        // Tre bottoni distribuiti (posizioni 1, 3, 5)
                        layoutParams.horizontalBias = when (i) {
                            0 -> 0.17f
                            1 -> 0.5f
                            else -> 0.83f
                        }
                    }
                    4 -> {
                        // Quattro bottoni distribuiti (posizioni 1, 2, 4, 5)
                        layoutParams.horizontalBias = when (i) {
                            0 -> 0.125f
                            1 -> 0.375f
                            2 -> 0.625f
                            else -> 0.875f
                        }
                    }
                    5 -> {
                        // Cinque bottoni (layout originale - nessuna modifica necessaria)
                    }
                }

                button.layoutParams = layoutParams
            }
        }
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

        // Pulsanti personalizzati
        val saveButton = dialogView.findViewById<Button>(R.id.custom_save_button)
        val cancelButton = dialogView.findViewById<Button>(R.id.custom_cancel_button)

        // Valori T1 e T2
        var t1Value = currentState.timerT1
        var t2Value = currentState.timerT2
        timerT1Value.text = "${t1Value}s"
        timerT2Value.text = "${t2Value}s"

        // Stato buzzer
        buzzerSwitch.isChecked = currentState.buzzerEnabled

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

        // Listener per il pulsante Salva
        saveButton.setOnClickListener {
            // Salva le impostazioni mantenendo l'URL del server corrente
            viewModel.saveSettings(
                timerT1 = t1Value,
                timerT2 = t2Value,
                operationMode = 1, // Manteniamo solo la modalità 1
                buzzerEnabled = buzzerSwitch.isChecked,
                tableNumber = tableNumber,
                serverUrl = currentState.serverUrl, // Mantieni l'URL corrente
                playersCount = playersCount
            )
            dialog.dismiss()
        }

        // Listener per il pulsante Annulla
        cancelButton.setOnClickListener {
            dialog.dismiss()
        }

        // Mostra il dialogo
        dialog.show()
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


}