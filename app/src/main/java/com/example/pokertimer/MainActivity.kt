package com.example.pokertimer

import android.app.AlertDialog
import android.app.Dialog
import android.content.Intent
import android.content.res.Configuration
import android.graphics.Color
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.view.LayoutInflater
import android.view.View
import android.view.WindowManager
import android.widget.Button
import android.widget.ImageView
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

class MainActivity : AppCompatActivity() {

    private lateinit var binding: MainActivityBinding
    private lateinit var viewModel: PokerTimerViewModel
    private val selectedPlayerSeats = mutableListOf<Int>()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

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

        // Imposta listener per il pulsante Back
        val backButton = findViewById<ImageView>(R.id.backToModeSelectionButton)
        backButton?.setOnClickListener {
            // Torna alla schermata di selezione modalità
            val intent = Intent(this, ModeSelectionActivity::class.java)
            startActivity(intent)
            finish() // Opzionale, chiude l'activity corrente
        }
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
            updateModeIndicators(it)
        }
    }

    private fun observeTimerState() {
        viewModel.timerState.observe(this) { state ->
            updateTimerDisplay(state)
            updateButtonsState(state)
            updateModeIndicators(state)
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

        // Pulsante impostazioni
        binding.btnSettings.setOnClickListener {
            showSettingsDialog()
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


        dialog.show()
    }



    private fun updateTimerDisplay(state: PokerTimerState) {
        // Aggiorna il contatore del timer
        binding.tvTimer.text = state.currentTimer.toString()
        binding.tvTableNumber.text = getString(R.string.table_format, state.tableNumber)
        binding.tvServerStatus.text = getString(
            if (state.isConnectedToServer) R.string.server_connected else R.string.server_disconnected
        )
        binding.tvServerStatus.setTextColor(
            getColor(if (state.isConnectedToServer) R.color.status_color else R.color.error_color)
        )
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

        // Aggiorna info modalità e buzzer
        binding.tvModeInfo.text = getString(R.string.mode_format, state.operationMode)
        binding.tvBuzzerInfo.text = getString(
            if (state.buzzerEnabled) R.string.buzzer_on else R.string.buzzer_off
        )

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

    private fun updateModeIndicators(state: PokerTimerState) {
        val instructionLines = mutableListOf<String>()

        // Istruzioni per i pulsanti Start/Pause
        if (state.isRunning && !state.isPaused) {
            // Timer in esecuzione
            instructionLines.add(getString(R.string.pause_instruction))
        } else if (state.isPaused) {
            // Timer in pausa
            instructionLines.add(getString(R.string.resume_instruction))
        } else {
            // Timer fermo
            instructionLines.add(getString(R.string.start_instruction))
        }

        // Istruzioni per il pulsante Stop
        instructionLines.add(getString(R.string.stop_instruction))

        // Istruzioni specifiche per il pulsante Reset in base alla modalità
        if (state.isAutoStartMode) {
            // Modalità 1 o 3
            instructionLines.add(getString(R.string.reset_auto_instruction))
        } else {
            // Modalità 2 o 4
            instructionLines.add(getString(R.string.reset_manual_instruction))
        }

        // Istruzioni per il pulsante Switch se disponibile
        if (!state.isT1OnlyMode) {
            instructionLines.add(getString(R.string.switch_instruction))
        }

        // Aggiorna il testo delle istruzioni
        binding.tvModeIndicators.text = instructionLines.joinToString("\n")
    }

    private fun showSettingsDialog() {
        val dialogView = layoutInflater.inflate(R.layout.dialog_settings, null)
        val currentState = viewModel.timerState.value ?: return
        var tableNumber = currentState.tableNumber
        dialogView.findViewById<TextView>(R.id.tv_table_number).text = tableNumber.toString()

        dialogView.findViewById<Button>(R.id.btn_decrease_table).setOnClickListener {
            if (tableNumber > 0) {
                tableNumber--
                dialogView.findViewById<TextView>(R.id.tv_table_number).text = tableNumber.toString()
            }
        }

        dialogView.findViewById<Button>(R.id.btn_increase_table).setOnClickListener {
            if (tableNumber < 99) {
                tableNumber++
                dialogView.findViewById<TextView>(R.id.tv_table_number).text = tableNumber.toString()
            }
        }

        // Imposta lo stato attuale nel dialogo
        when (currentState.operationMode) {
            PokerTimerState.MODE_1 -> dialogView.findViewById<RadioButton>(R.id.radio_mode_1).isChecked = true
            PokerTimerState.MODE_2 -> dialogView.findViewById<RadioButton>(R.id.radio_mode_2).isChecked = true
            PokerTimerState.MODE_3 -> dialogView.findViewById<RadioButton>(R.id.radio_mode_3).isChecked = true
            PokerTimerState.MODE_4 -> dialogView.findViewById<RadioButton>(R.id.radio_mode_4).isChecked = true
        }

        // Valori T1 e T2
        dialogView.findViewById<TextView>(R.id.tv_t1_value).text = "${currentState.timerT1}s"
        dialogView.findViewById<TextView>(R.id.tv_t2_value).text = "${currentState.timerT2}s"

        // Stato buzzer
        dialogView.findViewById<Switch>(R.id.switch_buzzer).isChecked = currentState.buzzerEnabled

        // Imposta l'URL del server nel campo di testo
        dialogView.findViewById<android.widget.EditText>(R.id.et_server_url).setText(currentState.serverUrl)

        // Visibilità delle impostazioni T2
        updateT2Visibility(
            dialogView,
            dialogView.findViewById<RadioButton>(R.id.radio_mode_1).isChecked || dialogView.findViewById<RadioButton>(R.id.radio_mode_2).isChecked
        )

        // Listener per i radio button della modalità
        dialogView.findViewById<RadioGroup>(R.id.radio_group_mode).setOnCheckedChangeListener { _, checkedId ->
            val isT1T2Mode = checkedId == R.id.radio_mode_1 || checkedId == R.id.radio_mode_2
            updateT2Visibility(dialogView, isT1T2Mode)
        }

        // Listener per i pulsanti di incremento/decremento di T1
        var t1Value = currentState.timerT1
        dialogView.findViewById<Button>(R.id.btn_decrease_t1).setOnClickListener {
            if (t1Value > 5) {
                t1Value -= 5
                dialogView.findViewById<TextView>(R.id.tv_t1_value).text = "${t1Value}s"
            }
        }

        dialogView.findViewById<Button>(R.id.btn_increase_t1).setOnClickListener {
            if (t1Value < 95) {
                t1Value += 5
                dialogView.findViewById<TextView>(R.id.tv_t1_value).text = "${t1Value}s"
            }
        }

        // Listener per i pulsanti di incremento/decremento di T2
        var t2Value = currentState.timerT2
        dialogView.findViewById<Button>(R.id.btn_decrease_t2).setOnClickListener {
            if (t2Value > 5) {
                t2Value -= 5
                dialogView.findViewById<TextView>(R.id.tv_t2_value).text = "${t2Value}s"
            }
        }

        dialogView.findViewById<Button>(R.id.btn_increase_t2).setOnClickListener {
            if (t2Value < 95) {
                t2Value += 5
                dialogView.findViewById<TextView>(R.id.tv_t2_value).text = "${t2Value}s"
            }
        }

        // Gestione del test di connessione al server
        dialogView.findViewById<Button>(R.id.btn_test_connection).setOnClickListener {
            val serverUrl = dialogView.findViewById<android.widget.EditText>(R.id.et_server_url).text.toString()
            if (serverUrl.isNotEmpty()) {
                // Mostra un indicatore di caricamento
                dialogView.findViewById<Button>(R.id.btn_test_connection).isEnabled = false
                dialogView.findViewById<Button>(R.id.btn_test_connection).text = getString(R.string.testing)

                viewModel.testServerConnection(serverUrl) { success ->
                    // Torna al thread principale
                    runOnUiThread {
                        dialogView.findViewById<Button>(R.id.btn_test_connection).isEnabled = true
                        dialogView.findViewById<Button>(R.id.btn_test_connection).text = getString(R.string.test_connection)

                        // Mostra il risultato del test
                        val message = if (success) R.string.connection_success else R.string.connection_failed
                        Toast.makeText(this, message, Toast.LENGTH_SHORT).show()
                    }
                }
            } else {
                Toast.makeText(this, R.string.enter_server_url, Toast.LENGTH_SHORT).show()
            }
        }

        // Costruzione del dialog
        AlertDialog.Builder(this)
            .setView(dialogView)
            .setPositiveButton(R.string.save) { _, _ ->
                // Determina la modalità selezionata
                val mode = when {
                    dialogView.findViewById<RadioButton>(R.id.radio_mode_1).isChecked -> PokerTimerState.MODE_1
                    dialogView.findViewById<RadioButton>(R.id.radio_mode_2).isChecked -> PokerTimerState.MODE_2
                    dialogView.findViewById<RadioButton>(R.id.radio_mode_3).isChecked -> PokerTimerState.MODE_3
                    dialogView.findViewById<RadioButton>(R.id.radio_mode_4).isChecked -> PokerTimerState.MODE_4
                    else -> PokerTimerState.MODE_1 // Default
                }

                // Salva le impostazioni
                viewModel.saveSettings(
                    timerT1 = t1Value,
                    timerT2 = t2Value,
                    operationMode = mode,
                    buzzerEnabled = dialogView.findViewById<Switch>(R.id.switch_buzzer).isChecked,
                    tableNumber = tableNumber,
                    serverUrl = dialogView.findViewById<android.widget.EditText>(R.id.et_server_url).text.toString()
                )
            }
            .setNegativeButton(R.string.cancel, null)
            .show()
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

    private fun updateT2Visibility(dialogView: View, isVisible: Boolean) {
        dialogView.findViewById<View>(R.id.tv_timer_t2_label).visibility = if (isVisible) View.VISIBLE else View.GONE
        dialogView.findViewById<View>(R.id.layout_timer_t2).visibility = if (isVisible) View.VISIBLE else View.GONE
    }
}