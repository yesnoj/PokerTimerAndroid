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
import java.net.HttpURLConnection
import java.net.URL
import android.content.res.ColorStateList
import android.graphics.Color
import androidx.core.content.ContextCompat

class ServerUrlActivity : AppCompatActivity() {

    companion object {
        private const val PREFS_NAME = "server_url_prefs"
        private const val KEY_SERVER_URL = "server_url"
        private const val KEY_IS_CONNECTED = "is_connected"
        private const val DISCOVERY_PORT = 8888
        private const val DISCOVERY_TIMEOUT_MS = 8000
        private const val TAG = "ServerUrlActivity"
    }

    private lateinit var serverUrlInput: EditText
    private lateinit var connectButton: Button
    private lateinit var discoverButton: Button
    private lateinit var disconnectButton: Button
    private var isConnected = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_server_url)

        // Inizializza le viste
        serverUrlInput = findViewById(R.id.serverUrlInput)
        connectButton = findViewById(R.id.connectButton)
        disconnectButton = findViewById(R.id.disconnectButton) // Nuovo pulsante Disconnetti
        discoverButton = findViewById(R.id.discoverButton)
        val backButton = findViewById<ImageView>(R.id.backButton)

        // Carica l'URL salvato
        loadSavedServerUrl()

        // Verifica lo stato di connessione
        checkConnectionState()

        // Imposta il listener per il pulsante indietro
        backButton.setOnClickListener { finish() }

        // Imposta il listener per il pulsante di discovery
        discoverButton.setOnClickListener { discoverServers() }

        // Imposta il listener per il pulsante di disconnessione
        disconnectButton.setOnClickListener { disconnectFromServer() }
    }
    /**
     * Disconnetti dal server
     */
    private fun disconnectFromServer() {
        // Modifica lo stato di connessione
        isConnected = false

        // Salva lo stato nelle preferenze
        val prefs = getSharedPreferences(PREFS_NAME, MODE_PRIVATE)
        prefs.edit().putBoolean(KEY_IS_CONNECTED, false).apply()

        // Aggiorna lo stato dei pulsanti
        updateConnectionButtonsState(false)

        // Mostra un messaggio di conferma
        Toast.makeText(this, "Disconnesso dal server", Toast.LENGTH_SHORT).show()
    }

    /**
     * Aggiorna lo stato dei pulsanti di connessione
     */
    /**
     * Aggiorna lo stato dei pulsanti di connessione
     */
    private fun updateConnectionButtonsState(connected: Boolean) {
        isConnected = connected

        if (connected) {
            // Se connesso, abilita Disconnetti e modifica Connetti
            disconnectButton.isEnabled = true
            connectButton.isEnabled = true
            connectButton.text = "Vai al server"
            connectButton.setBackgroundTintList(ColorStateList.valueOf(ContextCompat.getColor(this, R.color.status_color)))
            connectButton.setTextColor(Color.WHITE)

            // Configura il pulsante per andare alla dashboard
            connectButton.setOnClickListener {
                val intent = Intent(this, DashboardActivity::class.java)
                intent.putExtra("server_url", serverUrlInput.text.toString())
                startActivity(intent)
            }
        } else {
            // Se disconnesso, disabilita Disconnetti e ripristina Connetti
            disconnectButton.isEnabled = false
            connectButton.isEnabled = true
            connectButton.text = "Connetti"
            connectButton.setBackgroundTintList(ColorStateList.valueOf(ContextCompat.getColor(this, R.color.status_color)))
            connectButton.setTextColor(Color.WHITE)

            // Configura il pulsante per connettersi
            connectButton.setOnClickListener { connectToServer() }
        }
    }

    private fun checkConnectionState() {
        val prefs = getSharedPreferences(PREFS_NAME, MODE_PRIVATE)
        val isConnected = prefs.getBoolean(KEY_IS_CONNECTED, false)

        // Aggiorna lo stato dei pulsanti
        updateConnectionButtonsState(isConnected)

        // Se è connesso, configura il pulsante Connect per andare alla dashboard
        if (isConnected) {
            connectButton.setOnClickListener {
                // Avvia la DashboardActivity
                val intent = Intent(this, DashboardActivity::class.java)
                intent.putExtra("server_url", serverUrlInput.text.toString())
                startActivity(intent)
            }
        } else {
            // Se non è connesso, configura il pulsante per connettersi
            connectButton.setOnClickListener { connectToServer() }
        }
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

        // Tenta di connettersi prima di procedere
        val progressDialog = ProgressDialog(this).apply {
            setMessage("Connessione in corso...")
            setCancelable(false)
            show()
        }

        // Test di connessione
        Thread {
            try {
                val url = URL("$serverUrl/api/timers")
                val connection = url.openConnection() as HttpURLConnection
                connection.requestMethod = "GET"
                connection.connectTimeout = 5000

                val responseCode = connection.responseCode
                connection.disconnect()

                runOnUiThread {
                    progressDialog.dismiss()

                    if (responseCode == HttpURLConnection.HTTP_OK) {
                        // Connessione riuscita
                        Toast.makeText(this, "Connessione riuscita", Toast.LENGTH_SHORT).show()

                        // Salva lo stato di connessione
                        val prefs = getSharedPreferences(PREFS_NAME, MODE_PRIVATE)
                        prefs.edit()
                            .putBoolean(KEY_IS_CONNECTED, true)
                            .putString(KEY_SERVER_URL, serverUrl)
                            .apply()

                        // Aggiorna lo stato dei pulsanti
                        updateConnectionButtonsState(true)

                        // Avvia l'activity della dashboard
                        val intent = Intent(this, DashboardActivity::class.java)
                        intent.putExtra("server_url", serverUrl)
                        startActivity(intent)
                    } else {
                        // Connessione fallita
                        Toast.makeText(this, "Errore di connessione: $responseCode", Toast.LENGTH_SHORT).show()
                    }
                }
            } catch (e: Exception) {
                runOnUiThread {
                    progressDialog.dismiss()
                    Toast.makeText(this, "Errore: ${e.message}", Toast.LENGTH_SHORT).show()
                }
            }
        }.start()
    }    /**
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

                Log.d(TAG, "Sending discovery broadcasts to port $DISCOVERY_PORT")

                // Invia più pacchetti di broadcast per aumentare le possibilità di successo
                // Invia 3 pacchetti con un intervallo di 300ms tra l'uno e l'altro
                for (i in 0 until 3) {
                    // Invia il broadcast
                    socket.send(packet)
                    Log.d(TAG, "Sent discovery broadcast #${i+1}")

                    // Breve pausa tra i pacchetti
                    if (i < 2) { // Non dormiamo dopo l'ultimo pacchetto
                        Thread.sleep(300)
                    }
                }

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
                    Log.d(TAG, "Discovery timeout reached after ${DISCOVERY_TIMEOUT_MS}ms")
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