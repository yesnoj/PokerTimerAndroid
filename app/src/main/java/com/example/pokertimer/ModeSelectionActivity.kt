package com.example.pokertimer

import android.content.Intent
import android.content.SharedPreferences
import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import androidx.cardview.widget.CardView

class ModeSelectionActivity : AppCompatActivity() {

    companion object {
        private const val PREFS_NAME = "mode_selection_prefs"
        private const val KEY_LAST_MODE = "last_selected_mode"
        private const val MODE_TIMER = "timer"
        private const val MODE_DASHBOARD = "dashboard"
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_mode_selection)

        // Ottieni riferimenti ai pulsanti CardView
        val timerModeCard = findViewById<CardView>(R.id.timerModeCard)
        val dashboardModeCard = findViewById<CardView>(R.id.dashboardModeCard)

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

        // Controlla se l'utente aveva selezionato una modalità in precedenza
        checkLastMode()
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
}