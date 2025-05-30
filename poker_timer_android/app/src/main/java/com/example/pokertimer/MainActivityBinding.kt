package com.example.pokertimer

import android.widget.ImageButton
import android.widget.TextView

/**
 * Classe di binding personalizzata per tenere i riferimenti alle viste
 */
class MainActivityBinding {
    // Rimuoviamo i riferimenti ai pulsanti che non esistono più
    // lateinit var btnStartPause: Button
    // lateinit var btnReset: Button
    // lateinit var btnSwitch: Button
    // lateinit var btnStop: Button

    lateinit var tvTimer: TextView
    lateinit var tvActiveTimer: TextView
    lateinit var tvTableNumber: TextView
    lateinit var tvTimerStatus: TextView
    lateinit var tvSecondsLabel: TextView
    lateinit var btnPlayersSelection: ImageButton
    lateinit var btnCallFloorman: ImageButton
    lateinit var btnBarService: ImageButton

    companion object {
        fun bind(activity: MainActivity): MainActivityBinding {
            val binding = MainActivityBinding()

            // Riferimenti alle viste principali - rimuoviamo i bottoni che non esistono più
            // binding.btnStartPause = activity.findViewById(R.id.btn_start_pause)
            // binding.btnReset = activity.findViewById(R.id.btn_reset)
            // binding.btnSwitch = activity.findViewById(R.id.btn_switch)
            // binding.btnStop = activity.findViewById(R.id.btn_stop)

            binding.tvTimer = activity.findViewById(R.id.tv_timer)
            binding.tvActiveTimer = activity.findViewById(R.id.tv_active_timer)
            binding.tvTableNumber = activity.findViewById(R.id.tv_table_number)
            binding.tvTimerStatus = activity.findViewById(R.id.tv_timer_status)
            binding.tvSecondsLabel = activity.findViewById(R.id.tv_seconds_label)
            binding.btnPlayersSelection = activity.findViewById(R.id.btn_players_selection)
            binding.btnCallFloorman = activity.findViewById(R.id.btn_call_floorman)
            binding.btnBarService = activity.findViewById(R.id.btn_bar_service)

            return binding
        }
    }
}