package com.example.pokertimer

import android.animation.ObjectAnimator
import android.content.Context
import android.graphics.Color
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.ImageView
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.core.content.ContextCompat
import androidx.recyclerview.widget.RecyclerView
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import java.util.TimeZone
import kotlin.math.abs

class TimerAdapter(
    private val context: Context,
    private var timers: List<TimerItem>,
    private val listener: TimerActionListener
) : RecyclerView.Adapter<TimerAdapter.TimerViewHolder>() {

    interface TimerActionListener {
        fun onStartClicked(timer: TimerItem)
        fun onPauseClicked(timer: TimerItem)
        fun onResetClicked(timer: TimerItem)
        fun onSettingsClicked(timer: TimerItem)
        // Nuovo metodo per gestire il reset dei posti liberi
        fun onSeatInfoResetRequested(timer: TimerItem)
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
        // Log per debug
        android.util.Log.d("TimerAdapter", "Updating timers list, size: ${newTimers.size}")

        // Verifica se ci sono timer con seatOpenInfo
        newTimers.forEach { timer ->
            if (timer.hasSeatOpenInfo()) {
                android.util.Log.d("TimerAdapter", "Timer ${timer.deviceId} (table ${timer.tableNumber}) has seat info: ${timer.getFormattedSeatInfo()}")
            }
        }

        // Aggiorna la lista
        this.timers = newTimers

        // Notifica che l'intero dataset è cambiato per forzare un refresh completo
        notifyDataSetChanged()
    }

    // Metodo per recuperare l'ID di un timer in base alla posizione
    override fun getItemId(position: Int): Long {
        return timers[position].deviceId.hashCode().toLong()
    }

    class TimerViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        private val tableNumberText: TextView = itemView.findViewById(R.id.tableNumberText)
        private val deviceTypeIcon: ImageView = itemView.findViewById(R.id.deviceTypeIcon)
        private val floormanAlertIcon: ImageView = itemView.findViewById(R.id.floormanAlertIcon)
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
        private val settingsButton: Button = itemView.findViewById(R.id.settingsButton)
        private val seatInfoText: TextView = itemView.findViewById(R.id.seatInfoText)

        // Manteniamo i riferimenti ai pulsanti nascosti per compatibilità
        private val startButton: Button = itemView.findViewById(R.id.startButton)
        private val pauseButton: Button = itemView.findViewById(R.id.pauseButton)
        private val resetButton: Button = itemView.findViewById(R.id.resetButton)

        // Flag per tenere traccia dello stato floorman
        private var hasActiveFloormanCall = false
        private var highlightAnimator: ObjectAnimator? = null
        private var iconAnimator: ObjectAnimator? = null

        /**
         * Verifica se un timer è un dispositivo Android basato sul device_id
         */
        private fun isAndroidTimer(deviceId: String): Boolean {
            return deviceId.startsWith("android_")
        }

        /**
         * Verifica se un timer è un dispositivo hardware (Arduino/ESP) basato sul device_id
         */
        private fun isHardwareTimer(deviceId: String): Boolean {
            return deviceId.startsWith("arduino_")
        }

        fun bind(timer: TimerItem, context: Context, listener: TimerActionListener) {
            // Informazioni di base
            tableNumberText.text = "Tavolo ${timer.tableNumber}"

            // Determina il tipo di dispositivo e mostra l'icona appropriata
            val isAndroid = isAndroidTimer(timer.deviceId)
            val isHardware = isHardwareTimer(timer.deviceId)

            if (isAndroid) {
                deviceTypeIcon.setImageResource(R.drawable.ic_android)
                deviceTypeIcon.contentDescription = "Timer Android"
                // Nascondi la modalità per i dispositivi Android
                modeInfoText.visibility = View.GONE
            } else if (isHardware) {
                deviceTypeIcon.setImageResource(R.drawable.ic_hardware)
                deviceTypeIcon.contentDescription = "Timer Arduino"
                // Mostra la modalità per i dispositivi hardware
                modeInfoText.visibility = View.VISIBLE
                modeInfoText.text = "Modo: ${timer.operationMode}"
            } else {
                // Per dispositivi sconosciuti, usiamo comunque l'icona hardware
                deviceTypeIcon.setImageResource(R.drawable.ic_hardware)
                deviceTypeIcon.contentDescription = "Timer sconosciuto"
                // E mostriamo la modalità
                modeInfoText.visibility = View.VISIBLE
                modeInfoText.text = "Modo: ${timer.operationMode}"
            }

            val floormanIcon = itemView.findViewById<ImageView?>(R.id.floormanAlertIcon)
            if (floormanIcon == null) {
                android.util.Log.e("TimerAdapter", "floormanAlertIcon non trovata nel layout!")
            }

            // Controlla se c'è una chiamata floorman attiva
            val hasFloormanCall = timer.pendingCommand == "floorman_call"
            android.util.Log.d("TimerAdapter", "Timer ${timer.deviceId} - pendingCommand: ${timer.pendingCommand}, hasFloormanCall: $hasFloormanCall")

            // Mostra/nascondi l'icona alert
            floormanIcon?.let {
                it.visibility = if (hasFloormanCall) {
                    android.util.Log.d("TimerAdapter", "Mostrando icona floorman per tavolo ${timer.tableNumber}")
                    View.VISIBLE
                } else {
                    View.GONE
                }
            } ?: run {
                // Se l'icona non esiste, usa solo l'animazione del testo
                if (hasFloormanCall) {
                    android.util.Log.w("TimerAdapter", "Icona floorman non disponibile, usando solo animazione testo")
                }
            }


            // Mostra/nascondi l'icona alert
            floormanAlertIcon.visibility = if (hasFloormanCall) View.VISIBLE else View.GONE

            // Se lo stato è cambiato, aggiorna l'highlight
            if (hasFloormanCall != hasActiveFloormanCall) {
                hasActiveFloormanCall = hasFloormanCall

                if (hasActiveFloormanCall) {
                    // Avvia l'animazione di highlight del testo
                    startFloormanHighlight()
                    // Fai lampeggiare anche l'icona
                    startIconAnimation()
                } else {
                    // Ferma l'animazione e rimuovi l'highlight
                    stopFloormanHighlight()
                }
            }

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

            // Configurazione del pulsante impostazioni
            settingsButton.setOnClickListener { listener.onSettingsClicked(timer) }

            // Gestione dell'informazione sui posti liberi
            if (timer.hasSeatOpenInfo()) {
                // Ottieni le informazioni sui posti
                val seatInfo = when {
                    timer.seatOpenInfo != null -> timer.seatOpenInfo
                    timer.pendingCommand?.startsWith("seat_open:") == true ->
                        timer.pendingCommand.substringAfter("seat_open:").trim()
                    else -> ""
                }

                if (seatInfo.isNotEmpty()) {
                    seatInfoText.text = "SEAT OPEN: $seatInfo"
                    seatInfoText.visibility = View.VISIBLE

                    // Rendi cliccabile per resettare i posti
                    seatInfoText.setOnClickListener {
                        showSeatResetConfirmation(context, timer, seatInfo, listener)
                    }
                } else {
                    seatInfoText.visibility = View.GONE
                }
            } else {
                seatInfoText.visibility = View.GONE
            }

            // Configurazione dei pulsanti nascosti ma necessari per compatibilità con il codice
            // Questi pulsanti sono invisibili nell'UI ma ancora funzionali nel codice
            startButton.setOnClickListener { listener.onStartClicked(timer) }
            pauseButton.setOnClickListener { listener.onPauseClicked(timer) }
        }

        private fun startFloormanHighlight() {
            // Crea un'animazione che fa lampeggiare il titolo del tavolo
            highlightAnimator = ObjectAnimator.ofArgb(
                tableNumberText,
                "textColor",
                Color.BLACK,
                Color.parseColor("#FF9800"),  // Arancione
                Color.BLACK
            ).apply {
                duration = 1000
                repeatCount = ObjectAnimator.INFINITE
                repeatMode = ObjectAnimator.REVERSE
                start()
            }

            // Aggiungi anche un background colorato alla card (assumendo che la root view sia una MaterialCardView)
            val cardView = itemView as? com.google.android.material.card.MaterialCardView
            cardView?.apply {
                strokeColor = Color.parseColor("#FF9800")
                strokeWidth = 8  // Aumentato per maggiore visibilità
            }
        }

        private fun startIconAnimation() {
            // Animazione di lampeggio per l'icona
            iconAnimator = ObjectAnimator.ofFloat(
                floormanAlertIcon,
                "alpha",
                1f,
                0.3f,
                1f
            ).apply {
                duration = 800
                repeatCount = ObjectAnimator.INFINITE
                start()
            }
        }

        private fun stopIconAnimation() {
            iconAnimator?.cancel()
            iconAnimator = null
            floormanAlertIcon.alpha = 1f
        }

        fun stopFloormanHighlight() {
            // Ferma l'animazione del testo
            highlightAnimator?.cancel()
            highlightAnimator = null

            // Ferma l'animazione dell'icona
            stopIconAnimation()

            // Nascondi l'icona
            floormanAlertIcon.visibility = View.GONE

            // Ripristina il colore originale del testo
            tableNumberText.setTextColor(ContextCompat.getColor(itemView.context, R.color.colorPrimaryDark))

            // Rimuovi il bordo colorato dalla card
            val cardView = itemView as? com.google.android.material.card.MaterialCardView
            cardView?.apply {
                strokeColor = Color.TRANSPARENT
                strokeWidth = 0
            }
        }

        private fun showSeatResetConfirmation(
            context: Context,
            timer: TimerItem,
            seatInfo: String,
            listener: TimerActionListener
        ) {
            val dialog = AlertDialog.Builder(context)
                .setTitle("Reset Posti Liberi")
                .setMessage("Vuoi rimuovere l'indicazione di posti liberi ($seatInfo) per il tavolo ${timer.tableNumber}?")
                .setPositiveButton("Reset") { _, _ ->
                    // Chiamata al listener
                    listener.onSeatInfoResetRequested(timer)
                }
                .setNegativeButton("Annulla", null)
                .create()

            dialog.show()

            // Cambia il colore dei pulsanti a bianco
            dialog.getButton(AlertDialog.BUTTON_POSITIVE).setTextColor(Color.WHITE)
            dialog.getButton(AlertDialog.BUTTON_NEGATIVE).setTextColor(Color.WHITE)
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

    // Override per assicurarsi che le animazioni vengano fermate quando le view vengono riciclate
    override fun onViewRecycled(holder: TimerViewHolder) {
        super.onViewRecycled(holder)
        // Ferma eventuali animazioni attive
        holder.stopFloormanHighlight()
    }
}