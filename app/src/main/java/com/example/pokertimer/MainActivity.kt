package com.example.pokertimer

import android.app.AlertDialog
import android.app.Dialog
import android.app.ProgressDialog
import android.content.Intent
import android.content.res.Configuration
import android.graphics.Color
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.view.LayoutInflater
import android.view.WindowManager
import android.widget.Button
import android.widget.EditText
import android.widget.ImageView
import android.widget.LinearLayout
import android.widget.RadioButton
import android.widget.RadioGroup
import android.widget.Switch
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import androidx.lifecycle.ViewModelProvider
import android.util.Log
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.delay
import java.net.DatagramPacket
import java.net.DatagramSocket
import java.net.InetAddress
import java.net.SocketTimeoutException
import android.view.Menu
import android.view.MenuItem
import androidx.lifecycle.Observer
import android.os.Build
import android.view.View
import android.view.WindowInsets
import android.view.GestureDetector
import android.view.MotionEvent
import kotlin.math.abs


class MainActivity : AppCompatActivity() {

    private lateinit var binding: MainActivityBinding
    private lateinit var viewModel: PokerTimerViewModel
    private val selectedPlayerSeats = mutableListOf<Int>()
    private var isActionBarVisible = true
    private lateinit var gestureDetector: GestureDetector


    // Costanti per la discovery del server
    companion object {
        private const val DISCOVERY_PORT = 8888
        private const val DISCOVERY_TIMEOUT_MS = 3000
        private const val TAG = "MainActivity"
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Nascondi la barra delle notifiche (status bar)
        window.setFlags(
            WindowManager.LayoutParams.FLAG_FULLSCREEN,
            WindowManager.LayoutParams.FLAG_FULLSCREEN
        )

        // Rimuovi l'action bar
        supportActionBar?.hide()

        // Determina l'orientamento attuale e carica il layout appropriato
        val orientation = resources.configuration.orientation
        if (orientation == Configuration.ORIENTATION_LANDSCAPE) {
            setContentView(R.layout.activity_main_landscape)
        } else {
            setContentView(R.layout.activity_main_portrait)
        }

        // Inizializza il binding personalizzato
        binding = MainActivityBinding.bind(this)

        // Inizializza il ViewModel
        viewModel = ViewModelProvider(this)[PokerTimerViewModel::class.java]

        // Osserva i cambiamenti di stato del timer
        observeTimerState()

        // Configura i listener per i pulsanti
        setupButtonListeners()

        // Imposta il long press per accedere alle impostazioni
        setupLongPressForSettings()

        // Imposta lo swipe verso destra per tornare indietro
        setupSwipeGesture()
    }

    override fun onConfigurationChanged(newConfig: Configuration) {
        super.onConfigurationChanged(newConfig)

        // Cambia il layout in base al nuovo orientamento
        if (newConfig.orientation == Configuration.ORIENTATION_LANDSCAPE) {
            Log.d("MainActivity", "Switching to landscape layout")
            setContentView(R.layout.activity_main_landscape)
        } else {
            Log.d("MainActivity", "Switching to portrait layout")
            setContentView(R.layout.activity_main_portrait)
        }

        // Re-inizializza il binding
        binding = MainActivityBinding.bind(this)

        // Ricollega i listener e aggiorna lo stato
        setupButtonListeners()

        // Se il viewModel e lo stato sono già inizializzati, aggiorna la UI
        viewModel.timerState.value?.let {
            updateTimerDisplay(it)
            updateButtonsState(it)
        }
    }

    // Override di onTouchEvent per gestire il gesto
    override fun onTouchEvent(event: MotionEvent): Boolean {
        return gestureDetector.onTouchEvent(event) || super.onTouchEvent(event)
    }

    private fun setupLongPressForSettings() {
        val contentView = findViewById<View>(android.R.id.content)

        contentView.setOnLongClickListener {
            // Mostra il dialog delle impostazioni
            showSettingsDialog()
            true
        }
    }

    private fun setupSwipeGesture() {
        gestureDetector = GestureDetector(this, object : GestureDetector.SimpleOnGestureListener() {
            private val SWIPE_THRESHOLD = 100
            private val SWIPE_VELOCITY_THRESHOLD = 100

            override fun onFling(e1: MotionEvent?, e2: MotionEvent, velocityX: Float, velocityY: Float): Boolean {
                val diffX = e2.x - (e1?.x ?: 0f)

                if (diffX > SWIPE_THRESHOLD && abs(velocityX) > SWIPE_VELOCITY_THRESHOLD) {
                    // Swipe verso destra
                    finish()
                    return true
                }
                return false
            }
        })
    }



    private fun observeTimerState() {
        viewModel.timerState.observe(this) { state ->
            updateTimerDisplay(state)
            updateButtonsState(state)
        }
    }

    private fun toggleActionBar() {
        isActionBarVisible = !isActionBarVisible

        if (isActionBarVisible) {
            supportActionBar?.show()
        } else {
            supportActionBar?.hide()
        }

        // Opzionale: impostare in full screen quando la barra è nascosta
        if (!isActionBarVisible) {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
                window.setDecorFitsSystemWindows(false)
                window.insetsController?.hide(WindowInsets.Type.statusBars())
            } else {
                @Suppress("DEPRECATION")
                window.decorView.systemUiVisibility = View.SYSTEM_UI_FLAG_FULLSCREEN
            }
        } else {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
                window.setDecorFitsSystemWindows(true)
                window.insetsController?.show(WindowInsets.Type.statusBars())
            } else {
                @Suppress("DEPRECATION")
                window.decorView.systemUiVisibility = View.SYSTEM_UI_FLAG_VISIBLE
            }
        }
    }

    private fun setupButtonListeners() {
        // Pulsante Start/Pause
        binding.btnStartPause.setOnClickListener {
            viewModel.onStartPausePressed()
        }

        // Pulsante Reset
        binding.btnReset.setOnClickListener {
            viewModel.onResetPressed()
        }

        // Pulsante Switch
        binding.btnSwitch.setOnClickListener {
            viewModel.onSwitchPressed()
        }

        // Pulsante Stop
        binding.btnStop.setOnClickListener {
            viewModel.onStopPressed()
        }

        // Pulsante selezione giocatori
        binding.btnPlayersSelection.setOnClickListener {
            showPlayerSelectionDialog()
        }
    }

    private fun showPlayerSelectionDialog() {
        // Resetta le selezioni precedenti
        selectedPlayerSeats.clear()

        // Crea il dialogo
        val dialog = Dialog(this)
        dialog.setContentView(R.layout.dialog_player_selection)

        // Imposta la larghezza del dialogo
        val window = dialog.window
        window?.setLayout(WindowManager.LayoutParams.MATCH_PARENT, WindowManager.LayoutParams.WRAP_CONTENT)

        // Ottieni il numero del tavolo corrente
        val currentState = viewModel.timerState.value
        val tableNumber = currentState?.tableNumber ?: 1

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

        // Configura i listener per i bottoni dei giocatori
        playerButtons.forEachIndexed { index, button ->
            val playerNumber = index + 1
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

            // Chiudi il dialogo
            dialog.dismiss()
        }

        cancelButton.setOnClickListener {
            // Chiudi il dialogo senza inviare nulla
            dialog.dismiss()
        }

        dialog.show()
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

        // Nascondi il pulsante switch se siamo in modalità solo T1
        binding.btnSwitch.visibility = if (state.isT1OnlyMode) View.GONE else View.VISIBLE
    }

    private fun updateButtonsState(state: PokerTimerState) {
        // Testo del pulsante Start/Pause
        val startPauseText = when {
            state.isPaused -> getString(R.string.resume)
            state.isRunning && !state.isPaused -> getString(R.string.pause)
            else -> getString(R.string.start)
        }
        binding.btnStartPause.text = startPauseText

        // Colore del pulsante Start/Pause
        val startPauseColor = when {
            state.isPaused -> getColor(R.color.secondary_color)
            state.isRunning && !state.isPaused -> getColor(R.color.primary_color)
            else -> getColor(R.color.primary_color)
        }
        binding.btnStartPause.setBackgroundColor(startPauseColor)

        // Nascondi il pulsante switch se siamo in modalità solo T1
        binding.btnSwitch.visibility = if (state.isT1OnlyMode) View.GONE else View.VISIBLE
    }


    private fun showSettingsDialog() {
        val dialogView = layoutInflater.inflate(R.layout.dialog_settings, null)
        val currentState = viewModel.timerState.value ?: return

        // Inizializza le viste del dialogo
        val radioGroupMode = dialogView.findViewById<RadioGroup>(R.id.radio_group_mode)
        val radioMode1 = dialogView.findViewById<RadioButton>(R.id.radio_mode_1)
        val radioMode2 = dialogView.findViewById<RadioButton>(R.id.radio_mode_2)
        val radioMode3 = dialogView.findViewById<RadioButton>(R.id.radio_mode_3)
        val radioMode4 = dialogView.findViewById<RadioButton>(R.id.radio_mode_4)

        val timerT1Value = dialogView.findViewById<TextView>(R.id.tv_t1_value)
        val timerT2Value = dialogView.findViewById<TextView>(R.id.tv_t2_value)
        val timerT2Layout = dialogView.findViewById<LinearLayout>(R.id.layout_timer_t2)
        val timerT2Label = dialogView.findViewById<TextView>(R.id.tv_timer_t2_label)

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

        // Server URL e pulsanti di connessione
        val serverUrlInput = dialogView.findViewById<EditText>(R.id.et_server_url)
        val connectButton = dialogView.findViewById<Button>(R.id.btn_connect)
        val disconnectButton = dialogView.findViewById<Button>(R.id.btn_disconnect)

        // Header dello stato del server
        val serverStatusHeader = dialogView.findViewById<TextView>(R.id.server_status_header)
        updateServerStatusHeader(serverStatusHeader, currentState.isConnectedToServer)

        // Riferimento al pulsante di discovery
        val discoverButton = dialogView.findViewById<Button>(R.id.btn_discover_server)

        // Imposta i valori attuali nel dialogo
        when (currentState.operationMode) {
            PokerTimerState.MODE_1 -> radioMode1.isChecked = true
            PokerTimerState.MODE_2 -> radioMode2.isChecked = true
            PokerTimerState.MODE_3 -> radioMode3.isChecked = true
            PokerTimerState.MODE_4 -> radioMode4.isChecked = true
        }

        // Valori T1 e T2
        var t1Value = currentState.timerT1
        var t2Value = currentState.timerT2
        timerT1Value.text = "${t1Value}s"
        timerT2Value.text = "${t2Value}s"

        // Stato buzzer
        buzzerSwitch.isChecked = currentState.buzzerEnabled

        // Imposta l'URL del server nel campo di testo
        serverUrlInput.setText(currentState.serverUrl)

        // Visibilità delle impostazioni T2
        updateT2Visibility(
            dialogView,
            radioMode1.isChecked || radioMode2.isChecked
        )

        // Aggiorna lo stato dei pulsanti di connessione
        updateConnectionButtonsState(disconnectButton, connectButton, currentState.isConnectedToServer)

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

        // Listener per i radio button della modalità
        radioGroupMode.setOnCheckedChangeListener { _, checkedId ->
            val isT1T2Mode = checkedId == R.id.radio_mode_1 || checkedId == R.id.radio_mode_2
            updateT2Visibility(dialogView, isT1T2Mode)
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

        // Crea il dialogo
        val dialog = AlertDialog.Builder(this)
            .setView(dialogView)
            .setPositiveButton(R.string.save) { _, _ ->
                // Determina la modalità selezionata
                val mode = when {
                    radioMode1.isChecked -> PokerTimerState.MODE_1
                    radioMode2.isChecked -> PokerTimerState.MODE_2
                    radioMode3.isChecked -> PokerTimerState.MODE_3
                    radioMode4.isChecked -> PokerTimerState.MODE_4
                    else -> PokerTimerState.MODE_1 // Default
                }

                // Salva le impostazioni
                viewModel.saveSettings(
                    timerT1 = t1Value,
                    timerT2 = t2Value,
                    operationMode = mode,
                    buzzerEnabled = buzzerSwitch.isChecked,
                    tableNumber = tableNumber,
                    serverUrl = serverUrlInput.text.toString()
                )
            }
            .setNegativeButton(R.string.cancel, null)
            .create()

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
        } else {
            // Seleziona
            selectedPlayerSeats.add(playerNumber)
            button.isSelected = true
        }
    }

    /**
     * Aggiorna lo stato dei pulsanti di connessione in base allo stato attuale
     */
    private fun updateConnectionButtonsState(disconnectButton: Button, connectButton: Button, isConnected: Boolean) {
        if (isConnected) {
            // Se connesso, abilita Disconnetti e disabilita Connetti
            disconnectButton.isEnabled = true
            connectButton.isEnabled = false
            connectButton.text = "Connesso"
        } else {
            // Se disconnesso, abilita Connetti e disabilita Disconnetti
            disconnectButton.isEnabled = false
            connectButton.isEnabled = true
            connectButton.text = "Connetti"
        }
    }

    private fun updateT2Visibility(dialogView: View, isVisible: Boolean) {
        dialogView.findViewById<View>(R.id.tv_timer_t2_label).visibility = if (isVisible) View.VISIBLE else View.GONE
        dialogView.findViewById<View>(R.id.layout_timer_t2).visibility = if (isVisible) View.VISIBLE else View.GONE
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

                    // Aggiorna le informazioni localmente
                    // Nota: questo è solo temporaneo, idealmente il dato verrebbe aggiornato
                    // quando si ricarica la dashboard dal server
                    if (currentState != null) {
                        val newState = currentState.copy(
                            // Qui potresti aggiungere altre proprietà se necessario
                        )
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

    override fun onCreateOptionsMenu(menu: Menu): Boolean {
        menuInflater.inflate(R.menu.main_menu, menu)
        return true
    }

    override fun onOptionsItemSelected(item: MenuItem): Boolean {
        return when (item.itemId) {
            android.R.id.home -> {
                // Torna alla schermata di selezione modalità
                val intent = Intent(this, ModeSelectionActivity::class.java)
                startActivity(intent)
                finish() // Chiude l'activity corrente
                true
            }
            R.id.action_settings -> {
                showSettingsDialog()
                true
            }
            R.id.action_help -> {
                showHelpDialog()
                true
            }
            else -> super.onOptionsItemSelected(item)
        }
    }

    private fun showHelpDialog() {
        val dialogView = layoutInflater.inflate(R.layout.dialog_help, null)

        AlertDialog.Builder(this)
            .setView(dialogView)
            .setTitle("Aiuto Timer")
            .setPositiveButton("Chiudi", null)
            .show()
    }

}