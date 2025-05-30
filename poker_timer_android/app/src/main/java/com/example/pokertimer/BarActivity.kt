package com.example.pokertimer

import android.graphics.Color
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.util.Log
import android.view.MenuItem
import android.view.View
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.appcompat.widget.Toolbar
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import androidx.swiperefreshlayout.widget.SwipeRefreshLayout
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import org.json.JSONArray
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL

class BarActivity : AppCompatActivity() {

    private lateinit var recyclerView: RecyclerView
    private lateinit var swipeRefreshLayout: SwipeRefreshLayout
    private lateinit var emptyStateView: View
    private lateinit var adapter: BarRequestAdapter
    private val requests = mutableListOf<BarRequest>()
    private var serverUrl: String? = null

    // Per il refresh automatico
    private val refreshHandler = Handler(Looper.getMainLooper())
    private val refreshInterval = 2000L // 2 secondi

    private val refreshRunnable = object : Runnable {
        override fun run() {
            refreshData(false)
            refreshHandler.postDelayed(this, refreshInterval)
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_bar)

        // Ottieni l'URL del server
        serverUrl = intent.getStringExtra("server_url")
        if (serverUrl.isNullOrEmpty()) {
            Toast.makeText(this, "URL del server non valido", Toast.LENGTH_SHORT).show()
            finish()
            return
        }

        // Setup toolbar
        val toolbar = findViewById<Toolbar>(R.id.toolbar)
        setSupportActionBar(toolbar)
        supportActionBar?.apply {
            title = "Gestione Richieste Bar"
            setDisplayHomeAsUpEnabled(true)
        }

        // Inizializza viste
        recyclerView = findViewById(R.id.requestsRecyclerView)
        swipeRefreshLayout = findViewById(R.id.swipeRefreshLayout)
        emptyStateView = findViewById(R.id.emptyStateView)

        // Setup RecyclerView
        adapter = BarRequestAdapter(requests) { request ->
            completeRequest(request)
        }
        recyclerView.layoutManager = LinearLayoutManager(this)
        recyclerView.adapter = adapter

        // Setup SwipeRefresh
        swipeRefreshLayout.setOnRefreshListener {
            refreshData(true)
        }

        // Carica dati iniziali
        refreshData(true)
    }

    override fun onResume() {
        super.onResume()
        // Avvia il refresh automatico
        refreshHandler.post(refreshRunnable)
    }

    override fun onPause() {
        super.onPause()
        // Ferma il refresh automatico
        refreshHandler.removeCallbacks(refreshRunnable)
    }

    override fun onOptionsItemSelected(item: MenuItem): Boolean {
        return when (item.itemId) {
            android.R.id.home -> {
                onBackPressed()
                true
            }
            else -> super.onOptionsItemSelected(item)
        }
    }

    private fun refreshData(showLoading: Boolean) {
        if (showLoading && !swipeRefreshLayout.isRefreshing) {
            swipeRefreshLayout.isRefreshing = true
        }

        CoroutineScope(Dispatchers.Main).launch {
            try {
                val result = withContext(Dispatchers.IO) {
                    fetchBarRequests()
                }

                swipeRefreshLayout.isRefreshing = false

                if (result != null) {
                    updateUI(result)
                } else {
                    if (showLoading) {
                        Toast.makeText(this@BarActivity, "Errore nel caricamento", Toast.LENGTH_SHORT).show()
                    }
                }
            } catch (e: Exception) {
                swipeRefreshLayout.isRefreshing = false
                if (showLoading) {
                    Toast.makeText(this@BarActivity, "Errore: ${e.message}", Toast.LENGTH_SHORT).show()
                }
            }
        }
    }

    private suspend fun fetchBarRequests(): List<BarRequest>? {
        return try {
            val url = URL("$serverUrl/api/bar_requests")
            val connection = url.openConnection() as HttpURLConnection
            connection.requestMethod = "GET"
            connection.connectTimeout = 5000
            connection.readTimeout = 5000

            val responseCode = connection.responseCode
            if (responseCode == HttpURLConnection.HTTP_OK) {
                val response = connection.inputStream.bufferedReader().use { it.readText() }
                val jsonArray = JSONArray(response)

                val list = mutableListOf<BarRequest>()
                for (i in 0 until jsonArray.length()) {
                    val obj = jsonArray.getJSONObject(i)
                    list.add(BarRequest(
                        id = obj.getString("id"),
                        tableNumber = obj.getInt("table_number"),
                        timestamp = obj.getLong("timestamp")
                    ))
                }

                connection.disconnect()
                list.sortedByDescending { it.timestamp }
            } else {
                connection.disconnect()
                null
            }
        } catch (e: Exception) {
            Log.e("BarActivity", "Error fetching requests", e)
            null
        }
    }

    private fun updateUI(newRequests: List<BarRequest>) {
        requests.clear()
        requests.addAll(newRequests)
        adapter.notifyDataSetChanged()

        if (requests.isEmpty()) {
            recyclerView.visibility = View.GONE
            emptyStateView.visibility = View.VISIBLE
        } else {
            recyclerView.visibility = View.VISIBLE
            emptyStateView.visibility = View.GONE
        }
    }

    private fun completeRequest(request: BarRequest) {
        CoroutineScope(Dispatchers.Main).launch {
            try {
                val success = withContext(Dispatchers.IO) {
                    sendCompleteRequest(request.id)
                }

                if (success) {
                    // Rimuovi dalla lista locale
                    val index = requests.indexOf(request)
                    if (index >= 0) {
                        requests.removeAt(index)
                        adapter.notifyItemRemoved(index)
                    }

                    Toast.makeText(this@BarActivity, "Richiesta completata", Toast.LENGTH_SHORT).show()

                    // Aggiorna UI se lista vuota
                    if (requests.isEmpty()) {
                        recyclerView.visibility = View.GONE
                        emptyStateView.visibility = View.VISIBLE
                    }
                } else {
                    Toast.makeText(this@BarActivity, "Errore nel completare la richiesta", Toast.LENGTH_SHORT).show()
                }
            } catch (e: Exception) {
                Toast.makeText(this@BarActivity, "Errore: ${e.message}", Toast.LENGTH_SHORT).show()
            }
        }
    }

    private suspend fun sendCompleteRequest(requestId: String): Boolean {
        return try {
            val url = URL("$serverUrl/api/bar_requests/$requestId/complete")
            val connection = url.openConnection() as HttpURLConnection
            connection.requestMethod = "POST"
            connection.connectTimeout = 5000

            val responseCode = connection.responseCode
            connection.disconnect()

            responseCode == HttpURLConnection.HTTP_OK
        } catch (e: Exception) {
            Log.e("BarActivity", "Error completing request", e)
            false
        }
    }
}

// Data class per le richieste bar
data class BarRequest(
    val id: String,
    val tableNumber: Int,
    val timestamp: Long
)