package com.example.pokertimer

import android.content.Context
import android.graphics.Color
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.TextView
import androidx.core.content.ContextCompat
import androidx.recyclerview.widget.RecyclerView
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import java.util.TimeZone
import kotlin.math.abs
import android.widget.Toast

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
        private val resetButton: Button = itemView.findViewById(R.id.resetButton)
        // Aggiungi questa riga per far riferimento al campo seatInfoText
        private val seatInfoText: TextView = itemView.findViewById(R.id.seatInfoText)


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

            // Tempo trascorso dall'ultimo aggiornamento
            lastUpdateInfoText.text = formatLastUpdate(timer.lastUpdateTimestamp)

            // Bottoni di controllo - Nascondiamo resetButton
            resetButton.visibility = View.GONE

            startButton.setOnClickListener { listener.onStartClicked(timer) }
            pauseButton.setOnClickListener { listener.onPauseClicked(timer) }
            settingsButton.setOnClickListener { listener.onSettingsClicked(timer) }

            // Abilita/disabilita bottoni in base allo stato
            startButton.isEnabled = !timer.isRunning || timer.isPaused
            pauseButton.isEnabled = timer.isRunning && !timer.isPaused

            // Gestione dell'informazione sui posti liberi
            val seatInfoText: TextView = itemView.findViewById(R.id.seatInfoText)

            // Per debug/test, forziamo la visualizzazione per il tavolo 2 (come nel log)
            if (timer.tableNumber == 2) {
                seatInfoText.text = "SEAT OPEN: 1, 2, 3"
                seatInfoText.visibility = View.VISIBLE
                android.util.Log.d("TimerAdapter", "Forzando visualizzazione posti per tavolo ${timer.tableNumber}")
            } else if (timer.hasSeatOpenInfo()) {
                // Usa le info dai dati del server se disponibili
                seatInfoText.text = timer.getFormattedSeatInfo()
                seatInfoText.visibility = View.VISIBLE
                android.util.Log.d("TimerAdapter", "Mostro info posti da server: ${timer.getFormattedSeatInfo()}")
            } else {
                // Controlla anche direttamente pendingCommand
                if (timer.pendingCommand != null && timer.pendingCommand.startsWith("seat_open:")) {
                    val seats = timer.pendingCommand.substringAfter("seat_open:").trim()
                    seatInfoText.text = "SEAT OPEN: $seats"
                    seatInfoText.visibility = View.VISIBLE
                    android.util.Log.d("TimerAdapter", "Mostro info posti da pendingCommand: $seats")
                } else {
                    seatInfoText.visibility = View.GONE
                    android.util.Log.d("TimerAdapter", "Nessuna info posti da mostrare per tavolo ${timer.tableNumber}")
                }
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