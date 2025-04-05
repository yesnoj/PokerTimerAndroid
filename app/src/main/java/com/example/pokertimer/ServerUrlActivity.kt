package com.example.pokertimer

import android.app.ProgressDialog
import android.content.Intent
import android.os.Bundle
import android.text.TextUtils
import android.util.Log
import android.view.View
import android.widget.Button
import android.widget.EditText
import android.widget.ImageView
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import java.net.DatagramPacket
import java.net.DatagramSocket
import java.net.InetAddress
import java.net.SocketTimeoutException

class ServerUrlActivity : AppCompatActivity() {

    companion object {
        private const val PREFS_NAME = "server_url_prefs"
        private const val KEY_SERVER_URL = "server_url"
        private const val DISCOVERY_PORT = 8888
        private const val DISCOVERY_TIMEOUT_MS = 3000
        private const val TAG = "ServerUrlActivity"
    }

    private lateinit var serverUrlInput: EditText
    private lateinit var connectButton: Button
    private lateinit var discoverButton: Button

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_server_url)

        // Inizializza le viste
        serverUrlInput = findViewById(R.id.serverUrlInput)
        connectButton = findViewById(R.id.connectButton)
        discoverButton = findViewById(R.id.discoverButton) // Aggiungi questo pulsante al tuo layout
        val backButton = findViewById<ImageView>(R.id.backButton)

        // Carica l'URL salvato
        loadSavedServerUrl()

        // Imposta il listener per il pulsante indietro
        backButton.setOnClickListener { finish() }

        // Imposta il listener per il pulsante di connessione
        connectButton.setOnClickListener { connectToServer() }

        // Imposta il listener per il pulsante di discovery
        discoverButton.setOnClickListener { discoverServers() }
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

    /**
     * Cerca server disponibili sulla rete locale tramite UDP broadcast
     */
    private fun discoverServers() {
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

                Log.d(TAG, "Sending discovery broadcast to port $DISCOVERY_PORT")

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
                        showDiscoveredServers(discoveredServers)
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
    private fun showDiscoveredServers(servers: List<String>) {
        if (servers.size == 1) {
            // Se è stato trovato un solo server, selezionalo automaticamente
            val serverUrl = servers[0]
            serverUrlInput.setText(serverUrl)
            Toast.makeText(this, "Server trovato: $serverUrl", Toast.LENGTH_SHORT).show()
        } else {
            // Mostra una lista di selezione
            val builder = AlertDialog.Builder(this)
            builder.setTitle("Server trovati")

            builder.setItems(servers.toTypedArray()) { _, which ->
                val selectedServer = servers[which]
                serverUrlInput.setText(selectedServer)
            }

            builder.setNegativeButton("Annulla", null)
            builder.show()
        }
    }
}