package com.example.pokertimer;

import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.text.TextUtils;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

public class ServerUrlActivity extends AppCompatActivity {

    private static final String PREFS_NAME = "server_url_prefs";
    private static final String KEY_SERVER_URL = "server_url";

    private EditText serverUrlInput;
    private Button connectButton;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_server_url);

        // Inizializza le viste
        serverUrlInput = findViewById(R.id.serverUrlInput);
        connectButton = findViewById(R.id.connectButton);
        ImageView backButton = findViewById(R.id.backButton);

        // Carica l'URL salvato
        loadSavedServerUrl();

        // Imposta il listener per il pulsante indietro
        backButton.setOnClickListener(v -> finish());

        // Imposta il listener per il pulsante di connessione
        connectButton.setOnClickListener(v -> connectToServer());
    }

    /**
     * Carica l'URL del server salvato nelle preferenze
     */
    private void loadSavedServerUrl() {
        SharedPreferences prefs = getSharedPreferences(PREFS_NAME, MODE_PRIVATE);
        String savedUrl = prefs.getString(KEY_SERVER_URL, "");
        
        if (!TextUtils.isEmpty(savedUrl)) {
            serverUrlInput.setText(savedUrl);
        }
    }

    /**
     * Salva l'URL del server nelle preferenze
     */
    private void saveServerUrl(String url) {
        SharedPreferences prefs = getSharedPreferences(PREFS_NAME, MODE_PRIVATE);
        prefs.edit().putString(KEY_SERVER_URL, url).apply();
    }

    /**
     * Connetti al server e avvia la DashboardActivity
     */
    private void connectToServer() {
        String serverUrl = serverUrlInput.getText().toString().trim();
        
        if (TextUtils.isEmpty(serverUrl)) {
            Toast.makeText(this, "Inserisci l'URL del server", Toast.LENGTH_SHORT).show();
            return;
        }

        // Validazione di base dell'URL
        if (!serverUrl.startsWith("http://") && !serverUrl.startsWith("https://")) {
            serverUrl = "http://" + serverUrl;
            serverUrlInput.setText(serverUrl);
        }

        // Salva l'URL
        saveServerUrl(serverUrl);

        // Avvia l'activity della dashboard
        Intent intent = new Intent(this, DashboardActivity.class);
        intent.putExtra("server_url", serverUrl);
        startActivity(intent);
    }
}