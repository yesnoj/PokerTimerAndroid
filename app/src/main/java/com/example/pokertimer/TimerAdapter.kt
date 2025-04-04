package com.example.pokertimer

import android.content.Context
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.core.content.ContextCompat
import androidx.recyclerview.widget.RecyclerView
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import java.util.TimeZone
import kotlin.math.abs
import androidx.appcompat.app.AlertDialog
import android.graphics.Rect
import android.view.MotionEvent

class TimerAdapter(
    private val context: Context,
    private var timers: List<TimerItem>,
    private val listener: TimerActionListener
) : RecyclerView.Adapter<TimerAdapter.TimerViewHolder>() {

    interface TimerActionListener {
        fun onStartClicked(timer: TimerItem)
        fun onPauseClicked(timer: TimerItem)
        fun onSettingsClicked(timer: TimerItem)
        // Manteniamo onResetClicked nell'interfaccia ma non lo useremo nel layout
        fun onResetClicked(timer: TimerItem)
        fun onResetSeatInfo(timer: TimerItem)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): TimerViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_timer, parent, false)
        return TimerViewHolder(view)
    }


    override fun onBindViewHolder(holder: TimerViewHolder, position: Int) {
        val timer = timers[position]
        holder.bind(timer, context, listener)
    }


    override fun getItemCount(): Int = timers.size

    fun updateTimers(newTimers: List<TimerItem>) {
        this.timers = newTimers
        notifyDataSetChanged()
    }

    class TimerViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        private val tableNumberText: TextView = itemView.findViewById(R.id.tableNumberText)
        private val timerStatusText: TextView = itemView.findViewById(R.id.timerStatusText)
        private val timerValueText: TextView = itemView.findViewById(R.id.timerValueText)
        private val activeTimerText: TextView = itemView.findViewById(R.id.activeTimerText)
        private val modeInfoText: TextView = itemView.findViewById(R.id.modeInfoText)
        private val t1InfoText: TextView = itemView.findViewById(R.id.t1InfoText)
        private val t2InfoText: TextView = itemView.findViewById(R.id.t2InfoText)
        private val buzzerInfoText: TextView = itemView.findViewById(R.id.buzzerInfoText)
        private val batteryInfoText: TextView = itemView.findViewById(R.id.batteryInfoText)
        private val voltageInfoText: TextView = itemView.findViewById(R.id.voltageInfoText)
        private val wifiInfoText: TextView = itemView.findViewById(R.id.wifiInfoText)
        private val lastUpdateInfoText: TextView = itemView.findViewById(R.id.lastUpdateInfoText)
        private val startButton: Button = itemView.findViewById(R.id.startButton)
        private val pauseButton: Button = itemView.findViewById(R.id.pauseButton)
        private val settingsButton: Button = itemView.findViewById(R.id.settingsButton)
        // Il resetButton non viene più usato, ma lo manteniamo nella dichiarazione
        private val resetButton: Button = itemView.findViewById(R.id.resetButton)
        private val seatInfoText: TextView = itemView.findViewById(R.id.seatInfoText)

        init {
            // Debug per tutti i click
            itemView.findViewById<Button>(R.id.startButton).setOnClickListener {
                Toast.makeText(itemView.context, "Start button clicked", Toast.LENGTH_SHORT).show()
            }

            itemView.findViewById<Button>(R.id.pauseButton).setOnClickListener {
                Toast.makeText(itemView.context, "Pause button clicked", Toast.LENGTH_SHORT).show()
            }

            itemView.findViewById<Button>(R.id.settingsButton).setOnClickListener {
                Toast.makeText(itemView.context, "Settings button clicked", Toast.LENGTH_SHORT).show()
            }
        }

        fun bind(timer: TimerItem, context: Context, listener: TimerActionListener) {
            // Informazioni di base
            tableNumberText.text = "Tavolo ${timer.tableNumber}"
            timerValueText.text = formatTimerValue(timer.currentTimer)

            // Timer attivo
            activeTimerText.text = if (timer.operationMode == 3 || timer.operationMode == 4) {
                "T1" // Modalità solo T1
            } else {
                if (timer.currentTimer == timer.timerT1) "T1" else "T2"
            }

            // Stato timer
            val statusText = when {
                timer.isExpired -> "Scaduto"
                timer.isPaused -> "In pausa"
                timer.isRunning -> "In esecuzione"
                else -> "Fermo"
            }
            timerStatusText.text = statusText

            // Colore stato
            val statusBgColor = when {
                timer.isExpired -> ContextCompat.getColor(context, R.color.colorExpired)
                timer.isPaused -> ContextCompat.getColor(context, R.color.colorPaused)
                timer.isRunning -> ContextCompat.getColor(context, R.color.colorRunning)
                else -> ContextCompat.getColor(context, R.color.colorStopped)
            }
            timerStatusText.background.setTint(statusBgColor)

            // Dettagli timer
            modeInfoText.text = "Modo: ${timer.operationMode}"
            t1InfoText.text = "T1: ${timer.timerT1}s"
            t2InfoText.text = "T2: ${timer.timerT2}s"
            buzzerInfoText.text = "Buzzer: ${if (timer.buzzerEnabled) "On" else "Off"}"

            // Info stato
            batteryInfoText.text = "${timer.batteryLevel}%"
            // Colore batteria in base al livello
            val batteryColor = when {
                timer.batteryLevel > 60 -> ContextCompat.getColor(context, R.color.batteryHigh)
                timer.batteryLevel > 20 -> ContextCompat.getColor(context, R.color.batteryMedium)
                else -> ContextCompat.getColor(context, R.color.batteryLow)
            }
            batteryInfoText.setTextColor(batteryColor)

            voltageInfoText.text = "${timer.voltage}V"

            // WiFi signal può essere null per i dispositivi Android
            timer.wifiSignal?.let {
                wifiInfoText.text = "$it dBm"
                // Colore WiFi in base alla potenza
                val wifiColor = when {
                    abs(it) < 60 -> ContextCompat.getColor(context, R.color.batteryHigh)
                    abs(it) < 75 -> ContextCompat.getColor(context, R.color.batteryMedium)
                    else -> ContextCompat.getColor(context, R.color.batteryLow)
                }
                wifiInfoText.setTextColor(wifiColor)
            } ?: run {
                // Per i dispositivi Android mostriamo un valore fisso positivo
                wifiInfoText.text = "Ottimo"
                wifiInfoText.setTextColor(ContextCompat.getColor(context, R.color.batteryHigh))
            }

            // Aggiungi un touch listener per l'intero item
            itemView.setOnTouchListener { v, event ->
                when (event.action) {
                    MotionEvent.ACTION_UP -> {
                        // Calcola se il touch è avvenuto sopra seatInfoText
                        val rect = Rect()
                        seatInfoText.getGlobalVisibleRect(rect)
                        if (rect.contains(event.rawX.toInt(), event.rawY.toInt()) &&
                            timer.seatInfo != null &&
                            timer.seatInfo.openSeats.isNotEmpty()) {
                            Toast.makeText(context, "SEAT OPEN touched", Toast.LENGTH_SHORT).show()
                            AlertDialog.Builder(v.context)
                                .setTitle("Gestione posti liberi")
                                .setMessage("Vuoi cancellare questa notifica di posti liberi?")
                                .setNegativeButton("CANCEL", null)
                                .setPositiveButton("RESET") { _, _ ->
                                    listener.onResetSeatInfo(timer)
                                }
                                .show()
                            return@setOnTouchListener true
                        }
                    }
                }
                return@setOnTouchListener false
            }

            // Tempo trascorso dall'ultimo aggiornamento
            lastUpdateInfoText.text = formatLastUpdate(timer.lastUpdateTimestamp)

            // Bottoni di controllo - Nascondiamo resetButton
            resetButton.visibility = View.GONE

            startButton.setOnClickListener {
                Toast.makeText(context, "Start clicked", Toast.LENGTH_SHORT).show()
                listener.onStartClicked(timer)
            }

            pauseButton.setOnClickListener {
                Toast.makeText(context, "Pause clicked", Toast.LENGTH_SHORT).show()
                listener.onPauseClicked(timer)
            }

            settingsButton.setOnClickListener {
                Toast.makeText(context, "Settings clicked", Toast.LENGTH_SHORT).show()
                listener.onSettingsClicked(timer)
            }


            // Determina se il timer è online in base all'ultimo aggiornamento
            val isTimerOnline = try {
                val sdf = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSS'Z'", Locale.getDefault())
                sdf.timeZone = TimeZone.getTimeZone("UTC")
                val lastUpdateTime = sdf.parse(timer.lastUpdateTimestamp)
                val now = Date()

                // Calcola la differenza in minuti
                val diffInMs = now.time - (lastUpdateTime?.time ?: 0)
                val diffInMinutes = diffInMs / (1000 * 60)

                // Un timer è considerato online se l'ultimo aggiornamento è avvenuto
                // negli ultimi 5 minuti
                diffInMinutes < 5
            } catch (e: Exception) {
                // In caso di errore, considera il timer offline
                false
            }
            startButton.isEnabled = true
            pauseButton.isEnabled = true
            settingsButton.isEnabled = true
            startButton.alpha = 1.0f
            pauseButton.alpha = 1.0f
            settingsButton.alpha = 1.0f

            if (timer.isRunning && !timer.isPaused) {
                startButton.isEnabled = false // Disabilita Start solo se già in esecuzione
                startButton.alpha = 0.5f
            } else {
                pauseButton.isEnabled = false // Disabilita Pause se non in esecuzione
                pauseButton.alpha = 0.5f
            }

            // Gestione delle informazioni sui posti liberi
            if (timer.seatInfo != null && timer.seatInfo.openSeats.isNotEmpty()) {
                // Formatta i posti liberi in una stringa
                val formattedSeats = timer.seatInfo.openSeats.joinToString(", ")
                seatInfoText.text = "SEAT OPEN: $formattedSeats"
                seatInfoText.visibility = View.VISIBLE

                // Assicurati che sia cliccabile
                seatInfoText.isClickable = true
                seatInfoText.isFocusable = true

                seatInfoText.setOnClickListener { view ->
                    // Log con tag più visibile e messaggio semplice
                    Toast.makeText(context, "SEAT OPEN clicked", Toast.LENGTH_SHORT).show()

                    AlertDialog.Builder(view.context)
                        .setTitle("Gestione posti liberi")
                        .setMessage("Vuoi cancellare questa notifica di posti liberi?")
                        .setNegativeButton("CANCEL", null)
                        .setPositiveButton("RESET") { _, _ ->
                            listener.onResetSeatInfo(timer)
                        }
                        .show()
                }

                // Notifica potenzialmente da mostrare
                if (timer.seatInfo.needsNotification) {
                    (context as? DashboardActivity)?.checkAndShowNotification(timer)
                }
            } else {
                seatInfoText.visibility = View.GONE
                // Rimuovi il listener se non ci sono informazioni sui posti
                seatInfoText.setOnClickListener(null)
            }
        }

        private fun formatTimerValue(seconds: Int): String {
            return "${seconds}s"
        }

        private fun formatLastUpdate(timestamp: String): String {
            try {
                val sdf = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSS'Z'", Locale.getDefault())
                sdf.timeZone = TimeZone.getTimeZone("UTC")
                val time = sdf.parse(timestamp)
                val now = Date()
                val diffInMs = now.time - (time?.time ?: 0)
                val diffInSeconds = diffInMs / 1000

                return when {
                    diffInSeconds < 60 -> "${diffInSeconds}s fa"
                    diffInSeconds < 3600 -> "${diffInSeconds / 60}m fa"
                    diffInSeconds < 86400 -> "${diffInSeconds / 3600}h fa"
                    else -> "${diffInSeconds / 86400}g fa"
                }
            } catch (e: Exception) {
                return "N/A"
            }
        }
    }
}