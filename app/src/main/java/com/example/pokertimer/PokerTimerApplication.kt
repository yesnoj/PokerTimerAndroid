package com.example.pokertimer

import android.app.Activity
import android.app.Application

/**
 * Classe Application personalizzata per tenere traccia dell'Activity corrente
 */
class PokerTimerApplication : Application() {
    private var currentActivity: Activity? = null

    fun getCurrentActivity(): Activity? {
        return currentActivity
    }

    fun setCurrentActivity(activity: Activity?) {
        currentActivity = activity
    }
}