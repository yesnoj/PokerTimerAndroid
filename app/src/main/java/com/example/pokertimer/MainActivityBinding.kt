package com.example.pokertimer

import android.widget.Button
import android.widget.ImageButton
import android.widget.TextView

/**
 * Classe di binding personalizzata per tenere i riferimenti alle viste
 */
class MainActivityBinding {
    lateinit var btnStartPause: Button
    lateinit var btnReset: Button
    lateinit var btnSwitch: Button
    lateinit var btnStop: Button
    lateinit var btnSettings: ImageButton
    lateinit var tvTimer: TextView
    lateinit var tvActiveTimer: TextView
    lateinit var tvTableNumber: TextView
    lateinit var tvTimerStatus: TextView
    lateinit var tvModeIndicators: TextView
    lateinit var tvModeInfo: TextView
    lateinit var tvBuzzerInfo: TextView
    lateinit var tvServerStatus: TextView
    lateinit var tvSecondsLabel: TextView

    companion object {
        fun bind(activity: MainActivity): MainActivityBinding {
            val binding = MainActivityBinding()

            // Riferimenti alle viste principali
            binding.btnStartPause = activity.findViewById(R.id.btn_start_pause)
            binding.btnReset = activity.findViewById(R.id.btn_reset)
            binding.btnSwitch = activity.findViewById(R.id.btn_switch)
            binding.btnStop = activity.findViewById(R.id.btn_stop)
            binding.btnSettings = activity.findViewById(R.id.btn_settings)
            binding.tvTimer = activity.findViewById(R.id.tv_timer)
            binding.tvActiveTimer = activity.findViewById(R.id.tv_active_timer)
            binding.tvTableNumber = activity.findViewById(R.id.tv_table_number)
            binding.tvTimerStatus = activity.findViewById(R.id.tv_timer_status)
            binding.tvModeIndicators = activity.findViewById(R.id.tv_mode_indicators)
            binding.tvModeInfo = activity.findViewById(R.id.tv_mode_info)
            binding.tvBuzzerInfo = activity.findViewById(R.id.tv_buzzer_info)
            binding.tvServerStatus = activity.findViewById(R.id.tv_server_status)
            binding.tvSecondsLabel = activity.findViewById(R.id.tv_seconds_label)

            return binding
        }
    }
}