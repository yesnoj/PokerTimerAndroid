package com.example.pokertimer;

import android.content.Intent;
import android.os.Bundle;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.appcompat.widget.Toolbar;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;
import androidx.swiperefreshlayout.widget.SwipeRefreshLayout;

import com.google.android.material.floatingactionbutton.FloatingActionButton;

public class DashboardActivity extends AppCompatActivity {

    private RecyclerView timersRecyclerView;
    private SwipeRefreshLayout swipeRefreshLayout;
    private View emptyStateView;
    private View errorStateView;
    private View loadingStateView;
    private FloatingActionButton refreshFab;
    private Button refreshButton;
    private Button errorRetryButton;
    private TextView errorMessageText;

    private String serverUrl;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_dashboard);

        // Ottieni l'URL del server dall'intent
        serverUrl = getIntent().getStringExtra("server_url");
        if (serverUrl == null || serverUrl.isEmpty()) {
            Toast.makeText(this, "URL del server non valido", Toast.LENGTH_SHORT).show();
            finish();
            return;
        }

        // Inizializza la Toolbar
        Toolbar toolbar = findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);

        // Assicurati che il titolo sia visibile nella toolbar
        if (getSupportActionBar() != null) {
            getSupportActionBar().setTitle("Timer Dashboard");
            getSupportActionBar().setDisplayHomeAsUpEnabled(true);
        }

        // Inizializza le viste
        timersRecyclerView = findViewById(R.id.timersRecyclerView);
        swipeRefreshLayout = findViewById(R.id.swipeRefreshLayout);
        emptyStateView = findViewById(R.id.emptyStateView);
        errorStateView = findViewById(R.id.errorStateView);
        loadingStateView = findViewById(R.id.loadingStateView);
        refreshFab = findViewById(R.id.refreshFab);
        refreshButton = findViewById(R.id.refreshButton);
        errorRetryButton = findViewById(R.id.errorRetryButton);
        errorMessageText = findViewById(R.id.errorMessageText);

        // Configura la RecyclerView
        timersRecyclerView.setLayoutManager(new LinearLayoutManager(this));

        // In una implementazione reale, qui creeremmo l'adapter per visualizzare i timer
        // Per ora mostriamo solo lo stato vuoto
        showEmptyState();

        // Configura il listener per il pull-to-refresh
        swipeRefreshLayout.setOnRefreshListener(this::refreshTimerData);

        // Configura i pulsanti di refresh
        refreshFab.setOnClickListener(v -> refreshTimerData());
        refreshButton.setOnClickListener(v -> refreshTimerData());
        errorRetryButton.setOnClickListener(v -> refreshTimerData());
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        getMenuInflater().inflate(R.menu.dashboard_menu, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(@NonNull MenuItem item) {
        int id = item.getItemId();

        if (id == android.R.id.home) {
            onBackPressed();
            return true;
        } else if (id == R.id.action_refresh) {
            refreshTimerData();
            return true;
        } else if (id == R.id.action_change_server) {
            Intent intent = new Intent(this, ServerUrlActivity.class);
            startActivity(intent);
            finish();
            return true;
        } else if (id == R.id.action_switch_to_timer) {
            // Passa alla modalità Timer
            Intent intent = new Intent(this, MainActivity.class);
            startActivity(intent);
            finish();
            return true;
        }

        return super.onOptionsItemSelected(item);
    }

    /**
     * Aggiorna i dati dei timer
     */
    private void refreshTimerData() {
        // Mostra lo stato di caricamento
        showLoadingState();

        // Simula un ritardo nel caricamento dei dati
        timersRecyclerView.postDelayed(() -> {
            // Nascondi l'indicatore di refresh
            swipeRefreshLayout.setRefreshing(false);

            // Per ora, mostriamo solo lo stato vuoto
            // In una implementazione reale, qui caricheremmo i dati dal server

            // Simuliamo uno stato vuoto
            showEmptyState();
        }, 1500);
    }

    /**
     * Mostra lo stato di caricamento
     */
    private void showLoadingState() {
        loadingStateView.setVisibility(View.VISIBLE);
        emptyStateView.setVisibility(View.GONE);
        errorStateView.setVisibility(View.GONE);
        timersRecyclerView.setVisibility(View.GONE);
    }

    /**
     * Mostra lo stato vuoto quando non ci sono timer
     */
    private void showEmptyState() {
        loadingStateView.setVisibility(View.GONE);
        emptyStateView.setVisibility(View.VISIBLE);
        errorStateView.setVisibility(View.GONE);
        timersRecyclerView.setVisibility(View.GONE);
    }

    /**
     * Mostra lo stato di errore
     */
    private void showErrorState(String message) {
        loadingStateView.setVisibility(View.GONE);
        emptyStateView.setVisibility(View.GONE);
        errorStateView.setVisibility(View.VISIBLE);
        timersRecyclerView.setVisibility(View.GONE);

        errorMessageText.setText(message);
    }

    /**
     * Mostra la lista dei timer
     */
    private void showTimersList() {
        loadingStateView.setVisibility(View.GONE);
        emptyStateView.setVisibility(View.GONE);
        errorStateView.setVisibility(View.GONE);
        timersRecyclerView.setVisibility(View.VISIBLE);
    }
}