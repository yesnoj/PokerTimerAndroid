package com.example.pokertimer

/**
 * Classe che rappresenta le informazioni sui posti liberi al tavolo
 * @param openSeats Lista dei numeri dei posti liberi
 * @param needsNotification Flag che indica se è necessario mostrare una notifica per questa informazione
 */
data class SeatInfo(
    val openSeats: List<Int>,
    var needsNotification: Boolean = true
)