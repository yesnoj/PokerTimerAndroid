package com.example.pokertimer

import android.animation.ObjectAnimator
import android.animation.PropertyValuesHolder
import android.content.Context
import android.content.res.ColorStateList
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
import android.util.Log

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
        // NUOVO: Metodo per gestire il click sull'icona floorman (mantenuto per compatibilità)
        fun onFloormanIconClicked(timer: TimerItem)
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

        /**
         * Verifica se un timer è un dispositivo Android basato sul device_id
         */
        private fun isAndroidTimer(deviceId: String): Boolean {
            return deviceId.startsWith("android_")  // Usa apici doppi per le stringhe
        }

        /**
         * Verifica se un timer è un dispositivo hardware (Arduino/ESP) basato sul device_id
         */
        private fun isHardwareTimer(deviceId: String): Boolean {
            return deviceId.startsWith("arduino_")  // Usa apici doppi per le stringhe
        }

        fun bind(timer: TimerItem, context: Context, listener: TimerActionListener) {
            // IMPORTANTE: Resetta sempre lo stile della card all'inizio
            val cardView = itemView as? com.google.android.material.card.MaterialCardView
            cardView?.apply {
                // Resetta allo stile predefinito
                strokeColor = Color.TRANSPARENT
                strokeWidth = 0
                // Non impostiamo alcun colore di background - lasciamo quello del tema/layout
            }

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

            // MODIFICATO: Nascondi sempre l'icona floorman
            floormanAlertIcon.visibility = View.GONE

            // Rimuovi qualsiasi listener dall'icona floorman (non più cliccabile)
            floormanAlertIcon.setOnClickListener(null)
            floormanAlertIcon.isClickable = false
            floormanAlertIcon.isFocusable = false

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
            startButton.setOnClickListener { listener.onStartClicked(timer) }
            pauseButton.setOnClickListener { listener.onPauseClicked(timer) }
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
            if (timestamp.isEmpty()) {
                return "N/A"
            }

            try {
                // Ottieni una versione "pulita" del timestamp
                val cleanTimestamp = if (timestamp.contains(".")) {
                    val parts = timestamp.split(".")
                    val prefix = parts[0]  // La parte prima del punto
                    val suffix = parts[1]  // La parte dopo il punto

                    // Prendi solo i primi 3 caratteri della parte decimale (millisecondi)
                    val milliseconds = if (suffix.length > 3) suffix.substring(0, 3) else suffix

                    // Ricostruisci il timestamp con solo millisecondi
                    if (suffix.endsWith("Z")) {
                        "$prefix.$milliseconds"
                    } else {
                        "$prefix.${milliseconds}Z"
                    }
                } else {
                    // Se non ci sono decimali, assicurati che termini con Z
                    if (timestamp.endsWith("Z")) timestamp else "${timestamp}Z"
                }

                android.util.Log.d("TimerAdapter", "Pulito timestamp da '$timestamp' a '$cleanTimestamp'")

                // OPZIONE 1: Il timestamp è già nell'ora locale (ma con il formato ISO)
                // In questo caso, dobbiamo ignorare la 'Z' che indica UTC
                if (cleanTimestamp.endsWith("Z")) {
                    // Rimuovi la 'Z' per trattare il timestamp come ora locale
                    val localTimestamp = cleanTimestamp.substring(0, cleanTimestamp.length - 1)
                    val localFormat = java.text.SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSS", java.util.Locale.getDefault())

                    // Non impostare alcun fuso orario esplicito
                    // localFormat.timeZone = java.util.TimeZone.getDefault()

                    val date = localFormat.parse(localTimestamp)
                    if (date != null) {
                        val outputFormat = java.text.SimpleDateFormat("HH:mm:ss", java.util.Locale.getDefault())
                        return outputFormat.format(date)
                    }
                }

                // OPZIONE 2: Il timestamp è effettivamente in UTC e dobbiamo correggere lo sfasamento
                // Se il server invia timestamp in UTC (standard per ISO 8601 con 'Z')
                val inputFormat = java.text.SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSS'Z'", java.util.Locale.getDefault())
                inputFormat.timeZone = java.util.TimeZone.getTimeZone("UTC")

                // Imposta il fuso orario locale, che dovrebbe essere Europe/Rome per l'Italia
                val outputFormat = java.text.SimpleDateFormat("HH:mm:ss", java.util.Locale.getDefault())

                // CORREZIONE: Non impostiamo un fuso orario specifico, ma usiamo quello del sistema
                // Questo dovrebbe correggere automaticamente lo sfasamento
                // outputFormat.timeZone = java.util.TimeZone.getDefault()

                val date = inputFormat.parse(cleanTimestamp)
                if (date == null) {
                    return "N/A"
                }

                // Formatta l'orario nel formato desiderato
                return outputFormat.format(date)

            } catch (e: Exception) {
                android.util.Log.e("TimerAdapter", "Errore nel parsing: ${e.message}", e)
                return "N/A"
            }
        }
    }
}