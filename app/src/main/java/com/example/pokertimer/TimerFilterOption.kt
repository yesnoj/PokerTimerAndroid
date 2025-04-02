package com.example.pokertimer

/**
 * Enumeration che definisce le opzioni di filtro disponibili
 */
enum class TimerFilterOption(val title: String) {
    ALL("Tutti i timer"),
    ONLINE("Timer online"),
    OFFLINE("Timer offline");

    companion object {
        // Funzione per ottenere tutte le opzioni come array di stringhe
        fun getTitles(): Array<String> {
            return values().map { it.title }.toTypedArray()
        }

        // Funzione per ottenere l'opzione corrispondente al titolo
        fun fromTitle(title: String): TimerFilterOption {
            return values().firstOrNull { it.title == title } ?: ALL
        }
    }
}