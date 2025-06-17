package com.example.pokertimer

import android.app.Activity
import android.os.Bundle
import android.util.Log

/**
 * Activity invisibile che viene chiamata quando l'utente fa swipe su una notifica floorman.
 * Si occupa di registrare il dismiss e poi termina immediatamente.
 */
class NotificationDismissActivity : Activity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        try {
            // Ottieni il numero del tavolo dalla notifica
            val tableNumber = intent.getIntExtra("table_number", -1)

            if (tableNumber != -1) {
                Log.d("NotificationDismissActivity", "Notifica floorman ignorata per tavolo $tableNumber")
                // Segna la notifica come ignorata
                FloormanNotificationTracker.markAsDismissed(this, tableNumber)
            }
        } catch (e: Exception) {
            Log.e("NotificationDismissActivity", "Errore nel processare dismiss: ${e.message}")
        } finally {
            // Termina subito questa activity
            finish()
        }
    }
}