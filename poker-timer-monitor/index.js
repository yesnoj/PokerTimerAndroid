const express = require('express');
const cors = require('cors');
const path = require('path');
const bodyParser = require('body-parser');
const fs = require('fs');
const dgram = require('dgram'); // Aggiungi questa importazione per UDP

const app = express();
const port = 3000;
const DISCOVERY_PORT = 8888; // Porta per il servizio di discovery

// Middleware per parsing e sicurezza
app.use(cors());
app.use(express.json());
app.use(bodyParser.json());
app.use(express.urlencoded({ extended: true }));

// Memorizza lo stato di tutti i timer
const timers = {};

// Crea un socket UDP per il servizio di discovery
const discoveryServer = dgram.createSocket('udp4');

// Gestisci gli errori del server discovery
discoveryServer.on('error', (err) => {
  console.error(`Server discovery error:\n${err.stack}`);
  discoveryServer.close();
});

// Gestisci i messaggi di discovery
discoveryServer.on('message', (msg, rinfo) => {
  const message = msg.toString();
  console.log(`Discovery request received: ${message} from ${rinfo.address}:${rinfo.port}`);
  
  // Verifica che sia una richiesta di discovery del Poker Timer
  if (message.trim() === 'POKER_TIMER_DISCOVERY') {
    console.log(`Sending discovery response to ${rinfo.address}:${rinfo.port}`);
    // Invia una risposta con le informazioni del server
    const response = Buffer.from('POKER_TIMER_SERVER');
    discoveryServer.send(response, 0, response.length, rinfo.port, rinfo.address);
  }
});

// Avvia il server di discovery
discoveryServer.on('listening', () => {
  const address = discoveryServer.address();
  console.log(`Discovery server listening on ${address.address}:${address.port}`);
  // Abilita il broadcast
  discoveryServer.setBroadcast(true);
});

// Bind del socket di discovery
discoveryServer.bind(DISCOVERY_PORT);

// Endpoint per ricevere aggiornamenti dai timer
app.post('/api/status', (req, res) => {
  const timerData = req.body;
  const deviceId = timerData.device_id;
  
  console.log(`Received update from ${deviceId}`);
  
  // Aggiorna timestamp
  timerData.last_update = new Date().toISOString();
  
  // Aggiungi indirizzo IP
  const ipAddress = req.socket.remoteAddress;
  timerData.ip_address = ipAddress ? ipAddress.replace(/^.*:/, '') : '';

  // Memorizza lo stato aggiornato
  timers[deviceId] = {...timers[deviceId], ...timerData};
  
  // Controlla se ci sono comandi in sospeso per questo timer
  let responseData = { status: "ok" };
  
  if (timers[deviceId].pending_command) {
    // Aggiungi il comando alla risposta
    responseData.command = timers[deviceId].pending_command;
    
    // Se il comando è "settings", invia le nuove impostazioni
    if (timers[deviceId].pending_command === "settings" || 
        timers[deviceId].pending_command === "apply_settings") {
      responseData.settings = timers[deviceId].pending_settings;
      console.log('Sending new settings to device:', responseData.settings);
    }
    
    // Rimuovi il comando pendente dopo averlo inviato
    delete timers[deviceId].pending_command;
    delete timers[deviceId].pending_settings;
  }
  
  // Controlla se c'è una richiesta di posti da comunicare
  if (timers[deviceId].seat_info && timers[deviceId].seat_info.needs_web_notification) {
    // Aggiungi le informazioni sui posti alla risposta
    responseData.seat_request = {
      open_seats: timers[deviceId].seat_info.open_seats,
      action: timers[deviceId].seat_info.action
    };
    
    // Resetta il flag
    timers[deviceId].seat_info.needs_web_notification = false;
  }
  
  res.json(responseData);
});

// Endpoint per ottenere lo stato di tutti i timer
app.get('/api/timers', (req, res) => {
  res.json(timers);
});

// Endpoint per salvare le impostazioni di un timer specifico
app.post('/api/settings/:deviceId', (req, res) => {
  const deviceId = req.params.deviceId;
  const settings = req.body;
  
  console.log(`Ricevute impostazioni per ${deviceId}:`, settings);
  
  // Controllo esistenza dispositivo
  if (!timers[deviceId]) {
    timers[deviceId] = {};
  }
  
  // Aggiorna i valori specifici del timer
  timers[deviceId].mode = settings.mode;
  timers[deviceId].t1_value = settings.t1;
  timers[deviceId].t2_value = settings.t2;
  timers[deviceId].table_number = settings.tableNumber;
  timers[deviceId].buzzer = settings.buzzer;
  
  // Imposta il comando in sospeso
  timers[deviceId].pending_command = "settings";
  timers[deviceId].pending_settings = settings;
  
  // Risposta JSON
  res.json({ 
    status: "settings_queued", 
    settings: settings 
  });
});

// Endpoint per gestire i comandi del timer
app.post('/api/command/:deviceId', (req, res) => {
  const deviceId = req.params.deviceId;
  const { command } = req.body;
  
  console.log(`Received command ${command} for ${deviceId}`);
  
  if (!timers[deviceId]) {
    return res.status(404).json({ error: "Timer not found" });
  }
  
  // Se il comando è reset_seat_info, rimuovi le informazioni sui posti
  if (command === "reset_seat_info") {
    console.log(`Resetting seat info for device ${deviceId}`);
    
    // Rimuovi le informazioni sui posti - verifica il log di questa operazione
    if (timers[deviceId]) {
      delete timers[deviceId].seat_info;
      console.log(`Seat info removed for device ${deviceId}`);
    }
    
    // Rispondi con successo
    return res.json({ 
      status: "success", 
      command: command 
    });
  }
  
  // Imposta il comando in sospeso
  timers[deviceId].pending_command = command;
  
  res.json({ 
    status: "command_queued", 
    command: command 
  });
});

// Endpoint per gestire le richieste di posti liberi
app.post('/api/seat_request', (req, res) => {
  const requestData = req.body;
  
  console.log(`Received seat request for table ${requestData.table_number}`);
  console.log(`Seats: ${requestData.seats.join(', ')}`);
  
  // Cerca il dispositivo corrispondente a questo tavolo
  let targetDeviceId = null;
  for (const deviceId in timers) {
    if (timers[deviceId].table_number === requestData.table_number) {
      targetDeviceId = deviceId;
      break;
    }
  }
  
  if (targetDeviceId) {
    // Memorizza i dati dei posti nella struttura del timer
    if (!timers[targetDeviceId].seat_info) {
      timers[targetDeviceId].seat_info = {};
    }
    
    timers[targetDeviceId].seat_info = {
      open_seats: requestData.seats,
      timestamp: new Date().toISOString(),
      action: requestData.action || "seat_open",
      needs_web_notification: true
    };
    
    // Invia una risposta di successo
    res.json({ 
      status: "success", 
      message: `Seat request for table ${requestData.table_number} processed successfully`
    });
  } else {
    // Nessun dispositivo trovato per questo tavolo
    res.status(404).json({ 
      status: "error", 
      message: `No device found for table ${requestData.table_number}`
    });
  }
});

// Endpoint per confermare che la notifica è stata mostrata all'utente
app.post('/api/acknowledge_seat_notification/:deviceId', (req, res) => {
  const deviceId = req.params.deviceId;
  
  console.log(`Acknowledging notification for device: ${deviceId}`);
  
  // Gestione più robusta: anche se non troviamo il timer o il seat_info,
  // rispondiamo con successo
  if (timers[deviceId]) {
    if (timers[deviceId].seat_info) {
      timers[deviceId].seat_info.needs_web_notification = false;
      console.log(`Notification flag set to false for device: ${deviceId}`);
    } else {
      // Crea la struttura seat_info se non esiste
      timers[deviceId].seat_info = { needs_web_notification: false };
      console.log(`Created seat_info with flag false for device: ${deviceId}`);
    }
  } else {
    console.log(`Device not found: ${deviceId}, but acknowledging anyway`);
  }
  
  // Sempre rispondere con successo
  res.json({ status: "success" });
});

// Endpoint per cancellare tutti i timer
app.delete('/api/timers', (req, res) => {
  console.log('Richiesta di cancellazione di tutti i timer');
  
  // Conta quanti timer erano presenti
  const timerCount = Object.keys(timers).length;
  
  // Svuota l'oggetto timers
  for (const key in timers) {
    delete timers[key];
  }
  
  // Invia una risposta con il numero di timer cancellati
  res.json({ 
    status: "success", 
    message: `${timerCount} timer cancellati con successo`
  });
});

// Servizio pagine statiche
app.use(express.static('public'));

// Gestione route principale
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Gestione errori
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).send('Qualcosa è andato storto!');
});

// Endpoint per ottenere informazioni sul server (utile per la discovery)
app.get('/api/server-info', (req, res) => {
  res.json({
    name: "Poker Timer Server",
    version: "1.0",
    port: port,
    uptime: process.uptime()
  });
});

// Avvio server
app.listen(port, () => {
  console.log(`Timer monitoring server running on port ${port}`);
  console.log(`Discovery service running on port ${DISCOVERY_PORT}`);
  console.log(`Dashboard disponibile su http://localhost:${port}`);
});

// Gestione chiusura applicazione
process.on('SIGINT', () => {
  console.log('Server in fase di arresto...');
  // Chiudi anche il server di discovery
  discoveryServer.close();
  process.exit();
});