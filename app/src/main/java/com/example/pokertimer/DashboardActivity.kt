package com.example.pokertimer

import android.content.Intent
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.util.Log
import android.view.Menu
import android.view.MenuItem
import android.view.View
import android.widget.Button
import android.widget.RadioButton
import android.widget.RadioGroup
import android.widget.Switch
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.appcompat.widget.Toolbar
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import androidx.swiperefreshlayout.widget.SwipeRefreshLayout
import com.google.android.material.chip.Chip
import com.google.android.material.chip.ChipGroup
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
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import java.util.TimeZone
import android.widget.LinearLayout


class DashboardActivity : AppCompatActivity(), TimerAdapter.TimerActionListener {

    // Costanti per il refresh automatico
    private val AUTO_REFRESH_INTERVAL_MS = 1000L // 1 secondo
    private var timerRefreshHandler: Handler? = null
    private var refreshRunnable: Runnable? = null

    private lateinit var timersRecyclerView: RecyclerView
    private lateinit var swipeRefreshLayout: SwipeRefreshLayout
    private lateinit var emptyStateView: View
    private lateinit var errorStateView: View
    private lateinit var loadingStateView: View
    private lateinit var refreshFab: FloatingActionButton
    private lateinit var refreshButton: Button
    private lateinit var errorRetryButton: Button
    private lateinit var errorMessageText: TextView
    private lateinit var filteredCountText: TextView

    private var serverUrl: String? = null
    private lateinit var timerAdapter: TimerAdapter
    private val allTimerList = mutableListOf<TimerItem>()
    private val filteredTimerList = mutableListOf<TimerItem>()
    private var currentFilter = TimerFilterOption.ALL

    // Costante per il timeout online (in minuti)
    private val ONLINE_TIMEOUT_MINUTES = 5

    private val acknowledgedDevices = HashSet<String>()

    private val shownNotifications = HashSet<String>()

    // Metodo pubblico da chiamare dall'adapter
    fun checkAndShowNotification(timer: TimerItem) {
        if (timer.seatInfo?.needsNotification == true) {
            // Usa solo l'ID del dispositivo
            if (!acknowledgedDevices.contains(timer.deviceId)) {
                // Segna questo dispositivo come notificato
                acknowledgedDevices.add(timer.deviceId)

                // Log per debug
                android.util.Log.d("DashboardActivity", "Showing notification for device: ${timer.deviceId}")

                val formattedSeats = timer.seatInfo.openSeats.joinToString(", ")

                runOnUiThread {
                    AlertDialog.Builder(this)
                        .setTitle("Richiesta Posti Liberi")
                        .setMessage("Tavolo ${timer.tableNumber} - SEAT OPEN\nPosti: $formattedSeats")
                        .setPositiveButton("OK") { dialog, _ ->
                            dialog.dismiss()
                            acknowledgeNotification(timer.deviceId)
                        }
                        .setCancelable(false)
                        .show()
                }
            } else {
                // Se il dispositivo è già stato notificato, invia comunque la conferma
                // per assicurarsi che il server abbia aggiornato lo stato
                acknowledgeNotification(timer.deviceId)
            }
        }
    }

    override fun onResume() {
        super.onResume()
        (application as PokerTimerApplication).setCurrentActivity(this)
    }

    override fun onPause() {
        super.onPause()
        if ((application as PokerTimerApplication).getCurrentActivity() == this) {
            (application as PokerTimerApplication).setCurrentActivity(null)
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_dashboard)

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
        refreshButton = findViewById(R.id.refreshButton)
        errorRetryButton = findViewById(R.id.errorRetryButton)
        errorMessageText = findViewById(R.id.errorMessageText)

        // Inizializza componenti per il filtro, se presenti nel layout
        try {
            filteredCountText = findViewById(R.id.filteredCountText)
        } catch (e: Exception) {
            Log.e("DashboardActivity", "Elemento filteredCountText non trovato nel layout", e)
        }

        // Configura la RecyclerView
        timerAdapter = TimerAdapter(this, filteredTimerList, this)
        timersRecyclerView.layoutManager = LinearLayoutManager(this)
        timersRecyclerView.adapter = timerAdapter

        // Mostra lo stato iniziale
        showEmptyState()

        // Configura il listener per il pull-to-refresh
        swipeRefreshLayout.setOnRefreshListener { refreshTimerData(true) }

        // Configura i pulsanti di refresh
        refreshButton.setOnClickListener { refreshTimerData(true) }
        errorRetryButton.setOnClickListener { refreshTimerData(true) }

        // Carica i dati all'inizio
        refreshTimerData(true)
    }

    override fun onDestroy() {
        super.onDestroy()
        // Assicurati di rimuovere il runnable quando l'activity viene distrutta
        stopAutoRefresh()
        timerRefreshHandler = null
        refreshRunnable = null
    }

    // Implementa il metodo dell'interfaccia TimerActionListener
    override fun onResetSeatInfo(timer: TimerItem) {
        // Verifica che l'aggiornamento locale funzioni correttamente
        val index = allTimerList.indexOf(timer)
        if (index >= 0) {
            // Crea una copia del timer senza le informazioni sui posti
            val updatedTimer = timer.copy(seatInfo = null)
            allTimerList[index] = updatedTimer

            // Aggiorna immediatamente la UI
            filteredTimerList.clear()
            updateFilteredList()
            timerAdapter.notifyDataSetChanged()

            // Log per debug
            android.util.Log.d("DashboardActivity", "Removed seat info locally for device: ${timer.deviceId}")

            // Invia la richiesta al server per resettare (verifica che l'URL sia corretto)
            CoroutineScope(Dispatchers.IO).launch {
                try {
                    val jsonPayload = """
                    {
                        "command": "reset_seat_info"
                    }
                """.trimIndent()

                    val connection = URL("$serverUrl/api/command/${timer.deviceId}")
                        .openConnection() as HttpURLConnection
                    connection.requestMethod = "POST"
                    connection.doOutput = true
                    connection.setRequestProperty("Content-Type", "application/json; charset=UTF-8")

                    // Invia i dati
                    val outputStream = connection.outputStream
                    outputStream.write(jsonPayload.toByteArray())
                    outputStream.close()

                    val responseCode = connection.responseCode
                    if (responseCode == HttpURLConnection.HTTP_OK) {
                        android.util.Log.d("DashboardActivity", "Reset seat info successful")

                        // Leggi la risposta per debug
                        val reader = BufferedReader(InputStreamReader(connection.inputStream))
                        val response = StringBuilder()
                        var line: String?
                        while (reader.readLine().also { line = it } != null) {
                            response.append(line)
                        }
                        android.util.Log.d("DashboardActivity", "Server response: $response")
                    } else {
                        android.util.Log.e("DashboardActivity", "Failed to reset seat info: $responseCode")
                    }

                    connection.disconnect()
                } catch (e: Exception) {
                    android.util.Log.e("DashboardActivity", "Error resetting seat info", e)
                }
            }
        }
    }

    /**
     * Invia una conferma al server che la notifica è stata vista
     */
    private fun acknowledgeNotification(deviceId: String) {
        CoroutineScope(Dispatchers.IO).launch {
            try {
                val connection = URL("$serverUrl/api/acknowledge_seat_notification/$deviceId")
                    .openConnection() as HttpURLConnection
                connection.requestMethod = "POST"
                connection.connectTimeout = 5000
                connection.readTimeout = 5000

                val responseCode = connection.responseCode
                if (responseCode == HttpURLConnection.HTTP_OK) {
                    android.util.Log.d("DashboardActivity", "Notification acknowledged successfully")
                } else {
                    android.util.Log.e("DashboardActivity", "Failed to acknowledge notification: $responseCode")
                }
            } catch (e: Exception) {
                android.util.Log.e("DashboardActivity", "Error acknowledging notification", e)
            }
        }
    }

    // Nel metodo che elabora i timer o nell'adapter, quando si verifica se mostrare una notifica:
    private fun showNotificationIfNeeded(timer: TimerItem) {
        if (timer.seatInfo != null && timer.seatInfo.needsNotification) {
            // Crea un ID univoco per questa notifica
            val notificationId = "${timer.deviceId}_${timer.lastUpdateTimestamp}"

            // Controlla se questa notifica è già stata mostrata
            if (!shownNotifications.contains(notificationId)) {
                // Segna questa notifica come mostrata
                shownNotifications.add(notificationId)

                // Mostra la notifica
                val formattedSeats = timer.seatInfo.openSeats.joinToString(", ")

                AlertDialog.Builder(this)
                    .setTitle("Richiesta Posti Liberi")
                    .setMessage("Tavolo ${timer.tableNumber} - SEAT OPEN\nPosti: $formattedSeats")
                    .setPositiveButton("OK") { dialog, _ ->
                        dialog.dismiss()

                        // Invia la conferma al server che la notifica è stata vista
                        acknowledgeNotification(timer.deviceId)
                    }
                    .setCancelable(false)
                    .show()
            }
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

                    // Aggiorna la lista principale dei timer
                    allTimerList.clear()
                    allTimerList.addAll(parsedTimers)

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
            Toast.makeText(this, "Nessun timer corrisponde al filtro selezionato", Toast.LENGTH_SHORT).show()
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
            val sdf = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSS'Z'", Locale.getDefault())
            sdf.timeZone = TimeZone.getTimeZone("UTC")
            val lastUpdateTime = sdf.parse(timer.lastUpdateTimestamp)
            val now = Date()

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
    private fun showTimerSettingsDialog(timer: TimerItem) {
        // Crea un dialogo personalizzato con il layout delle impostazioni
        val dialogView = layoutInflater.inflate(R.layout.dialog_timer_settings, null)
        val dialog = AlertDialog.Builder(this)
            .setView(dialogView)
            .setCancelable(true)
            .create()

        // Imposta il titolo con il numero del tavolo
        val titleText = dialogView.findViewById<TextView>(R.id.dialogTitleText)
        titleText.text = "Impostazioni Timer - Tavolo ${timer.tableNumber}"

        // Inizializza riferimenti alle viste
        val modeRadioGroup = dialogView.findViewById<RadioGroup>(R.id.modeRadioGroup)
        val mode1Radio = dialogView.findViewById<RadioButton>(R.id.modeRadio1)
        val mode2Radio = dialogView.findViewById<RadioButton>(R.id.modeRadio2)
        val mode3Radio = dialogView.findViewById<RadioButton>(R.id.modeRadio3)
        val mode4Radio = dialogView.findViewById<RadioButton>(R.id.modeRadio4)

        val t1ValueText = dialogView.findViewById<TextView>(R.id.t1ValueText)
        val t2ValueText = dialogView.findViewById<TextView>(R.id.t2ValueText)
        val t2Container = dialogView.findViewById<LinearLayout>(R.id.t2Container)

        val tableNumberText = dialogView.findViewById<TextView>(R.id.tableNumberText)
        val decreaseTableButton = dialogView.findViewById<Button>(R.id.decreaseTableButton)
        val increaseTableButton = dialogView.findViewById<Button>(R.id.increaseTableButton)

        val buzzerSwitch = dialogView.findViewById<Switch>(R.id.buzzerSwitch)

        val decreaseT1Button = dialogView.findViewById<Button>(R.id.decreaseT1Button)
        val increaseT1Button = dialogView.findViewById<Button>(R.id.increaseT1Button)
        val decreaseT2Button = dialogView.findViewById<Button>(R.id.decreaseT2Button)
        val increaseT2Button = dialogView.findViewById<Button>(R.id.increaseT2Button)

        val resetDefaultsButton = dialogView.findViewById<Button>(R.id.resetDefaultsButton)
        val saveSettingsButton = dialogView.findViewById<Button>(R.id.saveSettingsButton)

        // Valori correnti delle impostazioni
        var currentMode = timer.operationMode
        var currentT1 = timer.timerT1
        var currentT2 = timer.timerT2
        var currentBuzzer = timer.buzzerEnabled
        var currentTableNumber = timer.tableNumber

        // Imposta i valori iniziali
        when (currentMode) {
            1 -> mode1Radio.isChecked = true
            2 -> mode2Radio.isChecked = true
            3 -> mode3Radio.isChecked = true
            4 -> mode4Radio.isChecked = true
        }

        t1ValueText.text = currentT1.toString()
        t2ValueText.text = currentT2.toString()
        tableNumberText.text = currentTableNumber.toString()
        buzzerSwitch.isChecked = currentBuzzer

        // Mostra/nascondi T2 in base alla modalità
        updateT2Visibility(currentMode, t2Container)

        // Listener per il RadioGroup della modalità
        modeRadioGroup.setOnCheckedChangeListener { _, checkedId ->
            currentMode = when (checkedId) {
                R.id.modeRadio1 -> 1
                R.id.modeRadio2 -> 2
                R.id.modeRadio3 -> 3
                R.id.modeRadio4 -> 4
                else -> 1 // Default
            }

            // Aggiorna la visibilità di T2
            updateT2Visibility(currentMode, t2Container)
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

        // Listener per il buzzer
        buzzerSwitch.setOnCheckedChangeListener { _, isChecked ->
            currentBuzzer = isChecked
        }

        // Listener per il pulsante di factory reset
        resetDefaultsButton.setOnClickListener {
            // Conferma con un dialog
            AlertDialog.Builder(this)
                .setTitle("Factory Reset")
                .setMessage("Sei sicuro di voler ripristinare tutte le impostazioni ai valori predefiniti?\n\nQuesto resetterà il timer a:\n- Modalità 1\n- T1 = 20s\n- T2 = 30s\n- Buzzer ON\n- Tavolo 0")
                .setPositiveButton("Factory Reset") { _, _ ->
                    // Ripristina i valori predefiniti
                    val defaultMode = 1
                    val defaultT1 = 20
                    val defaultT2 = 30
                    val defaultBuzzer = true
                    val defaultTableNumber = 0

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
                        forceFactoryReset = true
                    )

                    // Aggiorna manualmente la lista locale immediatamente
                    // Modifica l'oggetto timer in allTimerList per riflettere il reset
                    val updatedTimer = allTimerList.find { it.deviceId == timer.deviceId }
                    updatedTimer?.let {
                        // Crea una copia aggiornata del timer
                        val index = allTimerList.indexOf(it)
                        if (index >= 0) {
                            allTimerList[index] = it.copy(
                                operationMode = defaultMode,
                                timerT1 = defaultT1,
                                timerT2 = defaultT2,
                                buzzerEnabled = defaultBuzzer,
                                tableNumber = defaultTableNumber
                            )
                        }
                    }

                    // Aggiorna la lista filtrata
                    updateFilteredList()

                    // Riavvia l'aggiornamento automatico dopo un breve ritardo
                    Handler(Looper.getMainLooper()).postDelayed({
                        startAutoRefresh()
                    }, 3000) // Ritardo di 3 secondi prima di riprendere l'aggiornamento automatico

                    // Chiudi il dialogo
                    dialog.dismiss()

                    // Mostra un messaggio di conferma
                    Toast.makeText(this, "Factory Reset completato con successo", Toast.LENGTH_SHORT).show()
                }
                .setNegativeButton("Annulla", null)
                .show()
        }

        // Listener per il pulsante di salvataggio
        saveSettingsButton.setOnClickListener {
            // Salva e applica le impostazioni
            applyTimerSettings(timer.deviceId, currentMode, currentT1, currentT2, currentBuzzer, currentTableNumber)

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
     * @param forceFactoryReset Se true, forza l'applicazione delle impostazioni e disabilita l'aggiornamento automatico
     */
    private fun applyTimerSettings(
        deviceId: String,
        mode: Int,
        t1: Int,
        t2: Int,
        buzzerEnabled: Boolean,
        tableNumber: Int? = null,
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

                    // Aggiorna i dati, ma solo se non è un factory reset (per evitare che venga sovrascritto)
                    if (!forceFactoryReset) {
                        refreshTimerData(false)
                    }
                }
            } catch (e: Exception) {
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
                val dialog = androidx.appcompat.app.AlertDialog.Builder(this)
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
            R.id.action_change_server -> {
                val intent = Intent(this, ServerUrlActivity::class.java)
                startActivity(intent)
                finish()
                true
            }
            R.id.action_clear_timers -> {
                // Mostra un dialog di conferma prima di cancellare tutti i timer
                AlertDialog.Builder(this)
                    .setTitle("Cancella tutti i timer")
                    .setMessage("Sei sicuro di voler cancellare tutti i timer dalla dashboard? Questa operazione non può essere annullata.")
                    .setPositiveButton("Cancella") { _, _ ->
                        clearAllTimers()
                    }
                    .setNegativeButton("Annulla", null)
                    .show()
                true
            }
            else -> super.onOptionsItemSelected(item)
        }
    }

    /**
     * Cancella tutti i timer dalla lista locale
     */
/**
 * Cancella tutti i timer dalla lista locale e dal server
 */
private fun clearAllTimers() {
    // Invia la richiesta di cancellazione al server
    CoroutineScope(Dispatchers.Main).launch {
        try {
            // Usa una coroutine per fare la richiesta HTTP
            val result = withContext(Dispatchers.IO) {
                // Prepara la richiesta DELETE
                val connection = URL("$serverUrl/api/timers").openConnection() as HttpURLConnection
                connection.requestMethod = "DELETE"
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
            }

            // Dopo aver cancellato dal server, aggiorna la UI
            if (result.startsWith("ERROR:")) {
                Toast.makeText(this@DashboardActivity, result.substring(6), Toast.LENGTH_SHORT).show()
            } else {
                // Pulisci le liste locali
                allTimerList.clear()
                filteredTimerList.clear()
                timerAdapter.updateTimers(filteredTimerList)
                showEmptyState()
                Toast.makeText(this@DashboardActivity, "Tutti i timer sono stati rimossi dal server", Toast.LENGTH_SHORT).show()
                
                // Interrompi temporaneamente l'aggiornamento automatico per evitare che i timer riappaiano subito
                stopAutoRefresh()

                // Riavvia l'aggiornamento automatico dopo 5 secondi
                Handler(Looper.getMainLooper()).postDelayed({
                    startAutoRefresh()
                }, 5000)
            }
        } catch (e: Exception) {
            Toast.makeText(this@DashboardActivity, "Errore durante la cancellazione dei timer: ${e.message}", Toast.LENGTH_SHORT).show()
            e.printStackTrace()
        }
    }
}

    

    /**
     * Invia le impostazioni al server
     */
    private suspend fun sendTimerSettings(url: String, settings: JSONObject): String {
        return try {
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
}