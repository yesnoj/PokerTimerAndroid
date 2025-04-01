package com.example.pokertimer

import android.content.Intent
import android.content.SharedPreferences
import android.os.Bundle
import android.text.TextUtils
import android.widget.Button
import android.widget.EditText
import android.widget.ImageView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity

class ServerUrlActivity : AppCompatActivity() {

    companion object {
        private const val PREFS_NAME = "server_url_prefs"
        private const val KEY_SERVER_URL = "server_url"
    }

    private lateinit var serverUrlInput: EditText
    private lateinit var connectButton: Button

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_server_url)

        // Inizializza le viste
        serverUrlInput = findViewById(R.id.serverUrlInput)
        connectButton = findViewById(R.id.connectButton)
        val backButton = findViewById<ImageView>(R.id.backButton)

        // Carica l'URL salvato
        loadSavedServerUrl()

        // Imposta il listener per il pulsante indietro
        backButton.setOnClickListener { finish() }

        // Imposta il listener per il pulsante di connessione
        connectButton.setOnClickListener { connectToServer() }
    }

    /**
     * Carica l'URL del server salvato nelle preferenze
     */
    private fun loadSavedServerUrl() {
        val prefs = getSharedPreferences(PREFS_NAME, MODE_PRIVATE)
        val savedUrl = prefs.getString(KEY_SERVER_URL, "")

        if (!savedUrl.isNullOrEmpty()) {
            serverUrlInput.setText(savedUrl)
        }
    }

    /**
     * Salva l'URL del server nelle preferenze
     */
    private fun saveServerUrl(url: String) {
        val prefs = getSharedPreferences(PREFS_NAME, MODE_PRIVATE)
        prefs.edit().putString(KEY_SERVER_URL, url).apply()
    }

    /**
     * Connetti al server e avvia la DashboardActivity
     */
    private fun connectToServer() {
        var serverUrl = serverUrlInput.text.toString().trim()

        if (serverUrl.isEmpty()) {
            Toast.makeText(this, "Inserisci l'URL del server", Toast.LENGTH_SHORT).show()
            return
        }

        // Validazione di base dell'URL
        if (!serverUrl.startsWith("http://") && !serverUrl.startsWith("https://")) {
            serverUrl = "http://$serverUrl"
            serverUrlInput.setText(serverUrl)
        }

        // Salva l'URL
        saveServerUrl(serverUrl)

        // Avvia l'activity della dashboard
        val intent = Intent(this, DashboardActivity::class.java)
        intent.putExtra("server_url", serverUrl)
        startActivity(intent)
    }
}