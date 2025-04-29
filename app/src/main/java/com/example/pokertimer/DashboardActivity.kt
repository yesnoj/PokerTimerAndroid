package com.example.pokertimer

import android.app.Dialog
import android.graphics.Color
import android.widget.RadioButton
import android.widget.RadioGroup
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.util.Log
import android.view.Menu
import android.view.MenuItem
import android.view.View
import android.widget.Button
import android.widget.LinearLayout
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.appcompat.widget.Toolbar
import androidx.core.app.ActivityCompat
import androidx.core.app.NotificationManagerCompat
import androidx.core.content.ContextCompat
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import androidx.swiperefreshlayout.widget.SwipeRefreshLayout
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import org.json.JSONObject
import java.io.BufferedReader
import java.io.InputStreamReader
import java.net.HttpURLConnection
import java.net.URL
import android.provider.Settings
import android.net.Uri
import androidx.core.app.NotificationCompat
import android.app.Notification
import android.graphics.PorterDuff
import android.graphics.drawable.ColorDrawable
import android.view.Window
import android.view.WindowManager
import android.widget.Switch
import android.widget.AdapterView
import android.widget.ArrayAdapter
import android.widget.ImageView
import android.widget.Spinner

/**
 * Classe singleton per tenere traccia delle notifiche dei posti liberi già mostrate
 */
object SeatNotificationTracker {
    // Map per tenere traccia dei posti già notificati per ogni tavolo
    private val notifiedSeats = mutableMapOf<String, String>()

    /**
     * Verifica se una combinazione di posti per un timer specifico è già stata notificata
     * @return true se è una nuova notifica, false se è già stata mostrata
     */
    fun isNewNotification(deviceId: String, seatInfo: String): Boolean {
        val previousInfo = notifiedSeats[deviceId]
        return previousInfo != seatInfo
    }

    /**
     * Segna una notifica come visualizzata
     */
    fun markAsNotified(deviceId: String, seatInfo: String) {
        notifiedSeats[deviceId] = seatInfo
    }

    /**
     * Rimuove un timer dalla lista delle notifiche
     */
    fun clearNotification(deviceId: String) {
        notifiedSeats.remove(deviceId)
    }
}

class DashboardActivity : AppCompatActivity(), TimerAdapter.TimerActionListener {

    // Costanti per il refresh automatico
    private val AUTO_REFRESH_INTERVAL_MS = 1000L // 1 secondo
    private var timerRefreshHandler: Handler? = null
    private var refreshRunnable: Runnable? = null

    // Costanti per le notifiche
    companion object {
        private const val NOTIFICATION_CHANNEL_ID = "poker_timer_seats"
        private const val NOTIFICATION_ID = 1001
        private const val ONLINE_TIMEOUT_MINUTES = 3 // Timeout per considerare un timer online
    }

    private lateinit var timersRecyclerView: RecyclerView
    private lateinit var swipeRefreshLayout: SwipeRefreshLayout
    private lateinit var emptyStateView: View
    private lateinit var errorStateView: View
    private lateinit var loadingStateView: View
    private lateinit var errorMessageText: TextView
    private lateinit var filteredCountText: TextView

    private var serverUrl: String? = null
    private lateinit var timerAdapter: TimerAdapter
    private val allTimerList = mutableListOf<TimerItem>()
    private val filteredTimerList = mutableListOf<TimerItem>()
    private var currentFilter = TimerFilterOption.ALL

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_dashboard)

        // Verifica e richiedi il permesso per le notifiche su Android 13+
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            if (ContextCompat.checkSelfPermission(
                    this,
                    android.Manifest.permission.POST_NOTIFICATIONS
                ) != PackageManager.PERMISSION_GRANTED
            ) {
                Log.d("DashboardActivity", "Richiedo permesso POST_NOTIFICATIONS")
                ActivityCompat.requestPermissions(
                    this,
                    arrayOf(android.Manifest.permission.POST_NOTIFICATIONS),
                    100
                )
            } else {
                Log.d("DashboardActivity", "Permesso POST_NOTIFICATIONS già concesso")
            }
        }

        // Inizializza l'handler per l'aggiornamento periodico
        timerRefreshHandler = Handler(Looper.getMainLooper())

        // Crea il runnable per l'aggiornamento
        refreshRunnable = object : Runnable {
            override fun run() {
                refreshTimerData(false) // Non mostrare lo stato di caricamento per gli aggiornamenti automatici
                timerRefreshHandler?.postDelayed(this, AUTO_REFRESH_INTERVAL_MS)
            }
        }

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
        val errorRetryButton = findViewById<Button>(R.id.errorRetryButton)
        errorMessageText = findViewById(R.id.errorMessageText)

        try {
            filteredCountText = findViewById(R.id.filteredCountText)
        } catch (e: Exception) {
            Log.e("DashboardActivity", "Elemento filteredCountText non trovato nel layout", e)
        }

        // Configura la RecyclerView
        timerAdapter = TimerAdapter(this, filteredTimerList, this)
        timersRecyclerView.layoutManager = LinearLayoutManager(this)
        timersRecyclerView.adapter = timerAdapter

        // Crea il canale di notifica
        createNotificationChannel()

        // Verifica le impostazioni di notifica
        checkNotificationSettings()

        // Mostra lo stato iniziale
        showEmptyState()

        // Configura il listener per il pull-to-refresh
        swipeRefreshLayout.setOnRefreshListener { refreshTimerData(true) }

        // Configura i pulsanti di refresh
        errorRetryButton.setOnClickListener { refreshTimerData(true) }

        // Verifica l'intent iniziale per eventuali azioni di notifica
        handleNotificationIntent(intent)

        // Carica i dati all'inizio
        refreshTimerData(true)

        toolbar.overflowIcon?.setColorFilter(Color.WHITE, PorterDuff.Mode.SRC_ATOP)
    }

    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        handleNotificationIntent(intent)
    }

    override fun onRequestPermissionsResult(
        requestCode: Int,
        permissions: Array<out String>,
        grantResults: IntArray
    ) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)

        if (requestCode == 100) {
            // Verifica se la richiesta di permesso per le notifiche è stata accettata
            if (grantResults.isNotEmpty() && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                Log.d("DashboardActivity", "Autorizzazione notifiche concessa")
                Toast.makeText(this, "Notifiche autorizzate", Toast.LENGTH_SHORT).show()

                // Opzionale: mostra una notifica di test per verificare che tutto funzioni
                Handler(Looper.getMainLooper()).postDelayed({
                    showTestNotification()
                }, 1000)
            } else {
                Log.d("DashboardActivity", "Autorizzazione notifiche negata")
                Toast.makeText(this, "Le notifiche non saranno mostrate", Toast.LENGTH_SHORT).show()

                // Indirizza l'utente alle impostazioni dell'app per abilitare manualmente
                AlertDialog.Builder(this)
                    .setTitle("Notifiche disabilitate")
                    .setMessage("Le notifiche sono necessarie per avvisarti di nuovi posti liberi. Vuoi abilitarle nelle impostazioni?")
                    .setPositiveButton("Impostazioni") { _, _ ->
                        val intent = Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS)
                        intent.data = Uri.fromParts("package", packageName, null)
                        startActivity(intent)
                    }
                    .setNegativeButton("No, grazie", null)
                    .show()
            }
        }
    }

    /**
     * Mostra una notifica di test per verificare che il sistema di notifiche funzioni
     */
    /**
     * Mostra una notifica di test per verificare che il sistema di notifiche funzioni
     */
    private fun showTestNotification() {
        try {
            val title = "Test Notifica"
            val content = "Le notifiche funzionano correttamente"

            // Crea un intent per aprire la dashboard quando la notifica viene toccata
            val intent = Intent(this, DashboardActivity::class.java).apply {
                flags = Intent.FLAG_ACTIVITY_CLEAR_TOP or Intent.FLAG_ACTIVITY_SINGLE_TOP
                // IMPORTANTE: Includi l'URL del server nell'intent
                putExtra("server_url", serverUrl)
            }

            val pendingIntent = PendingIntent.getActivity(
                this, 0, intent,
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
                    PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
                } else {
                    PendingIntent.FLAG_UPDATE_CURRENT
                }
            )

            // Crea la notifica con priorità elevata
            val builder = NotificationCompat.Builder(this, NOTIFICATION_CHANNEL_ID)
                .setSmallIcon(R.drawable.ic_timer)
                .setContentTitle(title)
                .setContentText(content)
                .setPriority(NotificationCompat.PRIORITY_HIGH)  // Priorità alta
                .setCategory(NotificationCompat.CATEGORY_MESSAGE)  // Categoria messaggio
                .setVisibility(NotificationCompat.VISIBILITY_PUBLIC)  // Visibile nella lock screen
                .setContentIntent(pendingIntent)
                .setAutoCancel(true) // La notifica si chiude quando viene toccata

            // Mostra la notifica
            with(NotificationManagerCompat.from(this)) {
                // Verifica il permesso di notifica (Android 13+)
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
                    if (ActivityCompat.checkSelfPermission(
                            this@DashboardActivity,
                            android.Manifest.permission.POST_NOTIFICATIONS
                        ) != PackageManager.PERMISSION_GRANTED
                    ) {
                        Log.e("DashboardActivity", "Permesso notifiche non disponibile")
                        return
                    }
                }

                Log.d("DashboardActivity", "Sto mostrando la notifica di test")
                notify(999, builder.build())
            }
        } catch (e: Exception) {
            Log.e("DashboardActivity", "Errore mostrando la notifica di test", e)
        }
    }

    private fun handleNotificationIntent(intent: Intent) {
        // Gestisci l'apertura da notifica
        if (intent.hasExtra("table_number") && intent.hasExtra("highlight_timer")) {
            val tableNumber = intent.getIntExtra("table_number", -1)
            val timerDeviceId = intent.getStringExtra("highlight_timer")

            // Trova la posizione del timer
            if (tableNumber != -1 && timerDeviceId != null) {
                // Aspetta che la recyclerView sia pronta
                timersRecyclerView.post {
                    val position = filteredTimerList.indexOfFirst { it.tableNumber == tableNumber }
                    if (position >= 0) {
                        // Scrolla alla posizione del timer
                        timersRecyclerView.smoothScrollToPosition(position)

                        // Evidenzia la card
                        highlightTimerCard(position)
                    }
                }
            }
        }
    }

    override fun onResume() {
        super.onResume()
        // Avvia l'aggiornamento automatico quando l'activity è visibile
        startAutoRefresh()
    }

    override fun onPause() {
        super.onPause()
        // Ferma l'aggiornamento automatico quando l'activity non è visibile
        stopAutoRefresh()
    }

    override fun onDestroy() {
        super.onDestroy()
        // Assicurati di rimuovere il runnable quando l'activity viene distrutta
        stopAutoRefresh()
        timerRefreshHandler = null
        refreshRunnable = null
    }

    /**
     * Crea il canale di notifica (richiesto per Android 8.0+)
     */
    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val name = "Poker Timer Urgent Notifications"
            val descriptionText = "Notifiche urgenti per posti liberi nei tavoli"
            val importance = NotificationManager.IMPORTANCE_HIGH
            val channel = NotificationChannel(NOTIFICATION_CHANNEL_ID, name, importance).apply {
                description = descriptionText
                enableLights(true)
                lightColor = Color.RED
                enableVibration(true)
                vibrationPattern = longArrayOf(0, 250, 250, 250)
                setShowBadge(true)
                lockscreenVisibility = Notification.VISIBILITY_PUBLIC
                // Rimuovi questa riga che sta causando l'errore:
                // importance = NotificationManager.IMPORTANCE_HIGH
            }

            val notificationManager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
            notificationManager.createNotificationChannel(channel)

            // Log per verificare che il canale sia stato creato correttamente
            Log.d("DashboardActivity", "Canale di notifica creato con importance: ${channel.importance}")
        }
    }

    /**
     * Avvia l'aggiornamento automatico dei timer
     */
    private fun startAutoRefresh() {
        // Ferma eventuali aggiornamenti esistenti
        stopAutoRefresh()

        // Avvia il nuovo ciclo di aggiornamenti
        refreshRunnable?.let {
            timerRefreshHandler?.post(it)
        }
    }

    /**
     * Ferma l'aggiornamento automatico dei timer
     */
    private fun stopAutoRefresh() {
        refreshRunnable?.let {
            timerRefreshHandler?.removeCallbacks(it)
        }
    }

    override fun onCreateOptionsMenu(menu: Menu): Boolean {
        menuInflater.inflate(R.menu.dashboard_menu, menu)
        return true
    }

    /**
     * Ricarica i dati dal server con un ritardo
     * @param showLoading Determina se mostrare lo stato di caricamento
     * @param delayMs Ritardo in millisecondi prima di effettuare il refresh
     */
    private fun delayedRefreshTimerData(showLoading: Boolean = false, delayMs: Long = 500) {
        Handler(Looper.getMainLooper()).postDelayed({
            refreshTimerData(showLoading)
        }, delayMs)
    }

    /**
     * Aggiorna i dati dei timer
     * @param showLoading Determina se mostrare lo stato di caricamento
     */
    private fun refreshTimerData(showLoading: Boolean = true) {
        // Mostra lo stato di caricamento solo quando richiesto
        if (showLoading && !swipeRefreshLayout.isRefreshing) {
            showLoadingState()
        }

        // Creare una richiesta HTTP per ottenere i dati dei timer dal server
        val timerUrl = "$serverUrl/api/timers"  // Endpoint per ottenere i timer

        // Utilizzare le coroutine per effettuare la richiesta HTTP
        CoroutineScope(Dispatchers.Main).launch {
            try {
                val result = withContext(Dispatchers.IO) {
                    fetchTimersFromServer(timerUrl)
                }

                // Nascondi l'indicatore di refresh se attivo
                if (swipeRefreshLayout.isRefreshing) {
                    swipeRefreshLayout.isRefreshing = false
                }

                if (result.startsWith("ERROR:")) {
                    // Gestisce l'errore solo se era un refresh manuale
                    if (showLoading) {
                        showErrorState(result.substring(6)) // rimuove "ERROR:"
                    }
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

                    // Parsa i timer dal JSON
                    val parsedTimers = jsonResponse.parseTimers()

                    // Creiamo una mappa dei timer esistenti per id per un accesso più rapido
                    val existingTimersMap = allTimerList.associateBy { it.deviceId }

                    // Aggiorna la lista principale dei timer, ma conserva le informazioni sui posti
                    val updatedTimers = parsedTimers.map { newTimer ->
                        // Cerca il timer esistente corrispondente
                        val existingTimer = existingTimersMap[newTimer.deviceId]

                        if (existingTimer != null && existingTimer.hasSeatOpenInfo()) {
                            // Se il timer esistente ha info sui posti liberi
                            val existingSeatInfo = existingTimer.seatOpenInfo ?: ""

                            // Verifica se ci sono nuove informazioni sui posti
                            if (newTimer.hasSeatOpenInfo()) {
                                val newSeatInfo = newTimer.seatOpenInfo ?:
                                (if (newTimer.pendingCommand?.startsWith("seat_open:") == true)
                                    newTimer.pendingCommand.substringAfter("seat_open:").trim()
                                else "")

                                if (newSeatInfo.isNotEmpty()) {
                                    // Combina le informazioni sui posti (esistenti + nuovi)
                                    val combinedSeats = combineSeats(existingSeatInfo, newSeatInfo)

                                    // Crea una copia del nuovo timer con le informazioni sui posti combinate
                                    newTimer.copy(
                                        seatOpenInfo = combinedSeats,
                                        // Rimuovi pendingCommand per evitare duplicati
                                        pendingCommand = null
                                    )
                                } else {
                                    // Mantieni le informazioni sui posti esistenti
                                    newTimer.copy(
                                        seatOpenInfo = existingSeatInfo,
                                        pendingCommand = null
                                    )
                                }
                            } else {
                                // Mantieni le informazioni sui posti esistenti
                                newTimer.copy(
                                    seatOpenInfo = existingSeatInfo
                                )
                            }
                        } else {
                            // Nessuna informazione precedente sui posti, usa i nuovi dati così come sono
                            newTimer
                        }
                    }

                    // Aggiorna la lista principale dei timer
                    allTimerList.clear()
                    allTimerList.addAll(updatedTimers)

                    // Log per debug - verifica le informazioni sui posti liberi
                    for (timer in allTimerList) {
                        if (timer.hasSeatOpenInfo()) {
                            Log.d("DashboardActivity", "Timer ${timer.deviceId} ha informazioni su posti liberi: ${timer.getFormattedSeatInfo()}")

                            // Controlla se ci sono nuove informazioni da notificare
                            val seatInfo = timer.seatOpenInfo ?:
                            (if (timer.pendingCommand?.startsWith("seat_open:") == true)
                                timer.pendingCommand.substringAfter("seat_open:").trim()
                            else "")

                            if (seatInfo.isNotEmpty() && SeatNotificationTracker.isNewNotification(timer.deviceId, seatInfo)) {
                                // Mostra una notifica all'utente
                                showSeatOpenNotification(timer, seatInfo)

                                // Segna questa notifica come visualizzata
                                SeatNotificationTracker.markAsNotified(timer.deviceId, seatInfo)
                            }
                        } else {
                            // Controlla anche pendingCommand
                            if (timer.pendingCommand != null) {
                                Log.d("DashboardActivity", "Timer ${timer.deviceId} ha pendingCommand: ${timer.pendingCommand}")
                            }
                        }
                    }

                    // Applica il filtro corrente e aggiorna la UI
                    updateFilteredList()

                } catch (e: Exception) {
                    e.printStackTrace()
                    if (showLoading) {
                        showErrorState("Errore nella lettura dei dati: ${e.message}")
                    }
                }

            } catch (e: Exception) {
                e.printStackTrace()
                if (swipeRefreshLayout.isRefreshing) {
                    swipeRefreshLayout.isRefreshing = false
                }
                if (showLoading) {
                    showErrorState("Errore di connessione: ${e.message}")
                }
            }
        }
    }

    /**
     * Combina le informazioni sui posti esistenti con quelle nuove
     * evitando duplicati e mantenendo il formato corretto
     */
    private fun combineSeats(existingSeats: String, newSeats: String): String {
        // Controlla se ci sono dati da combinare
        if (existingSeats.isEmpty()) return newSeats
        if (newSeats.isEmpty()) return existingSeats

        // Converti le stringhe in liste di numeri
        val existingList = existingSeats.split(",").map { it.trim() }.filter { it.isNotEmpty() }
        val newList = newSeats.split(",").map { it.trim() }.filter { it.isNotEmpty() }

        // Combina le liste evitando duplicati
        val combinedList = (existingList + newList).distinct()

        // Riconverti in stringa con formato "1, 2, 3"
        return combinedList.joinToString(", ")
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
     * Mostra una notifica standard per nuovi posti liberi
     */
    private fun showSeatOpenNotification(timer: TimerItem, seatInfo: String) {
        val title = "⚠️ POSTI LIBERI"  // Emoji per attirare l'attenzione
        val content = "Tavolo ${timer.tableNumber}: $seatInfo"

        try {
            // Intent principale
            val intent = Intent(this, DashboardActivity::class.java).apply {
                flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP
                putExtra("table_number", timer.tableNumber)
                putExtra("highlight_timer", timer.deviceId)
                putExtra("server_url", serverUrl)
            }

            val pendingIntent = PendingIntent.getActivity(
                this,
                timer.tableNumber, // Uso del tableNumber come requestCode per avere PendingIntent diversi
                intent,
                PendingIntent.FLAG_UPDATE_CURRENT or (if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) PendingIntent.FLAG_IMMUTABLE else 0)
            )

            // Crea un'azione per la notifica
            val actionIntent = Intent(this, DashboardActivity::class.java).apply {
                action = "com.example.pokertimer.VIEW_SEATS"
                putExtra("table_number", timer.tableNumber)
                putExtra("highlight_timer", timer.deviceId)
                putExtra("server_url", serverUrl)
            }

            val actionPendingIntent = PendingIntent.getActivity(
                this,
                timer.tableNumber + 100, // Un requestCode diverso
                actionIntent,
                PendingIntent.FLAG_UPDATE_CURRENT or (if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) PendingIntent.FLAG_IMMUTABLE else 0)
            )

            val action = NotificationCompat.Action.Builder(
                R.drawable.ic_timer,
                "Vedi Dettagli",
                actionPendingIntent
            ).build()

            // Costruisci la notifica con tutte le opzioni per massimizzare la visibilità
            val builder = NotificationCompat.Builder(this, NOTIFICATION_CHANNEL_ID)
                .setSmallIcon(R.drawable.ic_timer)
                .setContentTitle(title)
                .setContentText(content)
                .setPriority(NotificationCompat.PRIORITY_MAX)
                .setCategory(NotificationCompat.CATEGORY_ALARM) // ALARM è più intrusivo di CALL
                .setVisibility(NotificationCompat.VISIBILITY_PUBLIC)
                .setContentIntent(pendingIntent)
                .addAction(action)
                .setAutoCancel(true)
                .setFullScreenIntent(pendingIntent, true)
                .setTimeoutAfter(10000) // 10 secondi
                .setOngoing(true) // Rende persistente la notifica
                .setDefaults(NotificationCompat.DEFAULT_ALL) // Suoni, vibrazione e luci LED

            // Aggiunta di stile per notifiche espandibili
            val bigTextStyle = NotificationCompat.BigTextStyle()
                .bigText("Posti liberi al tavolo ${timer.tableNumber}: $seatInfo\nTocca per visualizzare i dettagli.")
                .setBigContentTitle("⚠️ POSTI LIBERI DISPONIBILI")
                .setSummaryText("Notifica urgente")

            builder.setStyle(bigTextStyle)

            // Imposta vibrazione personalizzata (pattern più lungo e intenso)
            val vibratePattern = longArrayOf(0, 400, 200, 400, 200, 400)
            builder.setVibrate(vibratePattern)

            // Log prima di mostrare la notifica
            Log.d("DashboardActivity", "Mostrando notifica per tavolo ${timer.tableNumber} con posti: $seatInfo")

            // Verifica e richiedi permessi se necessario
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
                if (ActivityCompat.checkSelfPermission(
                        this@DashboardActivity,
                        android.Manifest.permission.POST_NOTIFICATIONS
                    ) != PackageManager.PERMISSION_GRANTED
                ) {
                    Log.e("DashboardActivity", "Permesso notifiche mancante!")
                    return
                }
            }

            // Ottieni il NotificationManager
            val notificationManager = NotificationManagerCompat.from(this)

            // Mostra la notifica e verifica il risultato
            notificationManager.notify(NOTIFICATION_ID + timer.tableNumber.hashCode(), builder.build())
            Log.d("DashboardActivity", "Notifica inviata con successo")

            // Richiama la notifica subito dopo averla mostrata per attrarre ulteriormente l'attenzione
            Handler(Looper.getMainLooper()).postDelayed({
                notificationManager.notify(NOTIFICATION_ID + timer.tableNumber.hashCode(), builder.build())
                Log.d("DashboardActivity", "Notifica richiamata dopo 500ms")
            }, 500)
        } catch (e: Exception) {
            Log.e("DashboardActivity", "Errore durante l'invio della notifica", e)
        }
    }

    private fun checkNotificationSettings() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val notificationManager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
            val channel = notificationManager.getNotificationChannel(NOTIFICATION_CHANNEL_ID)

            if (channel != null && channel.importance != NotificationManager.IMPORTANCE_HIGH) {
                // Il canale esiste ma non ha l'importanza corretta
                AlertDialog.Builder(this)
                    .setTitle("Notifiche non configurate correttamente")
                    .setMessage("Le notifiche potrebbero non apparire come popup. Vuoi configurare le impostazioni di notifica?")
                    .setPositiveButton("Impostazioni") { _, _ ->
                        // Apri le impostazioni del canale di notifica specifico
                        val intent = Intent(Settings.ACTION_CHANNEL_NOTIFICATION_SETTINGS).apply {
                            putExtra(Settings.EXTRA_APP_PACKAGE, packageName)
                            putExtra(Settings.EXTRA_CHANNEL_ID, NOTIFICATION_CHANNEL_ID)
                        }
                        startActivity(intent)
                    }
                    .setNegativeButton("No grazie", null)
                    .show()
            }
        }
    }

    /**
     * Evidenzia brevemente una card del timer
     */
    private fun highlightTimerCard(position: Int) {
        val viewHolder = timersRecyclerView.findViewHolderForAdapterPosition(position)
        val cardView = viewHolder?.itemView

        cardView?.let {
            // Salva il colore di sfondo originale
            val originalBackground = it.background

            // Cambia il colore di sfondo per evidenziare
            it.setBackgroundColor(ContextCompat.getColor(this, R.color.colorAccent))

            // Torna al colore originale dopo un breve periodo
            Handler(Looper.getMainLooper()).postDelayed({
                it.background = originalBackground
            }, 1500) // 1.5 secondi di evidenziazione
        }
    }

    /**
     * Invia un comando a un timer specifico
     */
    private fun sendCommandToTimer(deviceId: String, command: String) {
        // URL corretto basato sul codice server
        val commandUrl = "$serverUrl/api/command/$deviceId"

        CoroutineScope(Dispatchers.Main).launch {
            try {
                val result = withContext(Dispatchers.IO) {
                    sendCommandToServer(commandUrl, command)
                }

                if (result.startsWith("ERROR:")) {
                    Toast.makeText(this@DashboardActivity, result.substring(6), Toast.LENGTH_SHORT).show()
                } else {
                    // Aggiorna i dati dopo aver inviato il comando
                    Toast.makeText(this@DashboardActivity, "Comando '$command' inviato con successo", Toast.LENGTH_SHORT).show()
                    refreshTimerData(false)
                }
            } catch (e: Exception) {
                Toast.makeText(this@DashboardActivity, "Errore nell'invio del comando: ${e.message}", Toast.LENGTH_SHORT).show()
            }
        }
    }

    /**
     * Funzione per inviare comandi al server
     */
    private suspend fun sendCommandToServer(url: String, command: String): String {
        return try {
            val connection = URL(url).openConnection() as HttpURLConnection
            connection.requestMethod = "POST"
            connection.doOutput = true
            connection.setRequestProperty("Content-Type", "application/json; charset=UTF-8")

            // Formato JSON corretto basato sul codice server
            val jsonPayload = """
                {
                    "command": "$command"
                }
            """.trimIndent()

            // Invia i dati
            val outputStream = connection.outputStream
            outputStream.write(jsonPayload.toByteArray())
            outputStream.close()

            val responseCode = connection.responseCode
            if (responseCode == HttpURLConnection.HTTP_OK) {
                "Comando inviato con successo"
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
        if (::filteredCountText.isInitialized) {
            filteredCountText.visibility = View.GONE
        }
    }

    /**
     * Mostra lo stato vuoto quando non ci sono timer
     */
    private fun showEmptyState() {
        loadingStateView.visibility = View.GONE
        emptyStateView.visibility = View.VISIBLE
        errorStateView.visibility = View.GONE
        timersRecyclerView.visibility = View.GONE
        if (::filteredCountText.isInitialized) {
            filteredCountText.visibility = View.GONE
        }
    }

    /**
     * Mostra lo stato di errore
     */
    private fun showErrorState(message: String) {
        loadingStateView.visibility = View.GONE
        emptyStateView.visibility = View.GONE
        errorStateView.visibility = View.VISIBLE
        timersRecyclerView.visibility = View.GONE
        if (::filteredCountText.isInitialized) {
            filteredCountText.visibility = View.GONE
        }

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
        if (::filteredCountText.isInitialized) {
            filteredCountText.visibility = View.VISIBLE
        }
    }

    /**
     * Aggiorna la lista filtrata in base al filtro corrente
     */
    private fun updateFilteredList() {
        filteredTimerList.clear()

        // Applica il filtro corrente
        when (currentFilter) {
            TimerFilterOption.ALL -> {
                filteredTimerList.addAll(allTimerList)
            }
            TimerFilterOption.ONLINE -> {
                filteredTimerList.addAll(allTimerList.filter { isTimerOnline(it) })
            }
            TimerFilterOption.OFFLINE -> {
                filteredTimerList.addAll(allTimerList.filter { !isTimerOnline(it) })
            }
        }

        // Aggiorna l'adapter
        timerAdapter.updateTimers(filteredTimerList)

        // Aggiorna il contatore dei timer filtrati se inizializzato
        if (::filteredCountText.isInitialized) {
            updateFilteredCount()
        }

        // Mostra la vista appropriata
        if (filteredTimerList.isEmpty() && allTimerList.isEmpty()) {
            showEmptyState()
        } else if (filteredTimerList.isEmpty()) {
            showEmptyState()
            // Rimuovi questo toast che appare ogni secondo
            // Toast.makeText(this, "Nessun timer corrisponde al filtro selezionato", Toast.LENGTH_SHORT).show()
        } else {
            showTimersList()
        }
    }
    /**
     * Aggiorna il contatore dei timer filtrati
     */
    private fun updateFilteredCount() {
        val filterMessage = when (currentFilter) {
            TimerFilterOption.ALL -> "Visualizzazione di tutti i timer"
            TimerFilterOption.ONLINE -> "Visualizzazione dei timer online"
            TimerFilterOption.OFFLINE -> "Visualizzazione dei timer offline"
        }

        filteredCountText.text = "$filterMessage (${filteredTimerList.size})"
    }

    /**
     * Determina se un timer è online in base al timestamp dell'ultimo aggiornamento
     */
    private fun isTimerOnline(timer: TimerItem): Boolean {
        try {
            // Estrai la data dell'ultimo aggiornamento
            val sdf = java.text.SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSS'Z'", java.util.Locale.getDefault())
            sdf.timeZone = java.util.TimeZone.getTimeZone("UTC")
            val lastUpdateTime = sdf.parse(timer.lastUpdateTimestamp)
            val now = java.util.Date()

            // Calcola la differenza in minuti
            val diffInMs = now.time - (lastUpdateTime?.time ?: 0)
            val diffInMinutes = diffInMs / (1000 * 60)

            // Un timer è considerato online se l'ultimo aggiornamento è avvenuto
            // negli ultimi ONLINE_TIMEOUT_MINUTES minuti
            return diffInMinutes < ONLINE_TIMEOUT_MINUTES
        } catch (e: Exception) {
            // In caso di errore nel parsing della data, considera il timer offline
            return false
        }
    }

    /**
     * Mostra il dialogo per modificare le impostazioni di un timer specifico
     */
    /**
     * Mostra il dialogo per modificare le impostazioni di un timer specifico
     */
    private fun showTimerSettingsDialog(timer: TimerItem) {
        // Crea un dialogo personalizzato con il layout delle impostazioni
        val dialogView = layoutInflater.inflate(R.layout.dialog_timer_settings, null)
        val dialog = Dialog(this)
        dialog.requestWindowFeature(Window.FEATURE_NO_TITLE)
        dialog.setContentView(dialogView)
        dialog.window?.setBackgroundDrawable(ColorDrawable(Color.TRANSPARENT))

        // Assicura che il dialogo occupi la maggior parte della larghezza dello schermo
        val layoutParams = WindowManager.LayoutParams()
        layoutParams.copyFrom(dialog.window?.attributes)
        layoutParams.width = WindowManager.LayoutParams.MATCH_PARENT
        layoutParams.height = WindowManager.LayoutParams.WRAP_CONTENT
        dialog.window?.attributes = layoutParams

        // Imposta il titolo con il numero del tavolo
        val titleText = dialogView.findViewById<TextView>(R.id.dialogTitleText)
        titleText.text = "Impostazioni Timer - Tavolo ${timer.tableNumber}"

        // Imposta l'icona del tipo di dispositivo
        val deviceTypeIcon = dialogView.findViewById<ImageView>(R.id.deviceTypeIconInDialog)
        val modeContainer = dialogView.findViewById<LinearLayout>(R.id.modeContainer)
        val modeSpinner = dialogView.findViewById<Spinner>(R.id.modeSpinner)

        // Configura le opzioni per lo spinner della modalità
        val modeOptions = arrayOf(
            "Mode 1: T1/T2 con avvio automatico",
            "Mode 2: T1/T2 con avvio manuale",
            "Mode 3: Solo T1 con avvio automatico",
            "Mode 4: Solo T1 con avvio manuale"
        )
        val modeAdapter = ArrayAdapter(this, android.R.layout.simple_spinner_item, modeOptions)
        modeAdapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item)
        modeSpinner.adapter = modeAdapter

        // Verifica il tipo di dispositivo
        val isAndroid = timer.deviceId.startsWith("android_")
        val isHardware = timer.deviceId.startsWith("arduino_")

        if (isAndroid) {
            // Configurazione per dispositivi Android
            deviceTypeIcon.setImageResource(R.drawable.ic_android)
            deviceTypeIcon.contentDescription = "Timer Android"
            // Nascondi la sezione modalità per dispositivi Android
            modeContainer.visibility = View.GONE
        } else if (isHardware) {
            // Configurazione per dispositivi Arduino/Hardware
            deviceTypeIcon.setImageResource(R.drawable.ic_hardware)
            deviceTypeIcon.contentDescription = "Timer Arduino"
            // Mostra la sezione modalità per dispositivi hardware
            modeContainer.visibility = View.VISIBLE
            // Seleziona la modalità corrente
            modeSpinner.setSelection(timer.operationMode - 1) // -1 perché le modalità iniziano da 1
        } else {
            // Per dispositivi sconosciuti, usiamo l'icona hardware
            deviceTypeIcon.setImageResource(R.drawable.ic_hardware)
            deviceTypeIcon.contentDescription = "Timer sconosciuto"
            // Mostra la sezione modalità anche per dispositivi sconosciuti
            modeContainer.visibility = View.VISIBLE
            // Seleziona la modalità corrente
            modeSpinner.setSelection(timer.operationMode - 1)
        }

        val t1ValueText = dialogView.findViewById<TextView>(R.id.t1ValueText)
        val t2ValueText = dialogView.findViewById<TextView>(R.id.t2ValueText)
        val t2Container = dialogView.findViewById<LinearLayout>(R.id.t2Container)

        val tableNumberText = dialogView.findViewById<TextView>(R.id.tableNumberText)
        val decreaseTableButton = dialogView.findViewById<Button>(R.id.decreaseTableButton)
        val increaseTableButton = dialogView.findViewById<Button>(R.id.increaseTableButton)

        // Controlli per il numero giocatori
        val playersNumberText = dialogView.findViewById<TextView>(R.id.playersNumberText)
        val decreasePlayersButton = dialogView.findViewById<Button>(R.id.decreasePlayersButton)
        val increasePlayersButton = dialogView.findViewById<Button>(R.id.increasePlayersButton)

        val buzzerSwitch = dialogView.findViewById<Switch>(R.id.buzzerSwitch)

        val decreaseT1Button = dialogView.findViewById<Button>(R.id.decreaseT1Button)
        val increaseT1Button = dialogView.findViewById<Button>(R.id.increaseT1Button)
        val decreaseT2Button = dialogView.findViewById<Button>(R.id.decreaseT2Button)
        val increaseT2Button = dialogView.findViewById<Button>(R.id.increaseT2Button)

        val cancelButton = dialogView.findViewById<Button>(R.id.cancelButton)
        val saveButton = dialogView.findViewById<Button>(R.id.saveSettingsButton)
        val resetDefaultsButton = dialogView.findViewById<Button>(R.id.resetDefaultsButton)

        // Valori correnti delle impostazioni
        var currentMode = timer.operationMode
        var currentT1 = timer.timerT1
        var currentT2 = timer.timerT2
        var currentBuzzer = timer.buzzerEnabled
        var currentTableNumber = timer.tableNumber
        // Ottieni il numero di giocatori o usa un valore predefinito se non disponibile
        var currentPlayersCount = timer.playersCount ?: 10

        // Imposta i valori iniziali nei controlli
        t1ValueText.text = currentT1.toString()
        t2ValueText.text = currentT2.toString()
        tableNumberText.text = currentTableNumber.toString()
        playersNumberText.text = currentPlayersCount.toString()
        buzzerSwitch.isChecked = currentBuzzer

        // Funzione per aggiornare la visibilità di T2 in base alla modalità
        fun updateT2Visibility() {
            // Nascondi T2 solo se la modalità è 3 o 4 (T1 only)
            if (currentMode == 3 || currentMode == 4) {
                t2Container.visibility = View.GONE
            } else {
                t2Container.visibility = View.VISIBLE
            }
        }

        // Aggiorna la visibilità iniziale di T2
        updateT2Visibility()

        // Listener per lo spinner della modalità
        modeSpinner.onItemSelectedListener = object : AdapterView.OnItemSelectedListener {
            override fun onItemSelected(parent: AdapterView<*>?, view: View?, position: Int, id: Long) {
                // La modalità è la posizione + 1
                currentMode = position + 1
                updateT2Visibility()
            }

            override fun onNothingSelected(parent: AdapterView<*>?) {
                // Non fare nulla
            }
        }

        // Listener per i pulsanti T1
        decreaseT1Button.setOnClickListener {
            if (currentT1 > 5) {
                currentT1 -= 5
                t1ValueText.text = currentT1.toString()
            }
        }

        increaseT1Button.setOnClickListener {
            if (currentT1 < 95) {
                currentT1 += 5
                t1ValueText.text = currentT1.toString()
            }
        }

        // Listener per i pulsanti T2
        decreaseT2Button.setOnClickListener {
            if (currentT2 > 5) {
                currentT2 -= 5
                t2ValueText.text = currentT2.toString()
            }
        }

        increaseT2Button.setOnClickListener {
            if (currentT2 < 95) {
                currentT2 += 5
                t2ValueText.text = currentT2.toString()
            }
        }

        // Listener per i pulsanti del numero tavolo
        decreaseTableButton.setOnClickListener {
            if (currentTableNumber > 0) {
                currentTableNumber--
                tableNumberText.text = currentTableNumber.toString()
            }
        }

        increaseTableButton.setOnClickListener {
            if (currentTableNumber < 99) {
                currentTableNumber++
                tableNumberText.text = currentTableNumber.toString()
            }
        }

        // Listener per i pulsanti del numero giocatori
        decreasePlayersButton.setOnClickListener {
            if (currentPlayersCount > 1) {
                currentPlayersCount--
                playersNumberText.text = currentPlayersCount.toString()
            }
        }

        increasePlayersButton.setOnClickListener {
            if (currentPlayersCount < 10) {
                currentPlayersCount++
                playersNumberText.text = currentPlayersCount.toString()
            }
        }

        // Listener per il buzzer
        buzzerSwitch.setOnCheckedChangeListener { _, isChecked ->
            currentBuzzer = isChecked
        }

        // Listener per il pulsante Annulla
        cancelButton.setOnClickListener {
            dialog.dismiss()
        }

        // Listener per il pulsante di factory reset
        resetDefaultsButton.setOnClickListener {
            // Verifica se è un timer hardware (Arduino) prima di tutto
            if (timer.deviceId.startsWith("arduino_")) {
                // Conferma con un dialog specifico per i dispositivi Arduino
                val arduinoDialog = AlertDialog.Builder(this)
                    .setTitle("Factory Reset (Arduino)")
                    .setMessage("Sei sicuro di voler eseguire un factory reset completo su questo dispositivo hardware?\n\nQuesto resetterà completamente il timer, cancellando:\n- Tutte le impostazioni timer\n- Configurazioni WiFi\n- Dati salvati\n\nIl dispositivo si riavvierà e potrebbe disconnettersi dalla rete.")
                    .setPositiveButton("Factory Reset") { _, _ ->
                        // Per i timer Arduino, invia il comando factory_reset specifico
                        sendCommandToTimer(timer.deviceId, "factory_reset")

                        // Chiudi il dialogo
                        dialog.dismiss()

                        // Mostra un messaggio di conferma con avviso
                        Toast.makeText(this, "Factory Reset avviato sul dispositivo Arduino. Il timer si riavvierà.", Toast.LENGTH_LONG).show()
                    }
                    .setNegativeButton("Annulla", null)
                    .create()

                // Mostra il dialogo Arduino
                arduinoDialog.show()

                // Imposta il colore dei pulsanti a bianco
                arduinoDialog.getButton(AlertDialog.BUTTON_POSITIVE).setTextColor(Color.WHITE)
                arduinoDialog.getButton(AlertDialog.BUTTON_NEGATIVE).setTextColor(Color.WHITE)
            } else {
                // Per i timer Android, mostra il dialogo standard con reset parziale
                val androidDialog = AlertDialog.Builder(this)
                    .setTitle("Reset Impostazioni")
                    .setMessage("Sei sicuro di voler ripristinare le impostazioni ai valori predefiniti?\n\nQuesto resetterà il timer a:\n- T1 = 20s\n- T2 = 30s\n- Buzzer ON\n- Tavolo 0\n- Giocatori = 10")
                    .setPositiveButton("Reset") { _, _ ->
                        // Valori predefiniti per il reset parziale
                        val defaultMode = 1
                        val defaultT1 = 20
                        val defaultT2 = 30
                        val defaultBuzzer = true
                        val defaultTableNumber = 0
                        val defaultPlayersCount = 10

                        // Ferma l'aggiornamento automatico temporaneamente
                        stopAutoRefresh()

                        // Applica le impostazioni di factory reset
                        applyTimerSettings(
                            timer.deviceId,
                            defaultMode,
                            defaultT1,
                            defaultT2,
                            defaultBuzzer,
                            defaultTableNumber,
                            defaultPlayersCount,
                            forceFactoryReset = true
                        )

                        // Aggiorna manualmente la lista locale immediatamente
                        val updatedTimer = allTimerList.find { it.deviceId == timer.deviceId }
                        updatedTimer?.let {
                            val index = allTimerList.indexOf(it)
                            if (index >= 0) {
                                allTimerList[index] = it.copy(
                                    operationMode = defaultMode,
                                    timerT1 = defaultT1,
                                    timerT2 = defaultT2,
                                    buzzerEnabled = defaultBuzzer,
                                    tableNumber = defaultTableNumber,
                                    playersCount = defaultPlayersCount
                                )
                            }
                        }

                        // Aggiorna la lista filtrata
                        updateFilteredList()

                        // Riavvia l'aggiornamento automatico dopo un breve ritardo
                        Handler(Looper.getMainLooper()).postDelayed({
                            startAutoRefresh()
                        }, 3000)

                        // Chiudi il dialogo
                        dialog.dismiss()

                        // Mostra un messaggio di conferma
                        Toast.makeText(this, "Reset impostazioni completato con successo", Toast.LENGTH_SHORT).show()
                    }
                    .setNegativeButton("Annulla", null)
                    .create()

                // Mostra il dialogo Android
                androidDialog.show()

                // Imposta il colore dei pulsanti a bianco
                androidDialog.getButton(AlertDialog.BUTTON_POSITIVE).setTextColor(Color.WHITE)
                androidDialog.getButton(AlertDialog.BUTTON_NEGATIVE).setTextColor(Color.WHITE)
            }
        }

        // Listener per il pulsante di salvataggio
        saveButton.setOnClickListener {
            // Salva e applica le impostazioni
            applyTimerSettings(
                timer.deviceId,
                currentMode,
                currentT1,
                currentT2,
                currentBuzzer,
                currentTableNumber,
                currentPlayersCount
            )

            // Chiudi il dialogo
            dialog.dismiss()
        }

        // Mostra il dialogo
        dialog.show()
    }

    /**
     * Aggiorna la visibilità del container T2 in base alla modalità
     */
    private fun updateT2Visibility(mode: Int, t2Container: View) {
        // Nelle modalità 3 e 4 si usa solo T1
        t2Container.visibility = if (mode == 3 || mode == 4) View.GONE else View.VISIBLE
    }

    /**
     * Applica le impostazioni al timer e invia al server
     */
    private fun applyTimerSettings(
        deviceId: String,
        mode: Int,
        t1: Int,
        t2: Int,
        buzzerEnabled: Boolean,
        tableNumber: Int? = null,
        playersCount: Int = 10,  // Assicurati che questo parametro sia presente
        forceFactoryReset: Boolean = false
    ) {
        // URL per le impostazioni
        val settingsUrl = "$serverUrl/api/settings/$deviceId"

        // Determina il numero del tavolo da utilizzare
        val finalTableNumber = tableNumber ?: allTimerList.find { it.deviceId == deviceId }?.tableNumber ?: 0

        // Prepara i dati da inviare
        val settings = JSONObject().apply {
            put("mode", mode)
            put("t1", t1)
            put("t2", t2)
            put("tableNumber", finalTableNumber)
            put("buzzer", if (buzzerEnabled) 1 else 0)
            put("playersCount", playersCount)  // Aggiungi questo
        }

        // Log per debugging
        Log.d("TimerSettings", "Applying settings: $settings to device: $deviceId")

        // Utilizza coroutine per l'operazione di rete
        CoroutineScope(Dispatchers.Main).launch {
            try {
                val result = withContext(Dispatchers.IO) {
                    sendTimerSettings(settingsUrl, settings)
                }

                if (result.startsWith("ERROR:")) {
                    Toast.makeText(this@DashboardActivity, result.substring(6), Toast.LENGTH_SHORT).show()
                } else {
                    // Mostra il messaggio appropriato in base al tipo di operazione
                    Toast.makeText(
                        this@DashboardActivity,
                        if (forceFactoryReset) "Factory Reset completato" else "Impostazioni salvate con successo",
                        Toast.LENGTH_SHORT
                    ).show()

                    val updatedTimer = allTimerList.find { it.deviceId == deviceId }
                    updatedTimer?.let {
                        val index = allTimerList.indexOf(it)
                        if (index >= 0) {
                            val newTimer = it.copy(
                                operationMode = mode,
                                timerT1 = t1,
                                timerT2 = t2,
                                buzzerEnabled = buzzerEnabled,
                                tableNumber = finalTableNumber,
                                playersCount = playersCount
                            )
                            android.util.Log.d("DashboardActivity", "Updating timer locally: playersCount=${newTimer.playersCount}")
                            allTimerList[index] = newTimer
                        }
                    }

                    // Aggiorna la lista filtrata
                    updateFilteredList()

                    // Aggiorna i dati, ma solo se non è un factory reset (per evitare che venga sovrascritto)
                    if (!forceFactoryReset) {
                        refreshTimerData(false)
                    }
                }
            } catch (e: Exception) {
                Log.e("TimerSettings", "Errore: ${e.message}", e)
                Toast.makeText(this@DashboardActivity, "Errore: ${e.message}", Toast.LENGTH_SHORT).show()
            }
        }
    }

    override fun onOptionsItemSelected(item: MenuItem): Boolean {
        return when (item.itemId) {
            android.R.id.home -> {
                onBackPressed()
                true
            }
            R.id.action_filter -> {
                // Gestione del filtro
                val dialog = AlertDialog.Builder(this)
                    .setTitle("Filtra Timer")
                    .setSingleChoiceItems(
                        TimerFilterOption.getTitles(),
                        currentFilter.ordinal
                    ) { dialogInterface, which ->
                        // Applica il filtro selezionato
                        currentFilter = TimerFilterOption.values()[which]
                        updateFilteredList()
                        dialogInterface.dismiss()
                    }
                    .setNegativeButton("Annulla") { dialog, _ -> dialog.dismiss() }
                    .create()

                dialog.show()
                true
            }
            R.id.action_refresh -> {
                refreshTimerData(true)
                true
            }
            R.id.action_clear_timers -> {
                // Mostra un dialog di conferma prima di cancellare tutti i timer
                val dialog = AlertDialog.Builder(this)
                    .setTitle("Cancella tutti i timer")
                    .setMessage("Sei sicuro di voler cancellare tutti i timer dalla dashboard? Questa operazione non può essere annullata.")
                    .setPositiveButton("Cancella") { _, _ ->
                        clearAllTimers()
                    }
                    .setNegativeButton("Annulla", null)
                    .create()

                dialog.show()

                // Imposta i colori dei pulsanti a bianco
                dialog.getButton(AlertDialog.BUTTON_POSITIVE).setTextColor(Color.WHITE)
                dialog.getButton(AlertDialog.BUTTON_NEGATIVE).setTextColor(Color.WHITE)
                true
            }
            else -> super.onOptionsItemSelected(item)
        }
    }

    /**
     * Cancella tutti i timer dalla lista locale
     */
    private fun clearAllTimers() {
        allTimerList.clear()
        filteredTimerList.clear()
        timerAdapter.updateTimers(filteredTimerList)
        showEmptyState()
        Toast.makeText(this, "Tutti i timer sono stati rimossi dalla dashboard", Toast.LENGTH_SHORT).show()

        // Interrompi temporaneamente l'aggiornamento automatico per evitare che i timer riappaiano subito
        stopAutoRefresh()

        // Riavvia l'aggiornamento automatico dopo 5 secondi
        Handler(Looper.getMainLooper()).postDelayed({
            startAutoRefresh()
        }, 5000)
    }

    /**
     * Invia le impostazioni al server
     */
    private suspend fun sendTimerSettings(url: String, settings: JSONObject): String {
        return withContext(Dispatchers.IO) {
            try {
                val connection = URL(url).openConnection() as HttpURLConnection
                connection.requestMethod = "POST"
                connection.doOutput = true
                connection.setRequestProperty("Content-Type", "application/json; charset=UTF-8")

                // Invia il JSON
                val outputStream = connection.outputStream
                outputStream.write(settings.toString().toByteArray())
                outputStream.close()

                val responseCode = connection.responseCode
                if (responseCode == HttpURLConnection.HTTP_OK) {
                    "Impostazioni salvate con successo"
                } else {
                    "ERROR:Errore del server: $responseCode"
                }
            } catch (e: Exception) {
                e.printStackTrace()
                "ERROR:${e.message}"
            }
        }
    }

    // Implementazione dei metodi dell'interfaccia TimerActionListener

    override fun onStartClicked(timer: TimerItem) {
        sendCommandToTimer(timer.deviceId, "start")
    }

    override fun onPauseClicked(timer: TimerItem) {
        sendCommandToTimer(timer.deviceId, "pause")
    }

    override fun onResetClicked(timer: TimerItem) {
        sendCommandToTimer(timer.deviceId, "reset")
    }

    override fun onSettingsClicked(timer: TimerItem) {
        showTimerSettingsDialog(timer)
    }

    /**
     * Metodo per gestire il reset dei posti liberi da una card del timer
     */
    override fun onSeatInfoResetRequested(timer: TimerItem) {
        resetSeatOpenInfo(timer)
    }

    /**
     * Invia la richiesta di reset dei posti liberi al server
     */
    private fun resetSeatOpenInfo(timer: TimerItem) {
        // Mostra un toast per indicare che la richiesta è in corso
        Toast.makeText(this, "Resetting posti liberi per tavolo ${timer.tableNumber}...", Toast.LENGTH_SHORT).show()

        // Utilizza una coroutine per la chiamata di rete
        CoroutineScope(Dispatchers.Main).launch {
            try {
                // Utilizza il NetworkManager per inviare la richiesta di reset
                val networkManager = NetworkManager(applicationContext)
                val success = networkManager.resetSeatInfo(serverUrl ?: "", timer.tableNumber)

                if (success) {
                    Toast.makeText(this@DashboardActivity, "Posti liberati con successo", Toast.LENGTH_SHORT).show()

                    // IMPORTANTE: Aggiorna immediatamente la lista locale prima del refresh dal server
                    // Trova il timer nella lista principale e aggiornalo
                    val index = allTimerList.indexOfFirst { it.deviceId == timer.deviceId }
                    if (index >= 0) {
                        // Crea una copia del timer con seatOpenInfo rimosso
                        val updatedTimer = allTimerList[index].copy(
                            seatOpenInfo = null,
                            pendingCommand = null  // Rimuovi anche eventuali pendingCommand relativi ai posti
                        )
                        allTimerList[index] = updatedTimer

                        // Dopo il reset, invia un comando clear_seats al client - SPOSTA QUESTO CODICE
                        // in un withContext(Dispatchers.IO) o usa networkManager.sendCommand
                        withContext(Dispatchers.IO) {
                            try {
                                val deviceId = allTimerList[index].deviceId
                                val commandUrl = URL("$serverUrl/api/command/$deviceId")

                                val commandConnection = commandUrl.openConnection() as HttpURLConnection
                                commandConnection.requestMethod = "POST"
                                commandConnection.doOutput = true
                                commandConnection.setRequestProperty("Content-Type", "application/json; charset=UTF-8")

                                val jsonPayload = """{"command": "clear_seats"}"""

                                val outputStream = commandConnection.outputStream
                                outputStream.write(jsonPayload.toByteArray())
                                outputStream.close()

                                val cmdResponseCode = commandConnection.responseCode
                                android.util.Log.d("DashboardActivity", "Clear seats response code: $cmdResponseCode")

                                commandConnection.disconnect()
                            } catch (e: Exception) {
                                android.util.Log.e("DashboardActivity", "Error sending clear_seats command: ${e.message}", e)
                            }
                        }
                    }

                    // Il resto del codice...
                } else {
                    Toast.makeText(this@DashboardActivity, "Errore nel reset dei posti liberi", Toast.LENGTH_SHORT).show()
                }
            } catch (e: Exception) {
                Log.e("DashboardActivity", "Errore nel reset dei posti: ${e.message}", e)
                Toast.makeText(this@DashboardActivity, "Errore: ${e.message}", Toast.LENGTH_SHORT).show()
            }
        }
    }
}