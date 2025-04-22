package com.example.pokertimer

import android.content.Context
import android.content.SharedPreferences

/**
 * Gestisce il salvataggio e il caricamento delle impostazioni del timer
 */
class PokerTimerPreferences(context: Context) {

    private val prefs: SharedPreferences = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)

    companion object {
        private const val PREFS_NAME = "poker_timer_prefs"
        private const val KEY_TIMER_T1 = "timer_t1"
        private const val KEY_TIMER_T2 = "timer_t2"
        private const val KEY_OPERATION_MODE = "operation_mode"
        private const val KEY_BUZZER_ENABLED = "buzzer_enabled"
        private const val KEY_TABLE_NUMBER = "table_number"
        private const val KEY_SERVER_URL = "server_url"
        private const val KEY_PLAYERS_COUNT = "players_count" // Nuova chiave

        // Valori di default
        private const val DEFAULT_TIMER_T1 = 20
        private const val DEFAULT_TIMER_T2 = 30
        private const val DEFAULT_OPERATION_MODE = 1
        private const val DEFAULT_BUZZER_ENABLED = true
        private const val DEFAULT_TABLE_NUMBER = 1
        private const val DEFAULT_SERVER_URL = "http://192.168.4.1"
        private const val DEFAULT_PLAYERS_COUNT = 10 // Nuovo valore predefinito
    }

    /**
     * Salva le impostazioni del timer
     */
    fun saveTimerSettings(timerT1: Int, timerT2: Int, operationMode: Int, buzzerEnabled: Boolean,
                          tableNumber: Int, serverUrl: String, playersCount: Int = DEFAULT_PLAYERS_COUNT) {
        prefs.edit().apply {
            putInt(KEY_TIMER_T1, timerT1)
            putInt(KEY_TIMER_T2, timerT2)
            putInt(KEY_OPERATION_MODE, operationMode)
            putBoolean(KEY_BUZZER_ENABLED, buzzerEnabled)
            putInt(KEY_TABLE_NUMBER, tableNumber)
            putString(KEY_SERVER_URL, serverUrl)
            putInt(KEY_PLAYERS_COUNT, playersCount) // Salva il numero di giocatori
            apply()
        }
    }

    /**
     * Carica le impostazioni salvate
     */
    fun loadTimerSettings(): PokerTimerState {
        return PokerTimerState(
            timerT1 = prefs.getInt(KEY_TIMER_T1, DEFAULT_TIMER_T1),
            timerT2 = prefs.getInt(KEY_TIMER_T2, DEFAULT_TIMER_T2),
            operationMode = prefs.getInt(KEY_OPERATION_MODE, DEFAULT_OPERATION_MODE),
            buzzerEnabled = prefs.getBoolean(KEY_BUZZER_ENABLED, DEFAULT_BUZZER_ENABLED),
            // Gli altri valori usano i default del data class
            currentTimer = prefs.getInt(KEY_TIMER_T1, DEFAULT_TIMER_T1),
            tableNumber = prefs.getInt(KEY_TABLE_NUMBER, DEFAULT_TABLE_NUMBER),
            serverUrl = prefs.getString(KEY_SERVER_URL, DEFAULT_SERVER_URL) ?: DEFAULT_SERVER_URL,
            playersCount = prefs.getInt(KEY_PLAYERS_COUNT, DEFAULT_PLAYERS_COUNT) // Carica il numero di giocatori
        )
    }
}