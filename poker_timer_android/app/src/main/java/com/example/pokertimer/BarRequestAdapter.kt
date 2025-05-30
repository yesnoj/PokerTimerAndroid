package com.example.pokertimer

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import java.text.SimpleDateFormat
import java.util.*

class BarRequestAdapter(
    private val requests: List<BarRequest>,
    private val onCompleteClick: (BarRequest) -> Unit
) : RecyclerView.Adapter<BarRequestAdapter.ViewHolder>() {

    class ViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val tableNumberText: TextView = view.findViewById(R.id.tableNumberText)
        val timestampText: TextView = view.findViewById(R.id.timestampText)
        val okButton: Button = view.findViewById(R.id.okButton)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_bar_request, parent, false)
        return ViewHolder(view)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val request = requests[position]

        holder.tableNumberText.text = "Tavolo ${request.tableNumber}"

        // Formatta il timestamp
        val sdf = SimpleDateFormat("HH:mm:ss", Locale.getDefault())
        val date = Date(request.timestamp)
        holder.timestampText.text = "Richiesto alle ${sdf.format(date)}"

        holder.okButton.setOnClickListener {
            onCompleteClick(request)
        }
    }

    override fun getItemCount() = requests.size
}