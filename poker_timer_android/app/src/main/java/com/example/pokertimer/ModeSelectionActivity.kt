package com.example.pokertimer

import android.content.Intent
import android.content.SharedPreferences
import android.os.Bundle
import android.widget.Button
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.cardview.widget.CardView
import android.view.WindowManager
import android.graphics.Color



class ModeSelectionActivity : AppCompatActivity() {

    companion object {
        private const val PREFS_NAME = "mode_selection_prefs"
        private const val KEY_LAST_MODE = "last_selected_mode"
        private const val MODE_TIMER = "timer"
        private const val MODE_DASHBOARD = "dashboard"
        private const val MODE_BAR = "bar"
    }

    // Nel metodo onCreate di ModeSelectionActivity
    override fun onCreate(savedInstanceState: Bundle?) {
        // Nascondi la barra di stato (notifiche)
        window.setFlags(
            WindowManager.LayoutParams.FLAG_FULLSCREEN,
            WindowManager.LayoutParams.FLAG_FULLSCREEN
        )

        // Nascondi l'action bar
        supportActionBar?.hide()

        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_mode_selection)

        // Ottieni riferimenti ai pulsanti CardView
        val timerModeCard = findViewById<CardView>(R.id.timerModeCard)
        val dashboardModeCard = findViewById<CardView>(R.id.dashboardModeCard)
        val barModeCard = findViewById<CardView>(R.id.barModeCard)

        // Aggiungi il riferimento al pulsante Help
        val helpButton = findViewById<Button>(R.id.helpButton)

        // Imposta listener per il pulsante Help
        helpButton.setOnClickListener {
            // Mostra il dialog di aiuto
            showHelpDialog()
        }

        // Imposta listener per il pulsante Timer
        timerModeCard.setOnClickListener {
            // Salva la scelta
            saveLastMode(MODE_TIMER)

            // Avvia la MainActivity (Timer)
            val intent = Intent(this, MainActivity::class.java)
            startActivity(intent)
        }

        // Imposta listener per il pulsante Dashboard
        dashboardModeCard.setOnClickListener {
            // Salva la scelta
            saveLastMode(MODE_DASHBOARD)

            // Avvia la ServerUrlActivity
            launchDashboardMode()
        }

        // Imposta listener per il pulsante Bar
        barModeCard.setOnClickListener {
            android.util.Log.d("ModeSelectionActivity", "Bar card clicked")

            // Salva la scelta
            saveLastMode(MODE_BAR)

            // Avvia la modalità Bar
            launchBarMode()
        }

        // Controlla se l'utente aveva selezionato una modalità in precedenza
        checkLastMode()
    }

    private fun showHelpDialog() {
        val dialogView = layoutInflater.inflate(R.layout.dialog_help, null)
        val dialog = AlertDialog.Builder(this)
            .setView(dialogView)
            .setTitle("Aiuto Timer")
            .setPositiveButton("Chiudi", null)
            .show()

        // Imposta il colore del testo del pulsante "Chiudi" a bianco
        dialog.getButton(AlertDialog.BUTTON_POSITIVE).setTextColor(Color.WHITE)
    }

    /**
     * Salva l'ultima modalità selezionata nelle preferenze
     */
    private fun saveLastMode(mode: String) {
        val prefs = getSharedPreferences(PREFS_NAME, MODE_PRIVATE)
        prefs.edit().putString(KEY_LAST_MODE, mode).apply()
    }

    /**
     * Controlla se c'è una modalità salvata e avvia direttamente quella schermata
     */
    private fun checkLastMode() {
        val prefs = getSharedPreferences(PREFS_NAME, MODE_PRIVATE)
        val lastMode = prefs.getString(KEY_LAST_MODE, null)

        // Commentato per fare in modo che l'utente debba scegliere ogni volta
        // In futuro si può abilitare per saltare direttamente alla modalità scelta l'ultima volta

        /*
        if (lastMode == MODE_TIMER) {
            val intent = Intent(this, MainActivity::class.java)
            startActivity(intent)
            finish()
        } else if (lastMode == MODE_DASHBOARD) {
            launchDashboardMode()
            finish()
        } else if (lastMode == MODE_BAR) {
            launchBarMode()
            finish()
        }
        */
    }

    /**
     * Avvia la modalità dashboard
     */
    private fun launchDashboardMode() {
        // Avvia l'activity per inserire l'URL del server
        val intent = Intent(this, ServerUrlActivity::class.java)
        startActivity(intent)

        // Nota: in futuro, se implementiamo l'autenticazione, potremmo avviare LoginActivity
    }

    /**
     * Avvia la modalità bar
     */
    private fun launchBarMode() {
        android.util.Log.d("ModeSelectionActivity", "launchBarMode() called")

        // Avvia l'activity per inserire l'URL del server, ma con modalità bar
        val intent = Intent(this, ServerUrlActivity::class.java)
        intent.putExtra("mode", "bar")

        android.util.Log.d("ModeSelectionActivity", "Starting ServerUrlActivity with mode: bar")
        startActivity(intent)
    }
}