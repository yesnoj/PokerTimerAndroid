package com.example.pokertimer

import android.app.AlertDialog
import android.content.Context
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.view.GestureDetector
import android.view.LayoutInflater
import android.view.MotionEvent
import android.view.View
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.ViewModelProvider
import com.example.pokertimer.databinding.ActivityMainBinding
import com.example.pokertimer.databinding.DialogSettingsBinding
import android.widget.Toast

class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding
    private lateinit var viewModel: PokerTimerViewModel

    // Gestione dei tap e pressioni lunghe
    private val handler = Handler(Looper.getMainLooper())

    // Flag per la gestione multi-tocco
    private var isLongPressActive = false
    private val longPressDelay = 500L // ms
    private var doubleTapTimeWindow = 300L // ms
    private var lastTapTime = 0L

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        // Inizializza il ViewModel
        viewModel = ViewModelProvider(this)[PokerTimerViewModel::class.java]

        // Osserva i cambiamenti di stato del timer
        observeTimerState()

        // Configura i listener per i pulsanti
        setupButtonListeners()
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

        // Istruzioni per i pulsanti basate sulla modalità
        if (state.isAutoStartMode) {
            instructionLines.add(getString(R.string.start_pause_auto_instruction))
        } else {
            instructionLines.add(getString(R.string.start_pause_manual_instruction))
        }

        instructionLines.add(getString(R.string.stop_instruction))
        instructionLines.add(getString(R.string.reset_instruction))

        if (!state.isT1OnlyMode) {
            instructionLines.add(getString(R.string.switch_instruction))
        }

        // Aggiorna il testo delle istruzioni
        binding.tvModeIndicators.text = instructionLines.joinToString("\n")
    }

    private fun showSettingsDialog() {
        val dialogBinding = DialogSettingsBinding.inflate(LayoutInflater.from(this))
        val currentState = viewModel.timerState.value ?: return
        var tableNumber = currentState.tableNumber
        dialogBinding.tvTableNumber.text = tableNumber.toString()

        dialogBinding.btnDecreaseTable.setOnClickListener {
            if (tableNumber > 0) {
                tableNumber--
                dialogBinding.tvTableNumber.text = tableNumber.toString()
            }
        }

        dialogBinding.btnIncreaseTable.setOnClickListener {
            if (tableNumber < 99) {
                tableNumber++
                dialogBinding.tvTableNumber.text = tableNumber.toString()
            }
        }

        // Imposta lo stato attuale nel dialogo
        when (currentState.operationMode) {
            PokerTimerState.MODE_1 -> dialogBinding.radioMode1.isChecked = true
            PokerTimerState.MODE_2 -> dialogBinding.radioMode2.isChecked = true
            PokerTimerState.MODE_3 -> dialogBinding.radioMode3.isChecked = true
            PokerTimerState.MODE_4 -> dialogBinding.radioMode4.isChecked = true
        }

        // Valori T1 e T2
        dialogBinding.tvT1Value.text = "${currentState.timerT1}s"
        dialogBinding.tvT2Value.text = "${currentState.timerT2}s"

        // Stato buzzer
        dialogBinding.switchBuzzer.isChecked = currentState.buzzerEnabled

        // Imposta l'URL del server nel campo di testo
        dialogBinding.etServerUrl.setText(currentState.serverUrl)

        // Visibilità delle impostazioni T2
        updateT2Visibility(
            dialogBinding,
            dialogBinding.radioMode1.isChecked || dialogBinding.radioMode2.isChecked
        )

        // Listener per i radio button della modalità
        dialogBinding.radioGroupMode.setOnCheckedChangeListener { _, checkedId ->
            val isT1T2Mode = checkedId == R.id.radio_mode_1 || checkedId == R.id.radio_mode_2
            updateT2Visibility(dialogBinding, isT1T2Mode)
        }

        // Listener per i pulsanti di incremento/decremento di T1
        var t1Value = currentState.timerT1
        dialogBinding.btnDecreaseT1.setOnClickListener {
            if (t1Value > 5) {
                t1Value -= 5
                dialogBinding.tvT1Value.text = "${t1Value}s"
            }
        }

        dialogBinding.btnIncreaseT1.setOnClickListener {
            if (t1Value < 95) {
                t1Value += 5
                dialogBinding.tvT1Value.text = "${t1Value}s"
            }
        }

        // Listener per i pulsanti di incremento/decremento di T2
        var t2Value = currentState.timerT2
        dialogBinding.btnDecreaseT2.setOnClickListener {
            if (t2Value > 5) {
                t2Value -= 5
                dialogBinding.tvT2Value.text = "${t2Value}s"
            }
        }

        dialogBinding.btnIncreaseT2.setOnClickListener {
            if (t2Value < 95) {
                t2Value += 5
                dialogBinding.tvT2Value.text = "${t2Value}s"
            }
        }

        // Gestione del test di connessione al server
        dialogBinding.btnTestConnection.setOnClickListener {
            val serverUrl = dialogBinding.etServerUrl.text.toString()
            if (serverUrl.isNotEmpty()) {
                // Mostra un indicatore di caricamento
                dialogBinding.btnTestConnection.isEnabled = false
                dialogBinding.btnTestConnection.text = getString(R.string.testing)

                viewModel.testServerConnection(serverUrl) { success ->
                    // Torna al thread principale
                    runOnUiThread {
                        dialogBinding.btnTestConnection.isEnabled = true
                        dialogBinding.btnTestConnection.text = getString(R.string.test_connection)

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
            .setView(dialogBinding.root)
            .setPositiveButton(R.string.save) { _, _ ->
                // Determina la modalità selezionata
                val mode = when {
                    dialogBinding.radioMode1.isChecked -> PokerTimerState.MODE_1
                    dialogBinding.radioMode2.isChecked -> PokerTimerState.MODE_2
                    dialogBinding.radioMode3.isChecked -> PokerTimerState.MODE_3
                    dialogBinding.radioMode4.isChecked -> PokerTimerState.MODE_4
                    else -> PokerTimerState.MODE_1 // Default
                }

                // Salva le impostazioni
                viewModel.saveSettings(
                    timerT1 = t1Value,
                    timerT2 = t2Value,
                    operationMode = mode,
                    buzzerEnabled = dialogBinding.switchBuzzer.isChecked,
                    tableNumber = tableNumber,
                    serverUrl = dialogBinding.etServerUrl.text.toString()
                )
            }
            .setNegativeButton(R.string.cancel, null)
            .show()
    }
    private fun updateT2Visibility(dialogBinding: DialogSettingsBinding, isVisible: Boolean) {
        dialogBinding.tvTimerT2Label.visibility = if (isVisible) View.VISIBLE else View.GONE
        dialogBinding.layoutTimerT2.visibility = if (isVisible) View.VISIBLE else View.GONE
    }
}