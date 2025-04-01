package com.example.pokertimer

import android.content.Intent
import android.os.Bundle
import android.util.Log
import android.view.Menu
import android.view.MenuItem
import android.view.View
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.appcompat.widget.Toolbar
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import androidx.swiperefreshlayout.widget.SwipeRefreshLayout
import com.google.android.material.floatingactionbutton.FloatingActionButton
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import org.json.JSONObject
import java.io.BufferedReader
import java.io.InputStreamReader
import java.net.HttpURLConnection
import java.net.URL

class DashboardActivity : AppCompatActivity() {

    private lateinit var timersRecyclerView: RecyclerView
    private lateinit var swipeRefreshLayout: SwipeRefreshLayout
    private lateinit var emptyStateView: View
    private lateinit var errorStateView: View
    private lateinit var loadingStateView: View
    private lateinit var refreshFab: FloatingActionButton
    private lateinit var refreshButton: Button
    private lateinit var errorRetryButton: Button
    private lateinit var errorMessageText: TextView

    private var serverUrl: String? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_dashboard)

        // Ottieni l'URL del server dall'intent
        serverUrl = intent.getStringExtra("server_url")
        if (serverUrl.isNullOrEmpty()) {
            Toast.makeText(this, "URL del server non valido", Toast.LENGTH_SHORT).show()
            finish()
            return
        }

        // Inizializza la Toolbar
        val toolbar = findViewById<Toolbar>(R.id.toolbar)
        setSupportActionBar(toolbar)

        // Assicurati che il titolo sia visibile nella toolbar
        supportActionBar?.apply {
            title = "Timer Dashboard"
            setDisplayHomeAsUpEnabled(true)
        }

        // Inizializza le viste
        timersRecyclerView = findViewById(R.id.timersRecyclerView)
        swipeRefreshLayout = findViewById(R.id.swipeRefreshLayout)
        emptyStateView = findViewById(R.id.emptyStateView)
        errorStateView = findViewById(R.id.errorStateView)
        loadingStateView = findViewById(R.id.loadingStateView)
        refreshFab = findViewById(R.id.refreshFab)
        refreshButton = findViewById(R.id.refreshButton)
        errorRetryButton = findViewById(R.id.errorRetryButton)
        errorMessageText = findViewById(R.id.errorMessageText)

        // Configura la RecyclerView
        timersRecyclerView.layoutManager = LinearLayoutManager(this)

        // Mostra lo stato iniziale
        showEmptyState()

        // Configura il listener per il pull-to-refresh
        swipeRefreshLayout.setOnRefreshListener { refreshTimerData() }

        // Configura i pulsanti di refresh
        refreshFab.setOnClickListener { refreshTimerData() }
        refreshButton.setOnClickListener { refreshTimerData() }
        errorRetryButton.setOnClickListener { refreshTimerData() }

        // Carica i dati all'inizio
        refreshTimerData()
    }

    override fun onCreateOptionsMenu(menu: Menu): Boolean {
        menuInflater.inflate(R.menu.dashboard_menu, menu)
        return true
    }

    override fun onOptionsItemSelected(item: MenuItem): Boolean {
        return when (item.itemId) {
            android.R.id.home -> {
                onBackPressed()
                true
            }
            R.id.action_refresh -> {
                refreshTimerData()
                true
            }
            R.id.action_change_server -> {
                val intent = Intent(this, ServerUrlActivity::class.java)
                startActivity(intent)
                finish()
                true
            }
            R.id.action_switch_to_timer -> {
                // Passa alla modalità Timer
                val intent = Intent(this, MainActivity::class.java)
                startActivity(intent)
                finish()
                true
            }
            else -> super.onOptionsItemSelected(item)
        }
    }

    /**
     * Aggiorna i dati dei timer
     */
    private fun refreshTimerData() {
        // Mostra lo stato di caricamento
        showLoadingState()

        // Creare una richiesta HTTP per ottenere i dati dei timer dal server
        val timerUrl = "$serverUrl/api/timers"  // Endpoint per ottenere i timer

        // Utilizzare le coroutine per effettuare la richiesta HTTP
        CoroutineScope(Dispatchers.Main).launch {
            try {
                val result = withContext(Dispatchers.IO) {
                    fetchTimersFromServer(timerUrl)
                }

                // Nascondi l'indicatore di refresh
                swipeRefreshLayout.isRefreshing = false

                if (result.startsWith("ERROR:")) {
                    // Gestisce l'errore
                    showErrorState(result.substring(6)) // rimuove "ERROR:"
                    return@launch
                }

                try {
                    // Tenta di analizzare la risposta come JSON
                    val jsonResponse = JSONObject(result)

                    // Controlla se ci sono timer
                    if (jsonResponse.length() == 0) {
                        showEmptyState()
                        return@launch
                    }

                    // Qui elaboreremmo il JSON per mostrare i timer
                    // Per debugging, logga il risultato
                    Log.d("DashboardActivity", "Timer ricevuti: $result")

                    // Se ci sono timer, mostrarli
                    if (jsonResponse.length() > 0) {
                        // Per ora, mostra lo stato vuoto (da modificare con l'implementazione reale)
                        showEmptyState()

                        // TODO: Implementare l'adapter per i timer
                        // val timers = parseTimers(jsonResponse)
                        // val adapter = TimerAdapter(timers)
                        // timersRecyclerView.adapter = adapter
                        // showTimersList()
                    } else {
                        showEmptyState()
                    }

                } catch (e: Exception) {
                    e.printStackTrace()
                    showErrorState("Errore nella lettura dei dati: ${e.message}")
                }

            } catch (e: Exception) {
                e.printStackTrace()
                swipeRefreshLayout.isRefreshing = false
                showErrorState("Errore di connessione: ${e.message}")
            }
        }
    }

    /**
     * Funzione di supporto per il fetch dei dati
     */
    private suspend fun fetchTimersFromServer(url: String): String {
        return try {
            val connection = URL(url).openConnection() as HttpURLConnection
            connection.requestMethod = "GET"
            connection.connectTimeout = 5000
            connection.readTimeout = 5000

            val responseCode = connection.responseCode
            if (responseCode == HttpURLConnection.HTTP_OK) {
                // Leggi la risposta
                val reader = BufferedReader(InputStreamReader(connection.inputStream))
                val response = StringBuilder()
                var line: String?
                while (reader.readLine().also { line = it } != null) {
                    response.append(line)
                }
                reader.close()
                response.toString()
            } else {
                "ERROR:Errore del server: $responseCode"
            }
        } catch (e: Exception) {
            e.printStackTrace()
            "ERROR:${e.message}"
        }
    }

    /**
     * Mostra lo stato di caricamento
     */
    private fun showLoadingState() {
        loadingStateView.visibility = View.VISIBLE
        emptyStateView.visibility = View.GONE
        errorStateView.visibility = View.GONE
        timersRecyclerView.visibility = View.GONE
    }

    /**
     * Mostra lo stato vuoto quando non ci sono timer
     */
    private fun showEmptyState() {
        loadingStateView.visibility = View.GONE
        emptyStateView.visibility = View.VISIBLE
        errorStateView.visibility = View.GONE
        timersRecyclerView.visibility = View.GONE
    }

    /**
     * Mostra lo stato di errore
     */
    private fun showErrorState(message: String) {
        loadingStateView.visibility = View.GONE
        emptyStateView.visibility = View.GONE
        errorStateView.visibility = View.VISIBLE
        timersRecyclerView.visibility = View.GONE

        errorMessageText.text = message
    }

    /**
     * Mostra la lista dei timer
     */
    private fun showTimersList() {
        loadingStateView.visibility = View.GONE
        emptyStateView.visibility = View.GONE
        errorStateView.visibility = View.GONE
        timersRecyclerView.visibility = View.VISIBLE
    }
}