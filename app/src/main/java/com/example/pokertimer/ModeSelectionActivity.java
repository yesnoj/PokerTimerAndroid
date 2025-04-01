package com.example.pokertimer;

import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.view.View;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;
import androidx.cardview.widget.CardView;

public class ModeSelectionActivity extends AppCompatActivity {

    private static final String PREFS_NAME = "mode_selection_prefs";
    private static final String KEY_LAST_MODE = "last_selected_mode";
    private static final String MODE_TIMER = "timer";
    private static final String MODE_DASHBOARD = "dashboard";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_mode_selection);

        // Ottieni riferimenti ai pulsanti CardView
        CardView timerModeCard = findViewById(R.id.timerModeCard);
        CardView dashboardModeCard = findViewById(R.id.dashboardModeCard);

        // Imposta listener per il pulsante Timer
        timerModeCard.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                // Salva la scelta
                saveLastMode(MODE_TIMER);

                // Avvia la MainActivity (Timer)
                Intent intent = new Intent(ModeSelectionActivity.this, MainActivity.class);
                startActivity(intent);
            }
        });

        // Imposta listener per il pulsante Dashboard
        dashboardModeCard.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                // Salva la scelta
                saveLastMode(MODE_DASHBOARD);

                // Avvia la DashboardActivity o la ServerUrlActivity
                launchDashboardMode();
            }
        });

        // Controlla se l'utente aveva selezionato una modalità in precedenza
        checkLastMode();
    }

    /**
     * Salva l'ultima modalità selezionata nelle preferenze
     */
    private void saveLastMode(String mode) {
        SharedPreferences prefs = getSharedPreferences(PREFS_NAME, MODE_PRIVATE);
        prefs.edit().putString(KEY_LAST_MODE, mode).apply();
    }

    /**
     * Controlla se c'è una modalità salvata e avvia direttamente quella schermata
     */
    private void checkLastMode() {
        SharedPreferences prefs = getSharedPreferences(PREFS_NAME, MODE_PRIVATE);
        String lastMode = prefs.getString(KEY_LAST_MODE, null);

        if (lastMode != null) {
            // Per ora, commentato per fare in modo che l'utente debba scegliere ogni volta
            // In futuro si può abilitare per saltare direttamente alla modalità scelta l'ultima volta

            /*
            if (MODE_TIMER.equals(lastMode)) {
                Intent intent = new Intent(this, MainActivity.class);
                startActivity(intent);
                finish();
            } else if (MODE_DASHBOARD.equals(lastMode)) {
                launchDashboardMode();
                finish();
            }
            */
        }
    }

    /**
     * Avvia la modalità dashboard
     */
    private void launchDashboardMode() {
        // Per ora, avviamo l'activity per inserire l'URL del server
        Intent intent = new Intent(this, ServerUrlActivity.class);
        startActivity(intent);

        // Nota: in futuro, se implementiamo l'autenticazione, potremmo avviare LoginActivity
    }
}