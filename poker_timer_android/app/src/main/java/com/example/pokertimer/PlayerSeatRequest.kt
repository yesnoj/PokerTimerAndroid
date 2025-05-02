package com.example.pokertimer

/**
 * Classe che rappresenta una richiesta di posti liberi al tavolo
 */
data class PlayerSeatRequest(
    val tableNumber: Int,
    val selectedSeats: List<Int>
) {
    /**
     * Formatta la lista dei posti nel formato richiesto
     */
    fun getFormattedSeats(): String {
        return selectedSeats.joinToString(", ")
    }
}