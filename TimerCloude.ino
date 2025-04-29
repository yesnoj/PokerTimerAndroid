//IMPORTANT NOTE : If used the Arduino Lilygo Mini D1 Plus!
//The switch need to be set to OFF, to be recognized by Arduino IDE,
//Then to upload the sketch, while on serial monitor is shown "Connecting...." , need to be placed to ON!Otherwise the upload will not work!
//https://adafruit.github.io/Adafruit_NeoPixel/html/class_adafruit___neo_pixel.html
//Consider to use also https://github.com/ripred/ButtonGestures eventually for 3 button press

/*
 * TIMER POKER - GUIDA ALLE MODALITÀ E CONFIGURAZIONI
 * ---------------------------------------------------
 * 
 * PANORAMICA DELLE MODALITÀ OPERATIVE
 * -----------------------------------
 * Il timer supporta 4 diverse modalità operative che determinano il comportamento
 * del dispositivo all'avvio e in risposta ai click del pulsante.
 * 
 * Modalità 1: T1/T2 con avvio automatico
 * - All'avvio: il timer rimane fermo su T1
 * - Singolo click: se in pausa, riprende da dove interrotto
 *                  se fermo o terminato, avvia il timer attuale (T1 o T2)
 *                  altrimenti reimposta il timer attuale (T1 o T2) e parte subito
 * - Doppio click: passa all'altro timer (T1↔T2) e mette in pausa
 * - Click lungo: mette in pausa il timer
 * 
 * Modalità 2: T1/T2 con avvio manuale
 * - All'avvio: il timer rimane fermo su T1
 * - Singolo click: se in pausa, riprende da dove interrotto
 *                  se fermo o terminato, avvia il timer attuale (T1 o T2)
 *                  se in esecuzione, lo resetta e lo ferma
 * - Doppio click: passa all'altro timer (T1↔T2) ma rimane fermo
 * - Click lungo: mette in pausa il timer
 * 
 * Modalità 3: Solo T1 con avvio automatico
 * - All'avvio: il timer rimane fermo su T1
 * - Singolo click: se in pausa, riprende da dove interrotto
 *                  se fermo o terminato, avvia il timer da T1
 *                  altrimenti reimposta T1 e parte subito
 * - Doppio click: assente (non fa nulla)
 * - Click lungo: mette in pausa il timer
 * 
 * Modalità 4: Solo T1 con avvio manuale
 * - All'avvio: il timer rimane fermo su T1
 * - Singolo click: se in pausa, riprende da dove interrotto
 *                  se fermo o terminato, avvia il timer da T1
 *                  se in esecuzione, lo resetta a T1 e lo ferma
 * - Doppio click: assente (non fa nulla)
 * - Click lungo: mette in pausa il timer
 * 
 * COME CAMBIARE LA MODALITÀ OPERATIVA E CONFIGURAZIONI
 * ---------------------------------------------------
 * 1. All'avvio del dispositivo, tenere premuto il pulsante per 5 secondi
 * 2. Il display mostrerà "OP" seguito dal numero della modalità attuale
 * 3. Premere il pulsante (click singolo) per cambiare tra le opzioni:
 *    - 1, 2, 3, 4: Modalità operative
 *    - t1: Configurazione del timer T1
 *    - t2: Configurazione del timer T2
 *    - b: Configurazione del buzzer
 *    - nF: Configurazione WiFi (attivazione/disattivazione)
 *    - T: Configurazione numero del tavolo
 * 4. Per le modalità 1-4, confermare la scelta con un doppio click per salvare e uscire
 * 5. Per le configurazioni t1, t2, b, WiFi e numero tavolo:
 *    - Doppio click per entrare nel submenu
 *    - Click singolo per modificare i valori (o attivare/disattivare nel caso di buzzer e WiFi)
 *    - Doppio click per salvare e uscire
 *    - Dopo alcuni secondi di inattività, si torna al menu principale
 * 
 * PAUSA E RIPRESA DEL TIMER
 * -------------------------
 * In tutte le modalità:
 * - Pressione lunga: mette in pausa il timer
 * - Quando il timer è in pausa, un singolo click lo fa ripartire da dove era stato interrotto
 * 
 * FACTORY RESET (RIPRISTINO IMPOSTAZIONI DI FABBRICA)
 * --------------------------------------------------
 * Per ripristinare completamente il dispositivo alle impostazioni di fabbrica:
 * 1. Tenere premuto il pulsante per 15 secondi continuativi in qualsiasi momento
 * 2. Il display mostrerà "Fr" (Factory Reset) come conferma
 * 3. Il dispositivo emetterà una sequenza di 3 beep e si riavvierà automaticamente
 * 4. Le impostazioni predefinite verranno ripristinate:
 *    - Modalità 1
 *    - Timer T1: 20 secondi
 *    - Timer T2: 30 secondi
 *    - Buzzer: ON
 *    - WiFi: ON
 *    - Configurazione WiFi: resettata
 *    - Numero del tavolo: 1
 * 
 * CONFIGURAZIONE WIFI
 * ------------------
 * È possibile attivare o disattivare il WiFi attraverso il menu:
 * 1. Entrare nel menu delle modalità (premere il pulsante per 5 secondi all'avvio)
 * 2. Premere il pulsante ripetutamente fino a visualizzare "nF" (configurazione WiFi)
 * 3. Fare doppio click per entrare nel submenu
 * 4. Il display mostrerà:
 *    - "yn" se il WiFi è attivato (y=yes, n=no)
 *    - "nn" se il WiFi è disattivato (n=no, n=no)
 * 5. Premere il pulsante per cambiare lo stato
 * 6. Fare doppio click per salvare e uscire
 * 
 * Disattivare il WiFi può essere utile per:
 * - Aumentare la durata della batteria
 * - Eliminare le potenziali interferenze con altri dispositivi
 * - Usare il timer in contesti dove il WiFi non è necessario
 * 
 * CONFIGURAZIONE NUMERO TAVOLO
 * ---------------------------
 * È possibile impostare un numero identificativo per il tavolo (0-99):
 * 1. Entrare nel menu delle modalità (premere il pulsante per 5 secondi all'avvio)
 * 2. Premere il pulsante ripetutamente fino a visualizzare "T" (configurazione numero tavolo)
 * 3. Fare doppio click per entrare nel submenu
 * 4. Il display mostrerà il numero attuale del tavolo
 * 5. Premere il pulsante per incrementare il numero
 * 6. Fare doppio click per cambiare direzione (incrementa/decrementa)
 * 7. Fare doppio click nuovamente per salvare e uscire
 * 
 * INTERFACCIA WEB
 * ---------------
 * Il timer dispone di due interfacce web per la configurazione:
 * 
 * 1. Interfaccia diretta (modalità AP):
 *    - Al primo avvio o quando il WiFi è in modalità Access Point, il timer crea una rete
 *      WiFi con nome "PokerTimer-XXXX" (dove XXXX è un identificatore univoco)
 *    - Connettiti a questa rete dal tuo dispositivo
 *    - Apri il browser e vai all'indirizzo 192.168.4.1
 *    - L'interfaccia permette di configurare tutti i parametri del timer (T1, T2, modalità, ecc.)
 *    - Puoi anche configurare la connessione a una rete WiFi esistente
 * 
 * 2. Interfaccia tramite server centrale:
 *    - Quando il timer è collegato a una rete WiFi e configurato con l'indirizzo del server
 *    - Il timer invia periodicamente il proprio stato al server
 *    - Tramite l'interfaccia web del server è possibile:
 *      - Visualizzare lo stato di tutti i timer collegati
 *      - Controllare i timer (start, pause)
 *      - Modificare le impostazioni remotamente
 *    - I comandi e le impostazioni vengono sincronizzati al prossimo aggiornamento del timer
 * 
 * NOTA IMPORTANTE: Le modifiche alle impostazioni dall'interfaccia web richiedono alcuni
 * secondi per essere applicate, dato che il timer deve ricevere i cambiamenti e salvarli in
 * memoria permanente.
 * 
 * GESTIONE BATTERIA
 * ----------------
 * Il timer monitora costantemente il livello della batteria:
 * - Quando la batteria è scarica, il display mostrerà "LO" seguito da un'animazione di ricarica
 * - Il livello di carica è visibile nell'interfaccia web
 * - Il dispositivo passa in modalità risparmio energetico quando necessario
 * - Disattivare il WiFi aumenta significativamente la durata della batteria
 * 
 * FUNZIONE DI DIAGNOSTICA
 * ----------------------
 * Il dispositivo include funzioni di diagnostica avanzate:
 * - Riavviare il dispositivo mentre si tiene premuto il pulsante reset avvia una modalità di diagnostica
 * - In caso di problemi con il salvataggio delle impostazioni, è possibile resettare completamente
 *   la memoria EEPROM utilizzando l'endpoint "/reset-eeprom" nell'interfaccia web
 * - Per un reset completo, tenere premuto il pulsante per 15 secondi o utilizzare l'opzione
 *   "Factory Reset" nell'interfaccia web
 * 
 * REQUISITI HARDWARE
 * -----------------
 * - Scheda ESP8266 (WeMos ESP-WROOM-02) o compatibile
 * - Display a segmenti LED (NeoPixel)
 * - Pulsante per il controllo
 * - Buzzer (opzionale)
 * 
 * REQUISITI SOFTWARE
 * -----------------
 * - Arduino IDE con supporto ESP8266
 * - Librerie richieste:
 *   - ButtonGestures
 *   - EEPROM
 *   - Adafruit_NeoPixel
 *   - digitalWriteFast
 *   - ESP8266WiFi
 *   - ESP8266WebServer
 *   - ElegantOTA
 *   - DNSServer
 *   - WiFiManager
 *   - ArduinoJson
 */

#include "Arduino.h"
#include <ButtonGestures.h>
//#include "esp_adc_cal.h" //Not work with RP2040
#include <EEPROM.h>
#include <Adafruit_NeoPixel.h>
#include <digitalWriteFast.h>

#include <DNSServer.h>
#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>
#include <DNSServer.h>
#include <WiFiManager.h>
#include <FS.h>
#include <Ticker.h>
#include <ESP8266httpUpdate.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClient.h>
#include <ArduinoJson.h>




//WeMos ESP8266 ESP-WROOM-02 (OK BRIGHTNESS) https://artofcircuits.com/product/esp-wroom-02-wifi-18650-battery-charger-board

#define ledsPin      D1 //input pin Neopixel is attached to
#define buzzerPin    D2 //D2 is the correct one...D8 is used for just not buzz the buzzer!
#define buttonPin    D6
#define buttonLedPin D7
#define ledPin       2 //integrated board led
#define voltagePin   A0
//#define bluLED       2
//#define greenPin     16 //integrated board led

//Contatti bottone -> pin
//     yellow NO   -> D6 (button)
//            NC   -> N/A
//      green 2    -> D7 (led)
//      black 1-C  -> GND

//WEMOS LOLIN32 Lite (board with battery JST charger included) (OK BRIGHTNESS)
/*
#define ledsPin      4 //input pin Neopixel is attached to
#define buzzerPin    2
#define buttonLedPin 15//D2//integrated button led
#define buttonPin    13
#define ledPin       22 //integrated board led
*/

//RP2040 (OK BRIGHTNESS)
/*
#define ledsPin      0 //input pin Neopixel is attached to
#define ledPin       16 //integrated board led
#define buttonLedPin 1//D2//integrated button led
#define buzzerPin    8
#define buttonPin    7
*/

//S2 Mini (LOW BRIGHTNESS)
/*
#define ledsPin      1//D1//0 //input pin Neopixel is attached to
#define ledPin       15//16//integrated board led
#define buttonLedPin 2//D2//integrated button led
#define buzzerPin    6//D4 //8 //TBD
#define buttonPin    4//D3//7//
*/

//Lilygo Mini D1 Plus Battery (OK BRIGHTNESS)
/*
#define ledPin       0// can't finde the built-in led pin on board
#define ledsPin      19
#define buzzerPin    18
#define buttonPin    8
#define buttonLedPin 9
#define BAT_ADC      2
*/


#define timeOperationModeMenu 15000 // Timeout per uscire dal menu modalità operativa


#define OPERATION_MODE_1    1    // T1/T2 switchabile, con tap torna a T1/T2 e parte subito a contare
#define OPERATION_MODE_2    2    // T1/T2 switchabile, con tap riparte a contare da T1/T2
#define OPERATION_MODE_3    3    // Solo T1, con tap torna a T1 e parte subito a contare
#define OPERATION_MODE_4    4    // Solo T1, con tap resetta a T1 e rimane fermo
#define OPERATION_MODE_T1   5    // Configurazione di T1
#define OPERATION_MODE_T2   6    // Configurazione di T2  
#define OPERATION_MODE_BUZZER 7  // Modalità per configurare il buzzer
#define OPERATION_MODE_WIFI 8  // Modalità per configurare il WiFi
#define OPERATION_MODE_TABLE 9  // Modalità per configurare il numero del tavolo
#define OPERATION_MODE_PLAYERS 10  // Modalità per configurare il numero di giocatori


#define FACTORY_RESET_PRESS_TIME 15000  // 15 secondi di pressione per factory reset

#define VOLTAGE_SAMPLES 5

#define tickNote           100
#define pauseNote          550
#define endingNote         1000
#define notePauseDuration  50
#define noteTickDuration   80
#define noteFinishDuration 400

#define timerSet_20          20
#define timerSet_30          30
#define interval             1000 //1s timer
#define interval_doublePress 300
#define interval_longPress   1000
#define interval_debounce    60
#define interval_click       10
#define intervalAnimation    25
#define startupAnimations    2
#define timeLife_60          60000 //1min time life
#define timeBuzzerMenu       3000
#define timeTimeMenu         3000
#define timeTimeMenuExit     5000


#define memAddressBuzzerState 0
#define memAddressTimer1      10
#define memAddressTimer2      20
#define memAddressOperationMode 30  // Indirizzo EEPROM per salvare la modalità operativa
#define memAddressWiFiState 40
#define memAddressTableNumber 50  // Indirizzo EEPROM per salvare il numero del tavolo
#define memAddressPlayersCount 60  // Indirizzo EEPROM per salvare il numero di giocatori

static uint8_t buzzerOnOff = 1;
static uint8_t pokerTimer1 = timerSet_20;
static uint8_t pokerTimer2 = timerSet_30;

#define NUMPIXELS            56 // total number of neopixels in strip
#define LED_MODULES          2 //total number of digits (6 max, 2 per side)

#define ledPower10  10
#define ledPower20  20
#define ledPower30  30
#define ledPower40  40
#define ledPower50  50
#define ledPower60  60
#define ledPower70  70
#define ledPower80  80
#define ledPower90  90
#define ledPower100 100

#define DISCOVERY_PORT 8888


static uint8_t previousTimer;
static uint8_t timerCurrent;
static uint8_t pokerTimer1or2;

unsigned long previousMillis               = 0;
unsigned long previousMillisLife           = 0;
unsigned long previousMillisVolt           = 0;
unsigned long previousMillisLowVolt        = 0;
unsigned long previousMillisBuzzerOnOff    = 0;
unsigned long previousMillisPulseTime      = 0;

unsigned long currentMillis        = 0;
static uint8_t isStarted           = 0;
static uint8_t isPaused            = 0;
static uint8_t timeExpired         = 0;
static uint8_t ledState            = LOW;
static uint8_t wasCharging         = 0;
static uint8_t isDisCharging       = 0;
static float tempVoltageActual     = 0;
static float tempVoltageOld        = 0;
static uint8_t isFirstTime         = 1;
static uint8_t isBuzzerMenu        = 0;
static uint8_t isTime1MenuSet      = 0;
static uint8_t isTime2MenuSet      = 0;
static uint8_t pokerTimerIncrement = 5;
static uint8_t temporaryValueTime  = 0;
static uint8_t isWiFiMenu          = 0;

static uint8_t operationMode = OPERATION_MODE_1;  // Modalità di default
static uint8_t isOperationModeMenu = 0;           // Flag per il menu di selezione modalità
static uint8_t temporaryModeValue = 0;            // Valore temporaneo durante la configurazione
unsigned long previousMillisOperationMode = 0;     // Timer per il menu modalità
unsigned long previousMillisExitOperationMode = 0; // Timer per uscire dal menu

static float Voltage = 0.0;
static uint32_t readADC_Cal(int ADC_Raw);

// Setup a new OneButton on pin PIN_INPUT
// The 2. parameter activeLOW is true, because external wiring sets the button to LOW when pressed.

ButtonGestures  button(buttonPin,LOW,INPUT_PULLUP);

Adafruit_NeoPixel pixels = Adafruit_NeoPixel(NUMPIXELS, ledsPin, NEO_GRB + NEO_KHZ800);

uint8_t memAddressClock   = 0;
uint8_t memAddressVolt    = 10;
uint8_t memAddressPercent = 20;

uint16_t readClockLife = 0;
uint16_t lastClockLife = 0;

float readVolt = 0;
float lastVolt = 0;

float readPercent = 0;
float lastPercent = 0;

const float minimumVoltage1 = 3.2; //about 13 hours...
const float minimumVoltage2 = 3.5;


ESP8266WebServer server(80);  // Server sulla porta 80
WiFiManager wifiManager;      // Per gestire la configurazione WiFi
const char* hostname = "PokerTimer";  // Nome del dispositivo nella rete
bool wifiEnabled = true;      // Flag per abilitare/disabilitare WiFi

unsigned long buttonPressStartTime = 0;
bool isLongFactoryResetPress = false;

unsigned long wifiSetupStartTime = 0;
bool wifiSetupInProgress = false;
bool wifiAPMode = false;
unsigned long lastWiFiStatusCheck = 0;

unsigned long lastServerDiscoveryAttempt = 0;
const unsigned long SERVER_DISCOVERY_INTERVAL = 60000; // Tenta discovery ogni minuto
bool serverDiscovered = false;
String discoveredServerUrl = "";
const char* defaultMonitorServerUrl = "http://192.168.1.89:3000/api/status"; // URL di fallback


const byte DNS_PORT = 53;          // Porta standard DNS
DNSServer dnsServer;               // Server DNS per il captive portal
bool captivePortalEnabled = false; // Flag per gestire il captive portal
bool wifiStateWasChanged = false;
// In case the momentary button puts the input to HIGH when pressed:
// The 2. parameter activeLOW is false when the external wiring sets the button to HIGH when pressed.
// The 3. parameter can be used to disable the PullUp .
// OneButton button(PIN_INPUT, false, false);
//OneButton button(buttonPin, true , true);


struct WiFiCredentials {
  char ssid[33];      // SSID max 32 caratteri + null terminator
  char password[65];  // Password max 64 caratteri + null terminator
};

Ticker watchdogTicker;
volatile bool watchdogTriggered = false;


static uint8_t tableNumber = 0;  // Valore di default (0-99)
static uint8_t isTableNumberMenu = 0;  // Flag per il submenu del numero del tavolo
static bool tableNumberDirection = true;  // true = incrementa, false = decrementa
unsigned long lastClickTime = 0;  // Per rilevare il doppio click
static uint8_t isPlayersCountMenu = 0;  // Flag per il submenu del numero di giocatori

const char* monitorServerUrl = "http://192.168.1.89:3000/api/status"; // Cambia con l'IP del tuo server
unsigned long lastStatusUpdateTime = 0;
const unsigned long statusUpdateInterval = 3000; // Invia lo stato ogni 3 secondi

static uint8_t playersCount = 10;  // Valore predefinito per il numero di giocatori

void setup()
{
  Serial.begin(115200);
  EEPROM.begin(512);
  Serial.flush();
  Serial.println();
  

  pinMode(ledPin, OUTPUT);
  pinMode(buzzerPin, OUTPUT);
  pinMode(buttonLedPin, OUTPUT);
  pinMode(voltagePin, INPUT); //only works with WeMos ESP8266 ESP-WROOM-02

  //digitalWrite(ledPin, HIGH); //High/Low depends by the board
  //RP2040_led();
  
  SPIFFS.begin();

  diagEEPROM();

  //pixels.setBrightness(255);// doesn't seems to work...
  pixels.begin(); // This initializes the NeoPixel library.
 
  LedPulse(buttonLedPin,ledPower100,100);
 
  clear_module_leds(0);
  delay(10);
  clear_module_leds(1);

  if(digitalRead(buttonPin) == 0) {
    // Tieni premuto il pulsante per 5 secondi per entrare nel menu modalità
    delay(5000);
    if(digitalRead(buttonPin) == 0) {
      Serial.println("Entering operation mode menu...");
      
      // Assicuriamoci di leggere la modalità corrente da EEPROM
      readPokerTimerParams();
      
      isOperationModeMenu = 1;
      previousMillisOperationMode = millis();
      currentMillis = millis();
      
      // Usa temporaryModeValue uguale alla modalità operativa attuale
      temporaryModeValue = operationMode;
      
      // Mostra "OP" seguito dal numero della modalità
      showModeStartup(operationMode);
    }
    else {
      // Non facciamo nulla, poiché abbiamo rimosso il vecchio menu
      Serial.println("Button press too short for operation mode menu.");
    }
  }

  //readPokerLife();
  checkIsDischarging();
  tempVoltageOld = filterVoltage(); //Utilizziamo la funzione di filtraggio

  //writePokerTimerParams();
  readPokerTimerParams();
  temporaryValueTime = pokerTimer1;

  //if(lastVolt > minimumVoltage2 && isTimeMenu == 0 && isOperationModeMenu == 0){
  if(isOperationModeMenu == 0){
    // Mostra l'animazione di avvio
    for (int i = startupAnimations; i >= 0 ; i--)
      show_animation_boot(intervalAnimation);
    
    // Mostra la modalità corrente
    Serial.println("Showing operation mode...");
    showModeStartup(operationMode);
    
    // Avvia il timer in base alla modalità
    Serial.print("Boot PokerTimer set to: ");
    Serial.println(pokerTimer1);
    
    // In tutte le modalità, inizia con il timer fermo
    setTimer(pokerTimer1, 1);  // paused = 1
    isStarted = 0;
    
    isFirstTime = 0;
  }
  
  uint8_t savedWiFiState = EEPROM.read(memAddressWiFiState);
  if(savedWiFiState != 255) {  // 255 è il valore di default in EEPROM non inizializzata
    wifiEnabled = savedWiFiState;
  }
  
  // Se il WiFi è abilitato, lo inizializziamo in modo non bloccante nel loop
  if(wifiEnabled) {
    wifiSetupInProgress = true;
    wifiSetupStartTime = millis();
    // Impostiamo il nome host
    WiFi.hostname(hostname);
  }

  // Prova a caricare un URL server precedentemente salvato
  loadDiscoveredServerUrl();
  
  // Se non abbiamo un URL salvato, esegui subito la discovery
  if (!serverDiscovered) {
    // Tentiamo la discovery del server dopo un breve ritardo
    // per assicurarci che il WiFi sia completamente inizializzato
    delay(1000);
    discoverServer();
  }

  watchdogTicker.attach(5, watchdogCallback);
}




void setupWiFiAsync() {
  // Configurazione WiFi con WiFiManager
  Serial.println("Setting up WiFi (async)...");
  
  // Imposta il nome dell'access point e della password
  wifiManager.setAPStaticIPConfig(IPAddress(192,168,4,1), IPAddress(192,168,4,1), IPAddress(255,255,255,0));
  
  // Crea un nome AP univoco basato sul MAC address
  String uniqueAPName = getUniqueAPName();
  
  wifiManager.setAPCallback([uniqueAPName](WiFiManager *wifiManager) {
    Serial.println("WiFi not configured. Starting config portal...");
    Serial.print("Connect to AP: ");
    Serial.println(uniqueAPName);
  });
  
  // Timeout dopo 3 minuti di configurazione
  wifiManager.setConfigPortalTimeout(180);
  
  // Utilizziamo un metodo asincrono per la connessione
  wifiManager.setConnectTimeout(10);  // 10 secondi di timeout per ogni tentativo
  
  // Tenta di connettersi in modalità non bloccante
  wifiManager.setBreakAfterConfig(true);
  if (WiFi.status() == WL_CONNECTED) {
    // Già connesso
    Serial.println("WiFi already connected");
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());
    wifiSetupInProgress = false;
    initWebServer();
  }
  
  // Imposta il nome host
  WiFi.hostname(hostname);
}

// Funzione per inizializzare il server web
void initWebServer() {
  // Inizializza il server web
  setupWebServer();
  Serial.println("HTTP server started");
  wifiSetupInProgress = false;
}


String getUniqueAPName() {
  uint8_t mac[6];
  WiFi.macAddress(mac);
  
  // Usa gli ultimi 4 byte dell'indirizzo MAC per creare un identificatore univoco
  char apName[20];
  sprintf(apName, "PokerTimer-%02X%02X", mac[4], mac[5]);
  return String(apName);
}


void watchdogCallback() {
  watchdogTriggered = true;
}

void startAPMode() {
  wifiAPMode = true;
  String apName = getUniqueAPName();
  
  Serial.print("Starting AP mode with name: ");
  Serial.println(apName);
  
  // Configura e avvia l'AP
  WiFi.mode(WIFI_AP);
  delay(100);
  
  Serial.println("WiFi mode set to AP");
  
  bool configResult = WiFi.softAPConfig(IPAddress(192,168,4,1), IPAddress(192,168,4,1), IPAddress(255,255,255,0));
  if (!configResult) {
    Serial.println("AP configuration failed");
    return;
  }
  
  Serial.println("AP configured with IP: 192.168.4.1");
  
  bool apStarted = WiFi.softAP(apName.c_str());
  if (apStarted) {
    Serial.println("AP started successfully");
    Serial.print("AP IP address: ");
    Serial.println(WiFi.softAPIP());
    
    // Inizializza il server web con la nuova interfaccia AP
    setupAPWebServer();
  } else {
    Serial.println("Failed to start AP - check hardware");
  }
}


void setupAPWebServer() {
  // Rotta principale con stile migliorato ma leggero
  server.on("/", HTTP_GET, []() {
    String html = "<!DOCTYPE html><html><head><meta name='viewport' content='width=device-width,initial-scale=1'><title>Timer</title>";
    html += "<style>";
    html += "body{font-family:Arial,sans-serif;margin:0;padding:15px;background:#f0f0f0;color:#333}";
    html += "h2{color:#444;margin-top:15px}";
    html += "form{background:white;padding:15px;border-radius:8px;margin-bottom:15px;box-shadow:0 1px 3px rgba(0,0,0,0.1)}";
    html += "input,select{width:100%;padding:8px;margin:5px 0 15px;border:1px solid #ddd;border-radius:4px;box-sizing:border-box}";
    html += "input[type=checkbox]{width:auto;margin-right:8px}";
    html += "label{font-weight:bold}";
    html += ".check{display:flex;align-items:center;margin-bottom:15px}";
    html += ".check label{font-weight:normal}";
    html += "button{background:#4CAF50;color:white;padding:10px;border:none;border-radius:4px;cursor:pointer;width:100%;font-size:16px;margin:5px 0}";
    html += "button:hover{background:#45a049}";
    html += "#scan{background:#007bff}";
    html += "#scan:hover{background:#0069d9}";
    html += "#reset{background:#dc3545;margin-top:10px}";
    html += "#reset:hover{background:#c82333}";
    html += "hr{border:0;height:1px;background:#ddd;margin:15px 0}";
    html += ".networks{border:1px solid #ddd;margin-top:10px;max-height:150px;overflow-y:auto;border-radius:4px}";
    html += ".network{padding:8px;border-bottom:1px solid #eee;cursor:pointer}";
    html += ".network:hover{background:#f5f5f5}";
    html += ".info{font-size:12px;color:#666;margin-top:5px}";
    html += "</style></head><body>";
    
    html += "<h2>Timer Settings</h2>";
    html += "<form action='/save' method='post'>";
    html += "<label for='m'>Operation Mode:</label>";
    html += "<select id='m' name='mode' onchange='t()'>";
    html += "<option value='1'>Mode 1: T1/T2 with automatic start</option>";
    html += "<option value='2'>Mode 2: T1/T2 with manual start</option>";
    html += "<option value='3'>Mode 3: T1 only with automatic start</option>";
    html += "<option value='4'>Mode 4: T1 only with manual start</option>";
    html += "</select>";
    
    html += "<label for='t1'>T1 Value (seconds):</label>";
    html += "<input type='number' id='t1' name='t1' value='20' min='5' max='95' step='5'>";
    
    html += "<div id='t2'>";
    html += "<label for='t2v'>T2 Value (seconds):</label>";
    html += "<input type='number' id='t2v' name='t2' value='30' min='5' max='95' step='5'>";
    html += "</div>";
    
    html += "<label for='tn'>Table Number (0-99):</label>";
    html += "<input type='number' id='tn' name='tableNumber' value='1' min='0' max='99'>";
    
    html += "<div class='check'>";
    html += "<input type='checkbox' id='bz' name='buzzer' value='1' checked>";
    html += "<label for='bz'>Buzzer Enabled</label>";
    html += "</div>";
    
    // Aggiunto info batteria
    html += "<div class='info'>Battery Voltage: " + String(lastVolt, 2) + "V (" + String(lastPercent) + "%)</div>";
    
    html += "<button type='submit'>Save Timer Settings</button>";
    html += "</form>";
    
    html += "<h2>WiFi Setup</h2>";
    html += "<form action='/save-wifi' method='post'>";
    html += "<label for='s'>Network Name (SSID):</label>";
    html += "<input type='text' id='s' name='ssid' required>";
    
    html += "<label for='p'>Password:</label>";
    html += "<input type='password' id='p' name='password'>";
    
    html += "<div class='check'>";
    html += "<input type='checkbox' id='sp' onclick='p.type=p.type==\"password\"?\"text\":\"password\"'>";
    html += "<label for='sp'>Show password</label>";
    html += "</div>";
    
    // Aggiunto info segnale WiFi
    html += "<div class='info'>WiFi Signal: " + String(WiFi.RSSI()) + " dBm</div>";
    
    html += "<button type='button' id='scan' onclick='w()'>Scan Networks</button>";
    html += "<div class='networks' id='n'></div>";
    html += "<button type='submit'>Connect to WiFi</button>";
    html += "</form>";
    
    html += "<button id='reset' onclick='if(confirm(\"Reset all settings to factory defaults?\"))location=\"/reset\"'>Factory Reset</button>";
    
    html += "<script>";
    html += "function t(){document.getElementById('t2').style.display=['1','2'].includes(document.getElementById('m').value)?'block':'none'}";
    html += "function w(){document.getElementById('n').innerHTML='<p style=\"text-align:center\">Scanning...</p>';";
    html += "var x=new XMLHttpRequest();x.open('GET','/scan');";
    html += "x.onload=function(){if(x.status===200){var d=JSON.parse(x.responseText);var h='';";
    html += "if(d.n&&d.n.length){for(var i=0;i<d.n.length;i++){h+='<div class=\"network\" onclick=\"document.getElementById(\\'s\\').value=\\''+d.n[i]+'\\'\">'+d.n[i]+'</div>';}}";
    html += "else{h='<p style=\"text-align:center\">No networks found</p>'}document.getElementById('n').innerHTML=h;}};x.send();}";
    html += "window.onload=t;";
    html += "</script></body></html>";
    
    server.send(200, "text/html", html);
  });

  // Rotte invariate
  server.on("/scan", HTTP_GET, []() {
    int n = WiFi.scanNetworks();
    String json = "{\"n\":[";
    if (n > 0) {
      for (int i = 0; i < n; i++) {
        if (i > 0) json += ",";
        json += "\"" + WiFi.SSID(i) + "\"";
      }
    }
    json += "]}";
    server.send(200, "application/json", json);
  });

  // Rotta per factory reset 
  server.on("/reset", HTTP_GET, []() {
    server.send(200, "text/html", "<html><body><h3>Factory Reset...</h3></body></html>");
    delay(500);
    performFactoryReset(); // Usa la stessa funzione di setupWebServer
  });

  // Salva impostazioni
  server.on("/save", HTTP_POST, []() {
    if (server.hasArg("mode")) operationMode = constrain(server.arg("mode").toInt(), 1, 4);
    if (server.hasArg("t1")) pokerTimer1 = constrain(server.arg("t1").toInt(), 5, 95);
    if (server.hasArg("t2")) pokerTimer2 = constrain(server.arg("t2").toInt(), 5, 95);
    if (server.hasArg("tableNumber")) tableNumber = constrain(server.arg("tableNumber").toInt(), 0, 99);
    buzzerOnOff = server.hasArg("buzzer") ? 1 : 0;
    
    writePokerTimerParams();
      // Emetti un suono di conferma
    //IRENE
    if (buzzerOnOff) {
      tone(buzzerPin, 1000);
      delay(100);
      noTone(buzzerPin);
      delay(50);
      tone(buzzerPin, 1200);
      delay(100);
      noTone(buzzerPin);
    }
    if (!isStarted || timeExpired) setTimer(pokerTimer1, 1);
    
    server.sendHeader("Location", "/", true);
    server.send(302, "text/plain", "");
  });

  // Salva WiFi
  server.on("/save-wifi", HTTP_POST, []() {
    String ssid = server.arg("ssid");
    if (ssid.length() > 0) {
      saveWiFiCredentials(ssid.c_str(), server.arg("password").c_str());
      
      String html = "<html><head><style>body{font-family:Arial;text-align:center;margin:20px}</style></head>";
      html += "<body><h3>Connecting to " + ssid + "...</h3><p>Device will restart</p></body></html>";
      server.send(200, "text/html", html);
      delay(1000);
      ESP.restart();
    } else {
      server.sendHeader("Location", "/", true);
      server.send(302, "text/plain", "");
    }
  });

  // Pagine non trovate
  server.onNotFound([]() {
    server.sendHeader("Location", "/", true);
    server.send(302, "text/plain", "");
  });

  server.begin();
  Serial.println("AP web server started (styled)");
}

void setupCaptivePortal() {
  // Gestione di tutte le richieste DNS non riconosciute verso la nostra pagina
  server.onNotFound([]() {
    // Reindirizza alla pagina principale
    server.sendHeader("Location", String("http://") + WiFi.softAPIP().toString(), true);
    server.send(302, "text/plain", "");
  });
  
  // Risponde alle richieste /generate_204 e simili usate per il rilevamento captive portal
  server.on("/generate_204", HTTP_GET, []() {
    server.sendHeader("Location", String("http://") + WiFi.softAPIP().toString(), true);
    server.send(302, "text/plain", "");
  });
  
  server.on("/fwlink", HTTP_GET, []() {
    server.sendHeader("Location", String("http://") + WiFi.softAPIP().toString(), true);
    server.send(302, "text/plain", "");
  });
  
  // Risponde a richieste di Apple CaptiveNetwork Support
  server.on("/hotspot-detect.html", HTTP_GET, []() {
    server.sendHeader("Location", String("http://") + WiFi.softAPIP().toString(), true);
    server.send(302, "text/plain", "");
  });
}


// Funzione per configurare le pagine di configurazione WiFi
// Funzione per configurare le pagine di configurazione WiFi
void setupWiFiConfigPage() {
  // Pagina per configurare il WiFi
  server.on("/wifi", HTTP_GET, []() {
    String html = R"rawliteral(
<!DOCTYPE html>
<html>
<head>
  <title>WiFi Configuration</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    body {
      font-family: Arial, sans-serif;
      margin: 20px;
      background-color: #f5f5f5;
    }
    h1 {
      color: #333;
    }
    form {
      background: white;
      padding: 20px;
      border-radius: 8px;
      box-shadow: 0 2px 10px rgba(0,0,0,0.1);
      max-width: 500px;
      margin: 0 auto;
    }
    label {
      display: block;
      margin-top: 10px;
      font-weight: bold;
    }
    input[type=text], input[type=password] {
      width: 100%;
      padding: 10px;
      margin: 5px 0 15px;
      border: 1px solid #ddd;
      border-radius: 4px;
      box-sizing: border-box;
    }
    input[type=submit] {
      background-color: #4CAF50;
      color: white;
      padding: 10px 15px;
      border: none;
      border-radius: 4px;
      cursor: pointer;
      font-size: 16px;
    }
    input[type=submit]:hover {
      background-color: #45a049;
    }
    .back {
      display: block;
      margin-top: 20px;
      text-align: center;
      color: #0066cc;
      text-decoration: none;
    }
    .scan-result {
      margin-top: 10px;
      background: #f9f9f9;
      border: 1px solid #ddd;
      padding: 10px;
      border-radius: 4px;
      max-height: 200px;
      overflow-y: auto;
    }
    .network {
      padding: 5px;
      cursor: pointer;
    }
    .network:hover {
      background-color: #eee;
    }
    .button-container {
      margin-top: 20px;
      text-align: center;
    }
    .button-container a {
      display: inline-block;
      margin: 0 10px;
      padding: 10px 15px;
      background-color: #4CAF50;
      color: white;
      text-decoration: none;
      border-radius: 4px;
    }
    .button-container a.danger {
      background-color: #dc3545;
    }
    .button-container a:hover {
      opacity: 0.9;
    }
  </style>
</head>
<body>
  <h1>WiFi Configuration</h1>
  
  <form method='POST' action='/savewifi'>
    <label for="ssid">Network Name (SSID):</label>
    <input type="text" id="ssid" name="ssid" required>
    
    <label for="password">Password:</label>
    <input type="password" id="password" name="password">
    
    <input type="submit" value="Connect">
  </form>

  <div class="button-container">
    <a href="/" class="back">Back to Main Page</a>
    <a href="/resetwifi" class="danger">Reset WiFi Settings</a>
  </div>
  
  <div class="scan-result" id="scan-results">
    <p>Scanning for networks...</p>
  </div>
  
  <script>
    // Funzione per scansionare le reti WiFi
    function scanNetworks() {
      fetch('/scanwifi')
        .then(response => response.json())
        .then(data => {
          const resultsDiv = document.getElementById('scan-results');
          if (data.networks && data.networks.length > 0) {
            let html = '<p>Available Networks:</p>';
            data.networks.forEach(network => {
              html += `<div class="network" onclick="selectNetwork('${network}')">${network}</div>`;
            });
            resultsDiv.innerHTML = html;
          } else {
            resultsDiv.innerHTML = '<p>No networks found or scan failed</p>';
          }
        })
        .catch(error => {
          console.error('Error scanning networks:', error);
          document.getElementById('scan-results').innerHTML = '<p>Error scanning networks</p>';
        });
    }
    
    // Funzione per selezionare una rete
    function selectNetwork(ssid) {
      document.getElementById('ssid').value = ssid;
    }
    
    // Avvia la scansione quando la pagina si carica
    window.onload = scanNetworks;
  </script>
</body>
</html>
    )rawliteral";
    server.send(200, "text/html", html);
  });
  
  // Endpoint per scannerizzare le reti WiFi disponibili
  server.on("/scanwifi", HTTP_GET, []() {
    String json = "{\"networks\":[";
    int n = WiFi.scanNetworks();
    
    if (n > 0) {
      for (int i = 0; i < n; ++i) {
        if (i > 0) json += ",";
        json += "\"" + WiFi.SSID(i) + "\"";
      }
    }
    
    json += "]}";
    server.send(200, "application/json", json);
  });
  
  // Endpoint per salvare le credenziali WiFi
  server.on("/savewifi", HTTP_POST, []() {
    String ssid = server.arg("ssid");
    String password = server.arg("password");
    
    if (ssid.length() > 0) {
      // Salva le credenziali e riavvia
      saveWiFiCredentials(ssid.c_str(), password.c_str());
      
      String html = R"rawliteral(
<!DOCTYPE html>
<html>
<head>
  <title>WiFi Configuration</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta http-equiv="refresh" content="5;url=/">
  <style>
    body {
      font-family: Arial, sans-serif;
      margin: 20px;
      text-align: center;
    }
    .message {
      padding: 20px;
      background-color: #f0f8ff;
      border: 1px solid #b0c4de;
      border-radius: 8px;
      margin: 30px auto;
      max-width: 400px;
    }
    .spinner {
      border: 4px solid #f3f3f3;
      border-top: 4px solid #3498db;
      border-radius: 50%;
      width: 30px;
      height: 30px;
      animation: spin 2s linear infinite;
      margin: 20px auto;
    }
    @keyframes spin {
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }
  </style>
</head>
<body>
  <div class="message">
    <h2>WiFi Configuration Saved</h2>
    <p>Connecting to <strong>)rawliteral" + ssid + R"rawliteral(</strong>...</p>
    <div class="spinner"></div>
    <p>The device will restart in 5 seconds.</p>
  </div>
  <script>
    // Riavvia la pagina dopo 5 secondi
    setTimeout(function() {
      window.location.href = "/";
    }, 5000);
  </script>
</body>
</html>
      )rawliteral";
      
      server.send(200, "text/html", html);
      
      // Programma il riavvio dopo aver inviato la risposta
      delay(500);
      ESP.restart();
    } else {
      server.sendHeader("Location", "/wifi", true);
      server.send(302, "text/plain", "");
    }
  });

  // Endpoint per resettare le impostazioni WiFi
  server.on("/resetwifi", HTTP_GET, []() {
    // Reset delle impostazioni WiFi
    wifiManager.resetSettings();
    deleteWiFiCredentials();
    
    String html = R"rawliteral(
<!DOCTYPE html>
<html>
<head>
  <title>WiFi Reset</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta http-equiv="refresh" content="5;url=/">
  <style>
    body {
      font-family: Arial, sans-serif;
      margin: 20px;
      text-align: center;
    }
    .message {
      padding: 20px;
      background-color: #f8d7da;
      border: 1px solid #f5c6cb;
      border-radius: 8px;
      margin: 30px auto;
      max-width: 400px;
      color: #721c24;
    }
  </style>
</head>
<body>
  <div class="message">
    <h2>WiFi Settings Reset</h2>
    <p>All WiFi settings have been reset.</p>
    <p>The device will restart in 5 seconds.</p>
  </div>
  <script>
    // Riavvia la pagina dopo 5 secondi
    setTimeout(function() {
      window.location.href = "/";
    }, 5000);
  </script>
</body>
</html>
    )rawliteral";
    
    server.send(200, "text/html", html);
    
    // Programma il riavvio dopo aver inviato la risposta
    delay(500);
    ESP.restart();
  });
}


void performFactoryReset() {
  Serial.println("Esecuzione factory reset...");
  
  // Cancella SPIFFS (aggiunto)
  SPIFFS.format();
  
  // Cancella completamente le credenziali WiFi (aggiunto)
  WiFi.disconnect(true);
  
  // Ripristina i valori di default
  operationMode = OPERATION_MODE_1;
  pokerTimer1 = timerSet_20;
  pokerTimer2 = timerSet_30;
  buzzerOnOff = 1;
  tableNumber = 0;  // Reset del numero del tavolo a 0
  playersCount = 10; // Reset del numero di giocatori a 10
  
  // Salva i valori di default in EEPROM
  writePokerTimerParams();
  
  // Reset delle impostazioni WiFi
  wifiManager.resetSettings();
  
  // Mostra conferma su display
  for(int i = 0; i < LED_MODULES; i++) {
    clear_module_leds(i);
  }
  
  // Mostra "Fr" (Factory Reset)
  //"F"      
  pixels.setPixelColor(0, pixels.Color(255,0,255));  //B  A  C
  pixels.setPixelColor(1, pixels.Color(0,255,0));    //E  D  F
  pixels.setPixelColor(2, pixels.Color(255,0,255)); //DP  G  NC
  //"r"
  pixels.setPixelColor(3, pixels.Color(255,255,255));  //B  A  C
  pixels.setPixelColor(4, pixels.Color(0,255,255)); //E  D  F
  pixels.setPixelColor(5, pixels.Color(255,0,255)); //DP  G  NC
  pixels.show();
  
  // Avvisa l'utente con un suono distintivo
  for (int i = 0; i < 3; i++) {
    tone(buzzerPin, 2000);
    delay(200);
    noTone(buzzerPin);
    delay(100);
  }
  
  delay(2000); // Mostra "Fr" per 2 secondi
  
  // Riavvia il dispositivo
  ESP.restart();
}

void showPlayersMode() {
  for(int i = 0; i < LED_MODULES; i++) {
    clear_module_leds(i);
  }
  
  // "P" sul primo digit (simile alla P maiuscola)
  pixels.setPixelColor(0, pixels.Color(0,0,255));  //B  A  C
  pixels.setPixelColor(1, pixels.Color(0,255,0));  //E  D  F
  pixels.setPixelColor(2, pixels.Color(255,0,255)); //DP  G  NC
  
  //  "L" sul primo digit (simile alla L maiuscola)
  pixels.setPixelColor(3, pixels.Color(255,255,255));  //B  A  C
  pixels.setPixelColor(4, pixels.Color(0,0,0));  //E  D  F
  pixels.setPixelColor(5, pixels.Color(255,255,255));  //DP  G  NC
  pixels.show();
}

// Funzione dedicata a mostrare "OP" e il numero della modalità
void showModeStartup(uint8_t mode) {
  // Prima pulisci completamente il display
  for(int i = 0; i < LED_MODULES; i++) {
    clear_module_leds(i);
  }
  delay(100);
  
  // Mostra "OP" direttamente per le modalità 1-4
  // Mostra "b" per la modalità buzzer
  if (mode == OPERATION_MODE_BUZZER) {
    // Mostra "b" sul display
    // "b" sul primo digit (simile a "b" minuscola)
    pixels.setPixelColor(0, pixels.Color(255,255,0));  // B A C
    pixels.setPixelColor(1, pixels.Color(0,0,0));  // E D F
    pixels.setPixelColor(2, pixels.Color(255,0,255));  // DP G NC
    
    // Secondo digit spento
    pixels.setPixelColor(3, pixels.Color(255,255,255));  // B A C
    pixels.setPixelColor(4, pixels.Color(255,255,255));  // E D F
    pixels.setPixelColor(5, pixels.Color(255,255,255));  // DP G NC
    pixels.show();
    
    // Attendi 2 secondi
    delay(2000);
    
    // Ora mostra lo stato attuale del buzzer (0 o 1)
    buzzerOnOffScreen(buzzerOnOff);
  } else {
    // Per le modalità normali, mostra "OP"
    // "O" sul primo digit
    pixels.setPixelColor(0, pixels.Color(0,0,0));  // B A C
    pixels.setPixelColor(1, pixels.Color(0,0,0));  // E D F
    pixels.setPixelColor(2, pixels.Color(255,255,255));  // DP G NC
    // "P" sul secondo digit
    pixels.setPixelColor(3, pixels.Color(0,0,255));  // B A C
    pixels.setPixelColor(4, pixels.Color(0,255,0));  // E D F
    pixels.setPixelColor(5, pixels.Color(255,0,255));  // DP G NC
    pixels.show();
    
    // Aspetta 2 secondi per mostrare "OP"
    delay(2000);
    
    // Pulisci nuovamente il display per il numero
    for(int i = 0; i < LED_MODULES; i++) {
      clear_module_leds(i);
    }
    delay(100);
    
    // Mostra il numero della modalità
    show_char_noob(mode);
  }
  
  // Aspetta 2 secondi
  delay(2000);
}

void operationModeScreen(uint8_t mode) {
  for(int i = 0; i <= LED_MODULES; i++) {
    clear_module_leds(i);
  }
  
  // Mostra "OP" (OPeration mode)
  // "O" sul primo digit
  pixels.setPixelColor(0, pixels.Color(0,0,0));  // B A C
  pixels.setPixelColor(1, pixels.Color(0,0,0));  // E D F
  pixels.setPixelColor(2, pixels.Color(255,255,255));  // DP G NC
  
  // "P" sul secondo digit (simile a "P")
  pixels.setPixelColor(3, pixels.Color(0,0,255));  // B A C
  pixels.setPixelColor(4, pixels.Color(0,255,0));  // E D F
  pixels.setPixelColor(5, pixels.Color(255,0,255));  // DP G NC
  
  pixels.show();
  // Rimuoviamo il delay da qui
}


void wifiStatusScreen(uint8_t enabled) {
  for(int i = 0; i < LED_MODULES; i++) {
    clear_module_leds(i);
  }
  
  // Mostra "n" o "y" per lo stato WiFi (no/yes)

  if(enabled){
    pixels.setPixelColor(3, pixels.Color(0,255,0));  //B  A  C
    pixels.setPixelColor(4, pixels.Color(255,255,255));  //E  D  F
    pixels.setPixelColor(5, pixels.Color(255,255,255));  //DP  G  NC
  }
  else{
    pixels.setPixelColor(3, pixels.Color(0,0,0));  //B  A  C
    pixels.setPixelColor(4, pixels.Color(0,0,0));  //E  D  F
    pixels.setPixelColor(5, pixels.Color(0,255,0));  //DP  G  NC
  }

    pixels.setPixelColor(0, pixels.Color(255,255,255));
    pixels.setPixelColor(1, pixels.Color(255,255,255)); 
    pixels.setPixelColor(2, pixels.Color(255,255,255));
  
    pixels.show();
}

void showWiFiMode() {
  for(int i = 0; i < LED_MODULES; i++) {
    clear_module_leds(i);
  }
  
  // "W" sul primo digit
  pixels.setPixelColor(0, pixels.Color(0,255,255));  // B A C
  pixels.setPixelColor(1, pixels.Color(255,0,0));  // E D F
  pixels.setPixelColor(2, pixels.Color(255,0,255));  // DP G NC
  
  // "F" sul secondo digit
  pixels.setPixelColor(3, pixels.Color(255,0,255));  // B A C
  pixels.setPixelColor(4, pixels.Color(0,255,0));    // E D F
  pixels.setPixelColor(5, pixels.Color(255,0,255));  // DP G NC
  
  pixels.show();
}

// Funzione per mostrare "b" (modalità buzzer) sul display
void showBuzzerMode() {
  for(int i = 0; i < LED_MODULES; i++) {
    clear_module_leds(i);
  }
  
  // "b" sul primo digit (simile a "b" minuscola)
  pixels.setPixelColor(0, pixels.Color(255,255,0));  // B A C
  pixels.setPixelColor(1, pixels.Color(0,0,0));  // E D F
  pixels.setPixelColor(2, pixels.Color(255,0,255));  // DP G NC
  
  // Secondo digit spento
  pixels.setPixelColor(3, pixels.Color(255,255,255));  // B A C
  pixels.setPixelColor(4, pixels.Color(255,255,255));  // E D F
  pixels.setPixelColor(5, pixels.Color(255,255,255));  // DP G NC
  pixels.show();
}


void showT1Mode() {
  for(int i = 0; i < LED_MODULES; i++) {
    clear_module_leds(i);
  }
  
  // "t" sul primo digit
  pixels.setPixelColor(0, pixels.Color(255,255,255));  //B  A  C
  pixels.setPixelColor(1, pixels.Color(0,0,0));  //E  D  F
  pixels.setPixelColor(2, pixels.Color(255,0,255));  //DP  G  NC
  
  // "1" sul secondo digit
  pixels.setPixelColor(3, pixels.Color(0,255,0));  //B  A  C
  pixels.setPixelColor(4, pixels.Color(255,255,255));  //E  D  F
  pixels.setPixelColor(5, pixels.Color(255,255,255));  //DP  G  NC
  pixels.show();
}

void showT2Mode() {
  for(int i = 0; i < LED_MODULES; i++) {
    clear_module_leds(i);
  }
  
  // "t" sul primo digit
  pixels.setPixelColor(0, pixels.Color(255,255,255));  //B  A  C
  pixels.setPixelColor(1, pixels.Color(0,0,0));  //E  D  F
  pixels.setPixelColor(2, pixels.Color(255,0,255));  //DP  G  NC
  
  // "2" sul secondo digit
  pixels.setPixelColor(3, pixels.Color(0,0,255));  //B  A  C
  pixels.setPixelColor(4, pixels.Color(0,0,255));  //E  D  F
  pixels.setPixelColor(5, pixels.Color(255,0,255));  //DP  G  NC
  pixels.show();
}


void report_button(const uint8_t state, const char* const label = NULL) {
    switch (state) {
        case SINGLE_PRESS_SHORT:
          Serial.println(F("Single click and release"));
          
          // Nel menu modalità o submenu
          if(isOperationModeMenu == 1) {
            // Se siamo nel submenu del numero del tavolo
            if(isTableNumberMenu == 1) {
              // Click singolo - incrementa o decrementa in base alla direzione corrente
              if (tableNumberDirection) {
                tableNumber++;
                if (tableNumber > 99) tableNumber = 0; // Loop back se supera 99
              } else {
                tableNumber--;
                if (tableNumber < 0) tableNumber = 99; // Loop back se va sotto 1
              }
              
              Serial.print("Set Table Number to: ");
              Serial.println(tableNumber);
              show_char_noob(tableNumber);
              
              // Reset del timer per il timeout
              previousMillisExitOperationMode = currentMillis;
            } 
            // Se siamo nel submenu del numero di giocatori
            else if(isPlayersCountMenu == 1) {
              // Incrementa il numero di giocatori e limita il range (1-10)
              playersCount++;
              if (playersCount > 10) playersCount = 1; // Loop back da 10 a 1
              
              Serial.print("Set Players Count to: ");
              Serial.println(playersCount);
              show_char_noob(playersCount);
              
              // Reset del timer per il timeout
              previousMillisExitOperationMode = currentMillis;
            }
            // Se siamo nel submenu del buzzer
            else if(isBuzzerMenu == 1) {
              // Toggle stato buzzer
              buzzerOnOff = !buzzerOnOff;
              Serial.print("Buzzer toggled to: ");
              Serial.println(buzzerOnOff);
              buzzerOnOffScreen(buzzerOnOff);
              previousMillisExitOperationMode = currentMillis;
            } 
            // Se siamo nel submenu di T1
            else if(isTime1MenuSet == 1) {
              pokerTimer1 = ((pokerTimer1 + pokerTimerIncrement) % 100) == 0 ? 5 : ((pokerTimer1 + pokerTimerIncrement) % 100);
              temporaryValueTime = pokerTimer1;
              Serial.print("Set PokerTime1 to: ");
              Serial.println(pokerTimer1);
              show_char_noob(pokerTimer1);
              previousMillisExitOperationMode = currentMillis;
            }
            // Se siamo nel submenu di T2
            else if(isTime2MenuSet == 1) {
              pokerTimer2 = ((pokerTimer2 + pokerTimerIncrement) % 100) == 0 ? 5 : ((pokerTimer2 + pokerTimerIncrement) % 100);
              temporaryValueTime = pokerTimer2;
              Serial.print("Set PokerTime2 to: ");
              Serial.println(pokerTimer2);
              show_char_noob(pokerTimer2);
              previousMillisExitOperationMode = currentMillis;
            } 
            // Se siamo nel submenu WiFi
            else if(isWiFiMenu == 1) {
              // Salva lo stato precedente per confronto
              bool prevWiFiState = wifiEnabled;
              
              // Toggle stato WiFi
              wifiEnabled = !wifiEnabled;
              Serial.print("WiFi toggled to: ");
              Serial.println(wifiEnabled ? "ON" : "OFF");
              wifiStatusScreen(wifiEnabled);
              previousMillisExitOperationMode = currentMillis;
              
              // Imposta il flag se lo stato è cambiato
              if (prevWiFiState != wifiEnabled) {
                wifiStateWasChanged = true;
              }
            }
            // Se siamo nel menu principale delle modalità
            else {
              // Cicla tra le modalità disponibili
              temporaryModeValue = (temporaryModeValue % 10) + 1;  // Cicla tra 1-10 (aggiunto Players)
              Serial.print("Operation mode changed to: ");
              if(temporaryModeValue == OPERATION_MODE_TABLE) {
                Serial.println("Table Number Mode");
                showTableNumberScreen(); // Mostra "T"
              }
              else if(temporaryModeValue == OPERATION_MODE_PLAYERS) {
                Serial.println("Players Count Mode");
                showPlayersMode(); // Mostra "P"
              }
              else if(temporaryModeValue == OPERATION_MODE_BUZZER) {
                Serial.println("Buzzer Mode");
                showBuzzerMode(); // Mostra solo "b"
              } 
              else if(temporaryModeValue == OPERATION_MODE_T1) {
                Serial.println("T1 Configuration");
                showT1Mode(); // Mostra "t1"
              }
              else if(temporaryModeValue == OPERATION_MODE_T2) {
                Serial.println("T2 Configuration");
                showT2Mode(); // Mostra "t2"
              }
              else if(temporaryModeValue == OPERATION_MODE_WIFI) {
                Serial.println("WiFi Configuration");
                showWiFiMode(); // Mostra "nF"
              }
              else {
                Serial.println(temporaryModeValue);
                show_char_noob(temporaryModeValue);
              }
              previousMillisExitOperationMode = currentMillis;
            }
          }
          
          // Nella normale operazione del timer
          if(isBuzzerMenu == 0 && isTime1MenuSet == 0 && isTime2MenuSet == 0 && isWiFiMenu == 0 && isTableNumberMenu == 0 && isPlayersCountMenu == 0 && isOperationModeMenu == 0)
            SinglePress();

        break;
        
        case SINGLE_PRESS_LONG:  
          LongPressStart();
          Serial.println(F("Single click and hold"));      
        break;

        case DOUBLE_PRESS_SHORT:
          if(isOperationModeMenu == 1) {
            // Se siamo nel submenu del numero del tavolo
            if(isTableNumberMenu == 1) {
              // Doppio click - cambia solo la direzione senza uscire dal menu
              tableNumberDirection = !tableNumberDirection;
              Serial.print("Table number direction changed to: ");
              Serial.println(tableNumberDirection ? "incrementing" : "decrementing");
              
              // Reset del timer per il timeout
              previousMillisExitOperationMode = currentMillis;
            } 
            // Se siamo nel submenu del numero di giocatori
            else if(isPlayersCountMenu == 1) {
              // Salva il valore ed esci
              writePokerTimerParams();
              Serial.print("Players count saved: ");
              Serial.println(playersCount);
              isPlayersCountMenu = 0;
              isOperationModeMenu = 0;
              setTimer(pokerTimer1, 1);  // Resetta a T1
            }
            // Se siamo nel submenu del buzzer
            else if(isBuzzerMenu == 1) {
              // Salva lo stato del buzzer ed esci
              writePokerTimerParams();
              Serial.print("Buzzer state saved: ");
              Serial.println(buzzerOnOff ? "ON" : "OFF");
              isBuzzerMenu = 0;
              isOperationModeMenu = 0;
              setTimer(pokerTimer1, 1);  // Resetta a T1
            } 
            // Se siamo nel submenu di T1
            else if(isTime1MenuSet == 1) {
              // Salva il valore di T1 ed esci
              writePokerTimerParams();
              Serial.print("T1 value saved: ");
              Serial.println(pokerTimer1);
              isTime1MenuSet = 0;
              isOperationModeMenu = 0;
              setTimer(pokerTimer1, 1);  // Resetta a T1
            }
            // Se siamo nel submenu di T2
            else if(isTime2MenuSet == 1) {
              // Salva il valore di T2 ed esci
              writePokerTimerParams();
              Serial.print("T2 value saved: ");
              Serial.println(pokerTimer2);
              isTime2MenuSet = 0;
              isOperationModeMenu = 0;
              setTimer(pokerTimer1, 1);  // Resetta a T1
            }
            // Se siamo nel submenu WiFi
            else if(isWiFiMenu == 1) {
              // Salva lo stato del WiFi ed esci
              EEPROM.write(memAddressWiFiState, wifiEnabled);
              EEPROM.commit();
              Serial.print("WiFi state saved: ");
              Serial.println(wifiEnabled ? "ON" : "OFF");
              isWiFiMenu = 0;
              isOperationModeMenu = 0;
              
              // Se lo stato WiFi è cambiato, forza un reset
              if (wifiStateWasChanged) {
                Serial.println("WiFi state changed - forcing crash reset...");
                forceCrashReset();  // Usa la funzione di crash reset
              } else {
                setTimer(pokerTimer1, 1);  // Resetta a T1
              }
            }
            // Se siamo nel menu principale delle modalità
            else {
              // Se si seleziona una delle opzioni di configurazione, entra nel submenu
              if(temporaryModeValue == OPERATION_MODE_TABLE) {
                Serial.println("Entering table number submenu...");
                isTableNumberMenu = 1;
                tableNumberDirection = true;
                previousMillisExitOperationMode = currentMillis;
                show_char_noob(tableNumber);
              }
              else if(temporaryModeValue == OPERATION_MODE_PLAYERS) {
                Serial.println("Entering players count submenu...");
                isPlayersCountMenu = 1;
                previousMillisExitOperationMode = currentMillis;
                show_char_noob(playersCount);
              }
              else if(temporaryModeValue == OPERATION_MODE_BUZZER) {
                Serial.println("Entering buzzer submenu...");
                isBuzzerMenu = 1;
                previousMillisExitOperationMode = currentMillis;
                buzzerOnOffScreen(buzzerOnOff);
              } 
              else if(temporaryModeValue == OPERATION_MODE_T1) {
                Serial.println("Entering T1 submenu...");
                isTime1MenuSet = 1;
                temporaryValueTime = pokerTimer1;
                previousMillisExitOperationMode = currentMillis;
                show_char_noob(pokerTimer1);
              }
              else if(temporaryModeValue == OPERATION_MODE_T2) {
                Serial.println("Entering T2 submenu...");
                isTime2MenuSet = 1;
                temporaryValueTime = pokerTimer2;
                previousMillisExitOperationMode = currentMillis;
                show_char_noob(pokerTimer2);
              }
              else if(temporaryModeValue == OPERATION_MODE_WIFI) {
                Serial.println("Entering WiFi submenu...");
                isWiFiMenu = 1;
                previousMillisExitOperationMode = currentMillis;
                wifiStatusScreen(wifiEnabled);
              }
              // Altrimenti, salva la modalità normale e esci
              else {
                // Controlla se stiamo cambiando modalità
                bool modeChanged = (operationMode != temporaryModeValue);
                // Salva la nuova modalità
                operationMode = temporaryModeValue;
                writePokerTimerParams();
                isOperationModeMenu = 0;
                
                // Se il WiFi è stato modificato E stiamo cambiando modalità operativa, forza reset
                if (modeChanged && wifiStateWasChanged) {
                  Serial.println("Mode changed and WiFi state changed - forcing crash reset...");
                  forceCrashReset();
                } else {
                  setTimer(pokerTimer1, 1);  // Resetta a T1
                  wifiStateWasChanged = false; // Reset del flag se non riavviamo
                }
              }
            }
          } else {
            DoublePress();
          }
          Serial.println(F("Double click and release"));  
          break;

        case DOUBLE_PRESS_LONG:  
          Serial.print(F("Double click and hold"));      
        break;

        case TRIPLE_PRESS_SHORT:
          Serial.println(F("Triple click and release"));
        break;
          
        case NOT_PRESSED:
        default:
            return;
    }

    if (nullptr != label) {
        Serial.print(F(" on "));
        Serial.print(label);
    }

    Serial.println();
}


void loop()
{
  // Resetta il watchdog all'inizio di ogni ciclo del loop
  watchdogTriggered = false;
  
  // Controlla se il watchdog è scattato (improbabile qui, ma per sicurezza)
  if (watchdogTriggered) {
    Serial.println("Watchdog triggered - restarting");
    ESP.restart();
  }
  
  currentMillis = millis();
  
  // Gestisci il DNS server per il captive portal con protezione
  if (wifiEnabled && wifiSetupInProgress) {
    handleWiFiSetup();
  }
  
  // Gestisci il WiFi in modo completamente non bloccante
  if(wifiEnabled && wifiSetupInProgress) {
    handleWiFiSetup();
  }
  
  // Controllo per factory reset (15 secondi di pressione)
  if (digitalRead(buttonPin) == 0) {  // Pulsante premuto
    if (buttonPressStartTime == 0) {
      buttonPressStartTime = currentMillis;
    } 
    else if (!isLongFactoryResetPress && currentMillis - buttonPressStartTime >= FACTORY_RESET_PRESS_TIME) {
      isLongFactoryResetPress = true;
      performFactoryReset();
    }
  } 
  else {
    // Il pulsante è stato rilasciato
    buttonPressStartTime = 0;
    isLongFactoryResetPress = false;
  }
  
  // Menu per la selezione della modalità operativa
  if(isOperationModeMenu == 1) {
    report_button(button.check_button(), "Action on button 1");
    
    // Se siamo nel submenu del numero del tavolo
    if(isTableNumberMenu == 1) {
      // Timeout per tornare al menu principale
      if(currentMillis - previousMillisExitOperationMode >= timeTimeMenu) {
        Serial.println("Returning to main mode menu...");
        isTableNumberMenu = 0;
        previousMillisExitOperationMode = currentMillis;
      }
      
      // Mostra il valore attuale del numero del tavolo
      if(currentMillis - previousMillisPulseTime >= interval) {
        previousMillisPulseTime = currentMillis;
        show_char_noob(tableNumber);
      }
    }
    // Se siamo nel submenu del numero di giocatori
    else if(isPlayersCountMenu == 1) {
      // Timeout per tornare al menu principale
      if(currentMillis - previousMillisExitOperationMode >= timeTimeMenu) {
        Serial.println("Returning to main mode menu...");
        isPlayersCountMenu = 0;
        previousMillisExitOperationMode = currentMillis;
      }
      
      // Mostra il valore attuale del numero di giocatori
      if(currentMillis - previousMillisPulseTime >= interval) {
        previousMillisPulseTime = currentMillis;
        show_char_noob(playersCount);
      }
    }
    // Se siamo nel submenu del buzzer
    else if(isBuzzerMenu == 1) {
      // Timeout per tornare al menu principale
      if(currentMillis - previousMillisExitOperationMode >= timeTimeMenu) {
        Serial.println("Returning to main mode menu...");
        isBuzzerMenu = 0;
        previousMillisExitOperationMode = currentMillis;
      }
      
      // Mostra lo stato attuale del buzzer
      if(currentMillis - previousMillisPulseTime >= interval) {
        previousMillisPulseTime = currentMillis;
        buzzerOnOffScreen(buzzerOnOff);
      }
    }
    // Se siamo nel submenu T1
    else if(isTime1MenuSet == 1) {
      // Timeout per tornare al menu principale
      if(currentMillis - previousMillisExitOperationMode >= timeTimeMenu) {
        Serial.println("Returning to main mode menu...");
        isTime1MenuSet = 0;
        previousMillisExitOperationMode = currentMillis;
      }
      
      // Mostra il valore attuale di T1
      if(currentMillis - previousMillisPulseTime >= interval) {
        previousMillisPulseTime = currentMillis;
        show_char_noob(pokerTimer1);
      }
    }
    // Se siamo nel submenu T2
    else if(isTime2MenuSet == 1) {
      // Timeout per tornare al menu principale
      if(currentMillis - previousMillisExitOperationMode >= timeTimeMenu) {
        Serial.println("Returning to main mode menu...");
        isTime2MenuSet = 0;
        previousMillisExitOperationMode = currentMillis;
      }
      
      // Mostra il valore attuale di T2
      if(currentMillis - previousMillisPulseTime >= interval) {
        previousMillisPulseTime = currentMillis;
        show_char_noob(pokerTimer2);
      }
    }
    // Se siamo nel submenu WiFi
    else if(isWiFiMenu == 1) {
      // Timeout per tornare al menu principale
      if(currentMillis - previousMillisExitOperationMode >= timeTimeMenu) {
        Serial.println("Returning to main mode menu...");
        isWiFiMenu = 0;
        previousMillisExitOperationMode = currentMillis;
      }
      
      // Mostra lo stato attuale del WiFi
      if(currentMillis - previousMillisPulseTime >= interval) {
        previousMillisPulseTime = currentMillis;
        wifiStatusScreen(wifiEnabled);
      }
    }
    // Se siamo nel menu principale delle modalità
    else {
      // Timeout per uscire dal menu e salvare
      if(currentMillis - previousMillisExitOperationMode >= timeOperationModeMenu) {
        Serial.println("Exiting operation mode menu...");
        
        if(temporaryModeValue == OPERATION_MODE_BUZZER || 
           temporaryModeValue == OPERATION_MODE_T1 || 
           temporaryModeValue == OPERATION_MODE_T2 ||
           temporaryModeValue == OPERATION_MODE_WIFI ||
           temporaryModeValue == OPERATION_MODE_TABLE ||
           temporaryModeValue == OPERATION_MODE_PLAYERS) {
          // Se l'ultima selezione era una modalità di configurazione, non cambiare la modalità operativa
          writePokerTimerParams();
          Serial.println("Configuration options saved");
          
          // Gestisci specificamente il cambio di stato WiFi
          if(temporaryModeValue == OPERATION_MODE_WIFI && wifiStateWasChanged) {
            Serial.println("WiFi state changed by timeout - forcing crash reset...");
            forceCrashReset();  // Usa la funzione di crash reset
          }
        } else {
          // Altrimenti salva la nuova modalità operativa
          bool modeChanged = (operationMode != temporaryModeValue);
          operationMode = temporaryModeValue;
          writePokerTimerParams();
          Serial.print("Operation mode saved: ");
          Serial.println(operationMode);
          
          // Se il WiFi è stato modificato E stiamo cambiando modalità operativa, forza reset
          if (modeChanged && wifiStateWasChanged) {
            Serial.println("Mode changed and WiFi state changed by timeout - forcing crash reset...");
            forceCrashReset();
          }
        }
        
        // Se non abbiamo forzato un reset, ripristina lo stato normale
        isOperationModeMenu = 0;
        setTimer(pokerTimer1, 1);  // Resetta a T1
        wifiStateWasChanged = false; // Reset del flag
      }
      
      // Mostra la modalità corrente
      if(currentMillis - previousMillisPulseTime >= interval) {
        previousMillisPulseTime = currentMillis;
        if(temporaryModeValue == OPERATION_MODE_TABLE) {
          pulseTableNumberMode(100);
        }
        else if(temporaryModeValue == OPERATION_MODE_PLAYERS) {
          pulsePlayersMode(100);
        }
        else if(temporaryModeValue == OPERATION_MODE_BUZZER) {
          pulseBuzzerMode(100);
        } 
        else if(temporaryModeValue == OPERATION_MODE_T1) {
          pulseT1Mode(100);
        }
        else if(temporaryModeValue == OPERATION_MODE_T2) {
          pulseT2Mode(100);
        }
        else if(temporaryModeValue == OPERATION_MODE_WIFI) {
          pulseWiFiMode(100);
        }
        else {
          pulseNumber(100, temporaryModeValue);
        }
      }
    }
  }
  // Normale funzionamento del timer
  else {
    report_button(button.check_button(), "Action on button 1");

    // Controllo della batteria scarica
    if(isDisCharging == 1 && lastVolt <= minimumVoltage1 || isDisCharging == 0 && lastVolt >= minimumVoltage1 && lastVolt <= minimumVoltage2){
      if(currentMillis - previousMillisLowVolt >= interval){
        previousMillisLowVolt = currentMillis;
        Serial.println("Low Voltage...please charge!");
        isFirstTime = 1;
        pulseLowVoltage(interval);
      }
    }
    
    // Normali operazioni del timer
    else {
      if(isFirstTime == 1){
        show_animation_boot(intervalAnimation);
        setTimer(pokerTimer1,1);
        isFirstTime = 0;
      }
                   
      if ((currentMillis - previousMillis >= interval) && timerCurrent >= 0 && digitalRead(buttonPin) == 1 && isStarted == 1 && timeExpired == 0 && isPaused == 0) {
        previousMillis = currentMillis;
        Serial.print("Remaining Time: ");
        Serial.print(timerCurrent);
        Serial.print(" Button State: ");
        Serial.println(digitalRead(buttonPin));
         
        if(timerCurrent > 10){
          Serial.println();
          show_char_noob(timerCurrent);
          LedPulse(buttonLedPin,ledPower100,750);
        }
        else {
          if(timerCurrent == 10)
            show_char_noob(timerCurrent);
          else
            pulseNumber(100,timerCurrent);

          if(timerCurrent == 10 && timerCurrent > 0 || timerCurrent <= 5 && timerCurrent > 0){ //tick sound on 10,5,4,3,2,1
            Serial.println("BLINKING!");
            tickSound(noteTickDuration, tickNote, buzzerOnOff);
          }
          if(timerCurrent == 0){
            Serial.println("FINISH!");
            timeExpired = 1;
            isPaused = 1;
            isStarted = 0;
            endingSound(noteFinishDuration, endingNote, buzzerOnOff);
          }
        }
         
        if(timerCurrent > 0){
          timerCurrent = timerCurrent - 1;
        }
      }
    }
  }
  
  // Controllo della tensione per scrivere in EEPROM
  if(currentMillis - previousMillisVolt >= timeLife_60){ //write every 60sec on eeprom the last voltage value
    previousMillisVolt = currentMillis;
    checkIsDischarging();
  }
  
  // Gestisci il server web solo se il WiFi è connesso o in modalità AP
  if(wifiEnabled && (WiFi.status() == WL_CONNECTED || wifiAPMode)) {
    // Gestisci il server web
    unsigned long serverStartTime = millis();
    server.handleClient();
    
    // Se il server impiega troppo tempo, potremmo avere un problema
    if (millis() - serverStartTime > 500) {  // Se richiede più di 500ms
      Serial.println("Warning: Web server processing is taking too long");
    }
  }
  
  // NUOVA PARTE: Invia periodicamente lo stato al server centrale se il WiFi è connesso
  if (wifiEnabled && WiFi.status() == WL_CONNECTED) {
    unsigned long currentMillisForUpdate = millis();
    if (currentMillisForUpdate - lastStatusUpdateTime >= statusUpdateInterval) {
      lastStatusUpdateTime = currentMillisForUpdate;
      sendStatusToServer();
    }
  }
  
  // Petting il watchdog per farlo sapere che il loop è ancora attivo
  yield();  // Dà il tempo al sistema di processare attività in background
}


/*
void RP2040_led(){ //works only with RP2040
  Adafruit_NeoPixel led = Adafruit_NeoPixel(1, ledPin, NEO_GRB + NEO_KHZ800);
  led.setPixelColor(0, led.Color(0, 20, 0));
  led.show();
}
*/

void TurnOnOffBuzzer(){
    buzzerOnOff = !buzzerOnOff;
   
    Serial.print("Buzzer set to: ");
    Serial.println(buzzerOnOff);
    buzzerOnOffScreen(buzzerOnOff);
    pauseSound(notePauseDuration, pauseNote, buzzerOnOff);
    writePokerTimerParams();
}


void SinglePress() {
  digitalWrite(ledPin, digitalRead(buttonPin));

  Serial.print("Single Press! ");
  
  switch(operationMode) {
    case OPERATION_MODE_1:  // T1/T2 con avvio automatico
      if(isPaused == 1 && !timeExpired) {  
        // Se è in pausa (ma non è terminato), riprendi da dove interrotto
        Serial.print("Resume Timer at: ");
        Serial.print(timerCurrent);
        Serial.println(" seconds");    
        setTimer(timerCurrent, 0);
        isStarted = 1;
      } else if(isStarted == 0 && !timeExpired) {
        // Se il timer è fermo (ma non terminato), avvialo
        if(pokerTimer1or2 == pokerTimer1) {
          Serial.print("Start Timer from: ");
          Serial.print(pokerTimer1);
          Serial.println(" seconds");    
          setTimer(pokerTimer1, 0);
        } else {
          Serial.print("Start Timer from: ");
          Serial.print(pokerTimer2);
          Serial.println(" seconds");    
          setTimer(pokerTimer2, 0);
        }
        isStarted = 1;
      } else if(timeExpired == 1) {
        // Se il timer è terminato, resettalo ma rimane fermo
        if(pokerTimer1or2 == pokerTimer1) {
          Serial.print("Reset Timer to: ");
          Serial.print(pokerTimer1);
          Serial.println(" seconds but stay paused");    
          setTimer(pokerTimer1, 1);  // paused = 1
        } else {
          Serial.print("Reset Timer to: ");
          Serial.print(pokerTimer2);
          Serial.println(" seconds but stay paused");    
          setTimer(pokerTimer2, 1);  // paused = 1
        }
        isStarted = 0;
        timeExpired = 0;
      } else {
        // Se è in esecuzione, resettalo e avvialo subito
        if(pokerTimer1or2 == pokerTimer1) {
          Serial.print("Reset Timer to: ");
          Serial.print(pokerTimer1);
          Serial.println(" seconds and start");    
          setTimer(pokerTimer1, 0);
        } else {
          Serial.print("Reset Timer to: ");
          Serial.print(pokerTimer2);
          Serial.println(" seconds and start");    
          setTimer(pokerTimer2, 0);
        }
        isStarted = 1;
        timeExpired = 0;
      }
      break;
      
    case OPERATION_MODE_2:  // T1/T2 switchabile, con tap dipende dallo stato
      if(isPaused == 1 && !timeExpired) {  
        // Se è in pausa (ma non è terminato), riprendi da dove interrotto
        Serial.print("Resume Timer at: ");
        Serial.print(timerCurrent);
        Serial.println(" seconds");    
        setTimer(timerCurrent, 0);
        isStarted = 1;
      } else if(isStarted == 0 && !timeExpired) {
        // Se il timer è fermo (ma non terminato), avvialo
        if(pokerTimer1or2 == pokerTimer1) {
          Serial.print("Start Timer from: ");
          Serial.print(pokerTimer1);
          Serial.println(" seconds");    
          setTimer(pokerTimer1, 0);
        } else {
          Serial.print("Start Timer from: ");
          Serial.print(pokerTimer2);
          Serial.println(" seconds");    
          setTimer(pokerTimer2, 0);
        }
        isStarted = 1;
      } else if(timeExpired == 1) {
        // Se il timer è terminato, resettalo ma rimane fermo
        if(pokerTimer1or2 == pokerTimer1) {
          Serial.print("Reset Timer to: ");
          Serial.print(pokerTimer1);
          Serial.println(" seconds but stay paused");    
          setTimer(pokerTimer1, 1);  // paused = 1
        } else {
          Serial.print("Reset Timer to: ");
          Serial.print(pokerTimer2);
          Serial.println(" seconds but stay paused");    
          setTimer(pokerTimer2, 1);  // paused = 1
        }
        isStarted = 0;
        timeExpired = 0;
      } else {
        // Se è in esecuzione, resettalo e fermalo
        if(pokerTimer1or2 == pokerTimer1) {
          Serial.print("Reset Timer to: ");
          Serial.print(pokerTimer1);
          Serial.println(" seconds and pause");    
          setTimer(pokerTimer1, 1);
        } else {
          Serial.print("Reset Timer to: ");
          Serial.print(pokerTimer2);
          Serial.println(" seconds and pause");    
          setTimer(pokerTimer2, 1);
        }
        isStarted = 0;
        timeExpired = 0;
      }
      break;
      
    case OPERATION_MODE_3:  // Solo T1, con tap dipende dallo stato
      pokerTimer1or2 = pokerTimer1;  // Forza sempre T1
      
      if(isPaused == 1 && !timeExpired) {  
        // Se è in pausa (ma non è terminato), riprendi da dove interrotto
        Serial.print("Resume Timer at: ");
        Serial.print(timerCurrent);
        Serial.println(" seconds");    
        setTimer(timerCurrent, 0);
        isStarted = 1;
      } else if(isStarted == 0 && !timeExpired) {
        // Se il timer è fermo (ma non terminato), avvialo
        Serial.print("Start Timer from: ");
        Serial.print(pokerTimer1);
        Serial.println(" seconds");    
        setTimer(pokerTimer1, 0);
        isStarted = 1;
      } else if(timeExpired == 1) {
        // Se il timer è terminato, resettalo ma rimane fermo
        Serial.print("Reset Timer to: ");
        Serial.print(pokerTimer1);
        Serial.println(" seconds but stay paused");    
        setTimer(pokerTimer1, 1);  // paused = 1
        isStarted = 0;
        timeExpired = 0;
      } else {
        // Se è in esecuzione, resettalo e avvialo subito
        Serial.print("Reset Timer to: ");
        Serial.print(pokerTimer1);
        Serial.println(" seconds and start");    
        setTimer(pokerTimer1, 0);
        isStarted = 1;
        timeExpired = 0;
      }
      break;
      
    case OPERATION_MODE_4:  // Solo T1, con tap dipende dallo stato
      pokerTimer1or2 = pokerTimer1;  // Forza sempre T1
      
      if(isPaused == 1 && !timeExpired) {  
        // Se è in pausa (ma non è terminato), riprendi da dove interrotto
        Serial.print("Resume Timer at: ");
        Serial.print(timerCurrent);
        Serial.println(" seconds");    
        setTimer(timerCurrent, 0);
        isStarted = 1;
      } else if(isStarted == 0 && !timeExpired) {
        // Se il timer è fermo (ma non terminato), avvialo
        Serial.print("Start Timer from: ");
        Serial.print(pokerTimer1);
        Serial.println(" seconds");    
        setTimer(pokerTimer1, 0);
        isStarted = 1;
      } else if(timeExpired == 1) {
        // Se il timer è terminato, resettalo ma rimane fermo
        Serial.print("Reset Timer to: ");
        Serial.print(pokerTimer1);
        Serial.println(" seconds but stay paused");    
        setTimer(pokerTimer1, 1);  // paused = 1
        isStarted = 0;
        timeExpired = 0;
      } else {
        // Se è in esecuzione, resettalo e fermalo
        Serial.print("Reset Timer to: ");
        Serial.print(pokerTimer1);
        Serial.println(" seconds and pause");    
        setTimer(pokerTimer1, 1);
        isStarted = 0;
        timeExpired = 0;
      }
      break;
  }
}

void DoublePress() {
  // Nelle modalità 3 e 4 il doppio click è assente
  if(operationMode == OPERATION_MODE_3 || operationMode == OPERATION_MODE_4) {
    return;  // Non fare nulla
  }
  
  // Per le modalità 1 e 2
  if(operationMode == OPERATION_MODE_1 || operationMode == OPERATION_MODE_2) {
    Serial.print("Double Press!! Switch Timer to: ");
    
    if(pokerTimer1or2 == pokerTimer1) {
      Serial.print(pokerTimer2);
      Serial.println(" seconds");  
      
      // In modalità 1, passa a T2 e metti in pausa
      if(operationMode == OPERATION_MODE_1) {
        setTimer(pokerTimer2, 1);  // paused = 1
        isStarted = 0;
      } 
      // In modalità 2, passa a T2 e rimane fermo
      else {
        setTimer(pokerTimer2, 1);  // paused = 1
        isStarted = 0;
      }
    } else {
      Serial.print(pokerTimer1);
      Serial.println(" seconds");  
      
      // In modalità 1, passa a T1 e metti in pausa
      if(operationMode == OPERATION_MODE_1) {
        setTimer(pokerTimer1, 1);  // paused = 1
        isStarted = 0;
      } 
      // In modalità 2, passa a T1 e rimane fermo
      else {
        setTimer(pokerTimer1, 1);  // paused = 1
        isStarted = 0;
      }
    }
  }
}

void LongPressStart() {
  // Rimuoviamo la condizione che disabilita la pausa nelle modalità 3 e 4
  if(isPaused == 0 && isStarted == 1 && timerCurrent > 0) {
    analogWrite(buttonLedPin, 255);    
    delay(1);
    isPaused = 1;
    Serial.print("Start Long Press!! Paused Timer at: ");
    timerCurrent = timerCurrent + 1; // per compensare l'attesa per il long press
    Serial.print(timerCurrent);
    Serial.println(" seconds");
    show_char_noob(timerCurrent);

    pauseSound(notePauseDuration, pauseNote, buzzerOnOff);
  }
}

void LongPressStop()
{
  analogWrite(buttonLedPin,0);    
  delay(1);
}


void setTimer(uint8_t timerValue, uint8_t paused){
    //show_timer(timerValue);
    show_char_noob(timerValue);

    if(timerValue == pokerTimer1 || timerValue == pokerTimer2)
      pokerTimer1or2 = timerValue;
    timerCurrent = previousTimer = timerValue;
    isPaused = paused;
    timeExpired = 0;  // Resetta sempre timeExpired quando si imposta un nuovo timer
}

// LED MANAGEMENT

void clear_module_leds(uint8_t module){
  uint8_t num_led = module*3;

  pixels.setPixelColor(num_led, pixels.Color(255,255,255));  //B  A  C
  pixels.setPixelColor(num_led+1, pixels.Color(255,255,255));  //E  D  F
  pixels.setPixelColor(num_led+2, pixels.Color(255,255,255));  //DP  G  NC

  pixels.show();
}


void show_char_noob(uint8_t value)
{
  uint8_t num_led;
  uint8_t what_num;
  uint8_t unit;
  uint8_t decimal;

  if(value >= 10){
      decimal = value / 10;
      unit    = value % 10;
    }
    else{
      decimal = 0;
      unit    = value % 10;
    }


  for(int i = 0; i < 2; i++){
    num_led = i*3;
    if(i == 0){//first digit
      what_num = decimal;
    }
    else {
      what_num = unit;
    }
    switch (what_num)
      {

        case 0:
        pixels.setPixelColor(num_led, pixels.Color(0,0,0));  //B  A  C
        pixels.setPixelColor(num_led+1, pixels.Color(0,0,0));  //E  D  F
        pixels.setPixelColor(num_led+2, pixels.Color(255,255,255));  //DP  G  NC
        break;
       
        case 1:
        pixels.setPixelColor(num_led, pixels.Color(0,255,0));  //B  A  C  
        pixels.setPixelColor(num_led+1, pixels.Color(255,255,255));  //E  D  F
        pixels.setPixelColor(num_led+2, pixels.Color(255,255,255));  //DP  G  NC
        break;
         
        case 2:
        pixels.setPixelColor(num_led, pixels.Color(0,0,255));  //B  A  C
        pixels.setPixelColor(num_led+1, pixels.Color(0,0,255));  //E  D  F
        pixels.setPixelColor(num_led+2, pixels.Color(255,0,255));  //DP  G  NC
        break;

        case 3:
        pixels.setPixelColor(num_led, pixels.Color(0,0,0));  //B  A  C
        pixels.setPixelColor(num_led+1, pixels.Color(255,0,255));  //E  D  F
        pixels.setPixelColor(num_led+2, pixels.Color(255,0,255));  //DP  G  NC
        break;

        case 4:
        pixels.setPixelColor(num_led, pixels.Color(0,255,0));  //B  A  C
        pixels.setPixelColor(num_led+1, pixels.Color(255,255,0));  //E  D  F
        pixels.setPixelColor(num_led+2, pixels.Color(255,0,255));  //DP  G  NC
        break;

        case 5:
        pixels.setPixelColor(num_led, pixels.Color(255,0,0));  //B  A  C
        pixels.setPixelColor(num_led+1, pixels.Color(255,0,0));  //E  D  F
        pixels.setPixelColor(num_led+2, pixels.Color(255,0,255));  //DP  G  NC
        break;

        case 6:
        pixels.setPixelColor(num_led, pixels.Color(255,0,0));  //B  A  C
        pixels.setPixelColor(num_led+1, pixels.Color(0,0,0));  //E  D  F
        pixels.setPixelColor(num_led+2, pixels.Color(255,0,255));  //DP  G  NC
        break;

        case 7:
        pixels.setPixelColor(num_led, pixels.Color(0,0,0));  //B  A  C
        pixels.setPixelColor(num_led+1, pixels.Color(255,255,255));  //E  D  F
        pixels.setPixelColor(num_led+2, pixels.Color(255,255,255));  //DP  G  NC
        break;

        case 8:
        pixels.setPixelColor(num_led, pixels.Color(0,0,0));  //B  A  C
        pixels.setPixelColor(num_led+1, pixels.Color(0,0,0));  //E  D  F
        pixels.setPixelColor(num_led+2, pixels.Color(255,0,255));  //DP  G  NC
        break;

        case 9:
        pixels.setPixelColor(num_led, pixels.Color(0,0,0));  //B  A  C
        pixels.setPixelColor(num_led+1, pixels.Color(255,0,0));  //E  D  F
        pixels.setPixelColor(num_led+2, pixels.Color(255,0,255));  //DP  G  NC
        break;

        default:
        pixels.setPixelColor(num_led, pixels.Color(255,255,255));  //B  A  C
        pixels.setPixelColor(num_led+1, pixels.Color(255,255,255));  //E  D  F
        pixels.setPixelColor(num_led+2, pixels.Color(255,255,255));  //DP  G  NC
        break;
       
      }
      Serial.print("Number:");
      Serial.print(what_num);
      Serial.print(" Module:");
      Serial.println(i);
  }
 
  if(value < 10){ //to save power we turn off the first digit that is 0 if the value is less than 10
    clear_module_leds(0);
  }
  pixels.show();
}

void show_or_clear_segment(uint8_t module, uint8_t segment,uint8_t show_or_clear)
{
  uint8_t num_led = module*3;
  switch (segment)
  {
    case 'a':
    pixels.setPixelColor(num_led, pixels.Color(255,show_or_clear == 0 ? 255 : 0,255));  //B  A  C
    pixels.setPixelColor(num_led+1, pixels.Color(255,255,255));  //E  D  F
    pixels.setPixelColor(num_led+2, pixels.Color(255,255,255));  //DP  G  NC
    break;
    case 'b':
    pixels.setPixelColor(num_led, pixels.Color(show_or_clear == 0 ? 255 : 0,255,255));  //B  A  C
    pixels.setPixelColor(num_led+1, pixels.Color(255,255,255));  //E  D  F
    pixels.setPixelColor(num_led+2, pixels.Color(255,255,255));  //DP  G  NC
    break;
    case 'c':
    pixels.setPixelColor(num_led, pixels.Color(255,255,show_or_clear == 0 ? 255 : 0));  //B  A  C
    pixels.setPixelColor(num_led+1, pixels.Color(255,255,255));  //E  D  F
    pixels.setPixelColor(num_led+2, pixels.Color(255,255,255));  //DP  G  NC
    break;
    case 'd':
    pixels.setPixelColor(num_led, pixels.Color(255,255,255));  //B  A  C
    pixels.setPixelColor(num_led+1, pixels.Color(255,show_or_clear == 0 ? 255 : 0,255));  //E  D  F
    pixels.setPixelColor(num_led+2, pixels.Color(255,255,255));  //DP  G  NC
    break;
    case 'e':
    pixels.setPixelColor(num_led, pixels.Color(255,255,255));  //B  A  C
    pixels.setPixelColor(num_led+1, pixels.Color(show_or_clear == 0 ? 255 : 0,255,255));  //E  D  F
    pixels.setPixelColor(num_led+2, pixels.Color(255,255,255));  //DP  G  NC
    break;
    case 'f':
    pixels.setPixelColor(num_led, pixels.Color(255,255,255));  //B  A  C
    pixels.setPixelColor(num_led+1, pixels.Color(255,255,show_or_clear == 0 ? 255 : 0));  //E  D  F
    pixels.setPixelColor(num_led+2, pixels.Color(255,255,255));  //DP  G  NC
    break;
    case 'g':
    pixels.setPixelColor(num_led, pixels.Color(255,255,255));  //B  A  C
    pixels.setPixelColor(num_led+1, pixels.Color(255,255,255));  //E  D  F
    pixels.setPixelColor(num_led+2, pixels.Color(255,show_or_clear == 0 ? 255 : 0,255));  //DP  G  NC
    break;
  }
 
  pixels.show();
}


void showTableNumberScreen() {
  for(int i = 0; i < LED_MODULES; i++) {
    clear_module_leds(i);
  }
  
  // "T" sul primo digit
  pixels.setPixelColor(0, pixels.Color(255,255,255));  //B  A  C
  pixels.setPixelColor(1, pixels.Color(0,0,0));  //E  D  F
  pixels.setPixelColor(2, pixels.Color(255,0,255));  //DP  G  NC
  
  // Secondo digit spento
  pixels.setPixelColor(3, pixels.Color(255,255,255));  //B  A  C
  pixels.setPixelColor(4, pixels.Color(255,255,255));  //E  D  F
  pixels.setPixelColor(5, pixels.Color(255,255,255));  //DP  G  NC
  pixels.show();
}

void show_animation_boot(uint8_t time){
  Serial.println("Show animation...");
 
  for(int i = 0; i <= LED_MODULES; i++){
    clear_module_leds(i);
  }
 
  show_or_clear_segment(0,'a',1);
  show_or_clear_segment(1,'a',1);
  delay(time);
  show_or_clear_segment(0,'a',0);
  show_or_clear_segment(1,'a',0);
  delay(time);
   
  show_or_clear_segment(0,'b',1);
  show_or_clear_segment(1,'b',1);
  delay(time);
  show_or_clear_segment(0,'b',0);
  show_or_clear_segment(1,'b',0);
  delay(time);
   
  show_or_clear_segment(0,'g',1);
  show_or_clear_segment(1,'g',1);
  delay(time);
  show_or_clear_segment(0,'g',0);
  show_or_clear_segment(1,'g',0);
  delay(time);
       
  show_or_clear_segment(0,'e',1);
  show_or_clear_segment(1,'e',1);
  delay(time);
  show_or_clear_segment(0,'e',0);
  show_or_clear_segment(1,'e',0);
  delay(time);
     
  show_or_clear_segment(0,'d',1);
  show_or_clear_segment(1,'d',1);
  delay(time);
  show_or_clear_segment(0,'d',0);
  show_or_clear_segment(1,'d',0);
  delay(time);
       
  show_or_clear_segment(0,'c',1);
  show_or_clear_segment(1,'c',1);
  delay(time);
  show_or_clear_segment(0,'c',0);
  show_or_clear_segment(1,'c',0);
  delay(time);
     
  show_or_clear_segment(0,'g',1);
  show_or_clear_segment(1,'g',1);
  delay(time);
  show_or_clear_segment(0,'g',0);
  show_or_clear_segment(1,'g',0);
  delay(time);
     
  show_or_clear_segment(0,'f',1);
  show_or_clear_segment(1,'f',1);
  delay(time);
  show_or_clear_segment(0,'f',0);
  show_or_clear_segment(1,'f',0);
  delay(time);

}



void show_animation_charge(uint8_t time){
  Serial.println("Show charge animation...");
 
  for(int i = 0; i <= LED_MODULES; i++){
    clear_module_leds(i);
  }
 
  show_or_clear_segment(0,'f',1);
  delay(time);
  show_or_clear_segment(0,'f',0);
  delay(time);
   
  show_or_clear_segment(0,'e',1);
  delay(time);
  show_or_clear_segment(0,'e',0);
  delay(time);

  show_or_clear_segment(0,'d',1);
  delay(time);
  show_or_clear_segment(0,'d',0);
  delay(time);
 
  show_or_clear_segment(0,'c',1);
  delay(time);
  show_or_clear_segment(0,'c',0);
  delay(time);

  show_or_clear_segment(1,'f',1);
  delay(time);
  show_or_clear_segment(1,'f',0);
  delay(time);

  show_or_clear_segment(1,'a',1);
  delay(time);
  show_or_clear_segment(1,'a',0);
  delay(time);

  show_or_clear_segment(1,'b',1);
  delay(time);
  show_or_clear_segment(1,'b',0);
  delay(time);

  show_or_clear_segment(1,'c',1);
  delay(time);
  show_or_clear_segment(1,'c',0);
  delay(time);

  show_or_clear_segment(1,'d',1);
  delay(time);
  show_or_clear_segment(1,'d',0);
  delay(time);

  show_or_clear_segment(1,'e',1);
  delay(time);
  show_or_clear_segment(1,'e',0);
  delay(time);

  show_or_clear_segment(0,'b',1);
  delay(time);
  show_or_clear_segment(0,'b',0);
  delay(time);

  show_or_clear_segment(0,'a',1);
  delay(time);
  show_or_clear_segment(0,'a',0);
  //delay(time);
/*
  for(int i = 0; i <= LED_MODULES; i++){
    clear_module_leds(i);
  }
  */
}

void pulseWiFiMode(uint16_t pulseTime) {
  clear_module_leds(0);
  clear_module_leds(1);
  delay(pulseTime);
  showWiFiMode();
}

void pulseLowVoltage(uint16_t pulseTime){
  lowVoltageScreen();
  delay(pulseTime);
  clear_module_leds(0);
  clear_module_leds(1);
  show_animation_charge(intervalAnimation);
}

void pulseNumber(uint16_t pulseTime,uint8_t value){
  clear_module_leds(0);
  clear_module_leds(1);
  delay(pulseTime);
  show_char_noob(value);
}

void pulseBuzzerMode(uint16_t pulseTime) {
  // Prima pulisci il display
  clear_module_leds(0);
  clear_module_leds(1);
  delay(pulseTime);
  // Poi mostra la "b"
  showBuzzerMode();
}

void pulsePlayersMode(uint16_t pulseTime) {
  clear_module_leds(0);
  clear_module_leds(1);
  delay(pulseTime);
  showPlayersMode();
}

// Funzione per far lampeggiare "t1"
void pulseT1Mode(uint16_t pulseTime) {
  clear_module_leds(0);
  clear_module_leds(1);
  delay(pulseTime);
  showT1Mode();
}

// Funzione per far lampeggiare "t2"
void pulseT2Mode(uint16_t pulseTime) {
  clear_module_leds(0);
  clear_module_leds(1);
  delay(pulseTime);
  showT2Mode();
}

void pulseTableNumberMode(uint16_t pulseTime) {
  clear_module_leds(0);
  clear_module_leds(1);
  delay(pulseTime);
  showTableNumberScreen();
}

void tickSound(uint16_t time,uint16_t note, uint8_t OnOff){
  Serial.println(OnOff);
  LedPulse(buttonLedPin,ledPower100,500);
  if(OnOff == 1)
    tone(buzzerPin, note);
  else
    noTone(buzzerPin);
 
  LedPulse(buttonLedPin,ledPower100,500);
  delay(time);
  noTone(buzzerPin);
}


void pauseSound(uint16_t time, uint16_t note, uint8_t OnOff){
  for (int i = 2; i > 0; i--){
    if(OnOff == 1){
      tone(buzzerPin, note);
      delay(time);
      noTone(buzzerPin);
      delay(50);  
    }
    else
      noTone(buzzerPin);
    delay(50);  
  }
}

void endingSound(uint16_t time,uint16_t note, uint8_t OnOff){
  analogWrite(buttonLedPin,255);
  delay(1);
  if(OnOff == 1){
    tone(buzzerPin, note);
    delay(time*2);
    noTone(buzzerPin);
  }
  else{
    delay(time*2);
    noTone(buzzerPin);
  }

  analogWrite(buttonLedPin,0);
  delay(1);
}


void LedPulse(uint8_t pin, uint8_t power, uint16_t duration){
  float in, out;

  for (in = 4.712; in < 10.995; in = in + (0.0001 * duration))
  {
  out = sin(in) * (1.275 * power) + (1.275 * power);
  analogWrite(pin,out);
  delay(1);
  }
}

/*
uint8_t getVoltagePercentage(uint8_t AnalogInput){
  uint8_t value = 0;
  float   voltage;
  float   perc;

  value = analogRead(AnalogInput);
  voltage = value * 5.0/1023;
  perc = map(voltage, 3.6, 4.2, 0, 100);
  Serial.print("Voltage= ");
  Serial.println(voltage);
  Serial.print("Battery level= ");
  Serial.print(perc);
  Serial.println(" %");
  return voltage;
}
*/

void loopTimerTest(){
  if(timeExpired == 1){ //loop timer for test
    setTimer(pokerTimer1,0);
    digitalWrite(buttonPin, 1);
 }
}


void readPokerTimerParams() {
  Serial.println("===== READING EEPROM =====");
  
  // Inizializza la EEPROM con la dimensione corretta
  EEPROM.begin(512);
  
  // Leggi i valori
  uint8_t readT1 = EEPROM.read(memAddressTimer1);
  uint8_t readT2 = EEPROM.read(memAddressTimer2);
  uint8_t readBuzzer = EEPROM.read(memAddressBuzzerState);
  uint8_t readMode = EEPROM.read(memAddressOperationMode);
  uint8_t readTable = EEPROM.read(memAddressTableNumber);
  uint8_t readWiFi = EEPROM.read(memAddressWiFiState);
  uint8_t readPlayers = EEPROM.read(memAddressPlayersCount);
  
  Serial.print("Read T1: "); Serial.println(readT1);
  Serial.print("Read T2: "); Serial.println(readT2);
  Serial.print("Read Buzzer: "); Serial.println(readBuzzer);
  Serial.print("Read Mode: "); Serial.println(readMode);
  Serial.print("Read Table: "); Serial.println(readTable);
  Serial.print("Read WiFi: "); Serial.println(readWiFi);
  Serial.print("Read Players: "); Serial.println(readPlayers);
  
  // Valida e assegna i valori
  if (readT1 != 255 && readT1 >= 5 && readT1 <= 95) {
    pokerTimer1 = readT1;
  } else {
    pokerTimer1 = timerSet_20;
    Serial.println("Using default T1: 20s");
  }
  
  if (readT2 != 255 && readT2 >= 5 && readT2 <= 95) {
    pokerTimer2 = readT2;
  } else {
    pokerTimer2 = timerSet_30;
    Serial.println("Using default T2: 30s");
  }
  
  if (readBuzzer != 255 && (readBuzzer == 0 || readBuzzer == 1)) {
    buzzerOnOff = readBuzzer;
  } else {
    buzzerOnOff = 1;
    Serial.println("Using default Buzzer: ON");
  }
  
  if (readMode != 255 && readMode >= 1 && readMode <= 4) {
    operationMode = readMode;
  } else {
    operationMode = OPERATION_MODE_1;
    Serial.println("Using default Mode: 1");
  }
  
  if (readTable != 255 && readTable >= 0 && readTable <= 99) {
    tableNumber = readTable;
  } else {
    tableNumber = 0;
    Serial.println("Using default Table: 0");
  }
  
  if (readWiFi != 255) {
    wifiEnabled = (readWiFi == 1);
  } else {
    wifiEnabled = true;
    Serial.println("Using default WiFi: ON");
  }
  
  if (readPlayers != 255 && readPlayers >= 1 && readPlayers <= 10) {
    playersCount = readPlayers;
  } else {
    playersCount = 10;
    Serial.println("Using default Players Count: 10");
  }
  
  Serial.println("===== EEPROM READ COMPLETE =====");
  Serial.print("Timer1: "); Serial.print(pokerTimer1); Serial.println("s");
  Serial.print("Timer2: "); Serial.print(pokerTimer2); Serial.println("s");
  Serial.print("Buzzer: "); Serial.println(buzzerOnOff ? "ON" : "OFF");
  Serial.print("Mode: "); Serial.println(operationMode);
  Serial.print("Table: "); Serial.println(tableNumber);
  Serial.print("WiFi: "); Serial.println(wifiEnabled ? "ON" : "OFF");
  Serial.print("Players: "); Serial.println(playersCount);
}

bool writePokerTimerParams() {
  Serial.println("===== WRITING EEPROM PARAMS =====");
  Serial.print("T1: "); Serial.println(pokerTimer1);
  Serial.print("T2: "); Serial.println(pokerTimer2);
  Serial.print("Mode: "); Serial.println(operationMode);
  Serial.print("Buzzer: "); Serial.println(buzzerOnOff);
  Serial.print("Table: "); Serial.println(tableNumber);
  Serial.print("WiFi: "); Serial.println(wifiEnabled);
  Serial.print("Players: "); Serial.println(playersCount);
  
  // Reinizializza EEPROM ad ogni scrittura
  EEPROM.begin(512);
  
  // Esegui scritture multiple di ogni valore per aumentare l'affidabilità
  for (int i = 0; i < 3; i++) {
    EEPROM.write(memAddressTimer1, pokerTimer1);
    EEPROM.write(memAddressTimer2, pokerTimer2);
    EEPROM.write(memAddressBuzzerState, buzzerOnOff);
    EEPROM.write(memAddressOperationMode, operationMode);
    EEPROM.write(memAddressTableNumber, tableNumber);
    EEPROM.write(memAddressWiFiState, wifiEnabled ? 1 : 0);
    EEPROM.write(memAddressPlayersCount, playersCount);
    
    // Forza un commit dopo ogni set di scritture
    EEPROM.commit();
    delay(10);
  }
  
  // Assicurati che il commit finale sia eseguito
  bool success = EEPROM.commit();
  
  if (success) {
    Serial.println("EEPROM commit SUCCESS");
  } else {
    Serial.println("EEPROM commit FAILED");
  }
  
  // Verifica dopo l'ultima scrittura
  delay(50);
  
  uint8_t verifyT1 = EEPROM.read(memAddressTimer1);
  uint8_t verifyT2 = EEPROM.read(memAddressTimer2);
  uint8_t verifyMode = EEPROM.read(memAddressOperationMode);
  uint8_t verifyBuzzer = EEPROM.read(memAddressBuzzerState);
  uint8_t verifyTable = EEPROM.read(memAddressTableNumber);
  uint8_t verifyPlayers = EEPROM.read(memAddressPlayersCount);
  
  Serial.println("===== EEPROM VERIFICATION =====");
  Serial.print("T1 written: "); Serial.print(pokerTimer1); Serial.print(" | Read: "); Serial.println(verifyT1);
  Serial.print("T2 written: "); Serial.print(pokerTimer2); Serial.print(" | Read: "); Serial.println(verifyT2);
  Serial.print("Mode written: "); Serial.print(operationMode); Serial.print(" | Read: "); Serial.println(verifyMode);
  Serial.print("Buzzer written: "); Serial.print(buzzerOnOff); Serial.print(" | Read: "); Serial.println(verifyBuzzer);
  Serial.print("Table written: "); Serial.print(tableNumber); Serial.print(" | Read: "); Serial.println(verifyTable);
  Serial.print("Players written: "); Serial.print(playersCount); Serial.print(" | Read: "); Serial.println(verifyPlayers);
  
  if (verifyT1 != pokerTimer1 || verifyT2 != pokerTimer2 || verifyMode != operationMode ||
      verifyBuzzer != buzzerOnOff || verifyTable != tableNumber || verifyPlayers != playersCount) {
    Serial.println("⚠️ WARNING: EEPROM verification failed!");
    return false;
  } else {
    Serial.println("✓ EEPROM verification OK");
    return true;
  }
}


void applySettingsImmediately() {
  // Salva lo stato corrente
  bool wasRunning = (isStarted == 1 && isPaused == 0);
  bool wasPaused = isPaused;
  
  // Rileggiamo i valori da EEPROM per assicurarci di avere quelli aggiornati
  uint8_t freshT1 = EEPROM.read(memAddressTimer1);
  uint8_t freshT2 = EEPROM.read(memAddressTimer2);
  uint8_t freshMode = EEPROM.read(memAddressOperationMode);
  uint8_t freshBuzzer = EEPROM.read(memAddressBuzzerState);
  uint8_t freshTable = EEPROM.read(memAddressTableNumber);
  uint8_t freshPlayers = EEPROM.read(memAddressPlayersCount); // Aggiungi questa riga
  
  // Verifichiamo se ci sono differenze
  bool valuesChanged = false;
  
  if (freshT1 != 255 && freshT1 != pokerTimer1) {
    Serial.print("Updating T1 from EEPROM: ");
    Serial.print(pokerTimer1);
    Serial.print(" -> ");
    Serial.println(freshT1);
    pokerTimer1 = freshT1;
    valuesChanged = true;
  }
  
  if (freshT2 != 255 && freshT2 != pokerTimer2) {
    Serial.print("Updating T2 from EEPROM: ");
    Serial.print(pokerTimer2);
    Serial.print(" -> ");
    Serial.println(freshT2);
    pokerTimer2 = freshT2;
    valuesChanged = true;
  }
  
  if (freshMode != 255 && freshMode >= 1 && freshMode <= 4 && freshMode != operationMode) {
    Serial.print("Updating Mode from EEPROM: ");
    Serial.print(operationMode);
    Serial.print(" -> ");
    Serial.println(freshMode);
    operationMode = freshMode;
    valuesChanged = true;
  }
  
  if (freshBuzzer != 255 && (freshBuzzer == 0 || freshBuzzer == 1) && freshBuzzer != buzzerOnOff) {
    Serial.print("Updating Buzzer from EEPROM: ");
    Serial.print(buzzerOnOff);
    Serial.print(" -> ");
    Serial.println(freshBuzzer);
    buzzerOnOff = freshBuzzer;
    valuesChanged = true;
  }
  
  if (freshTable != 255 && freshTable >= 0 && freshTable <= 99 && freshTable != tableNumber) {
    Serial.print("Updating Table from EEPROM: ");
    Serial.print(tableNumber);
    Serial.print(" -> ");
    Serial.println(freshTable);
    tableNumber = freshTable;
    valuesChanged = true;
  }
  
  // Aggiungi questo blocco per gestire il numero di giocatori
  if (freshPlayers != 255 && freshPlayers >= 1 && freshPlayers <= 10 && freshPlayers != playersCount) {
    Serial.print("Updating Players Count from EEPROM: ");
    Serial.print(playersCount);
    Serial.print(" -> ");
    Serial.println(freshPlayers);
    playersCount = freshPlayers;
    valuesChanged = true;
  }
  
  if (valuesChanged) {
    Serial.println("Values updated from EEPROM!");
  } else {
    Serial.println("No changes from EEPROM values.");
  }
  
  // Aggiungiamo log estesi per debug
  Serial.println("=== Applying Settings Immediately ===");
  Serial.print("Current T1: "); Serial.println(pokerTimer1);
  Serial.print("Current T2: "); Serial.println(pokerTimer2);
  Serial.print("Current Mode: "); Serial.println(operationMode);
  Serial.print("Current Timer: "); Serial.println(timerCurrent);
  Serial.print("Current Timer1or2: "); Serial.println(pokerTimer1or2);
  Serial.print("Current Buzzer: "); Serial.println(buzzerOnOff);  // Aggiungi questa riga
  Serial.print("Current Players Count: "); Serial.println(playersCount);  // Aggiungi questa riga
  
  // Nelle modalità 3 e 4 (solo T1) usa sempre T1
  if (operationMode == 3 || operationMode == 4) {
    // Forza l'utilizzo di T1
    pokerTimer1or2 = pokerTimer1;
    timerCurrent = pokerTimer1;
    Serial.print("Switching to T1 (mode only supports T1): ");
    Serial.println(pokerTimer1);
  } else {
      pokerTimer1or2 = pokerTimer1;
      timerCurrent = pokerTimer1;
      Serial.print("Setting default timer to T1: ");
      Serial.println(pokerTimer1);
  }
  
  // Emetti un suono di conferma
  if (buzzerOnOff) {
    tone(buzzerPin, 1000);
    delay(100);
    noTone(buzzerPin);
    delay(50);
    tone(buzzerPin, 1200);
    delay(100);
    noTone(buzzerPin);
  }

  // Forza l'aggiornamento del display
  Serial.print("Updating display to show: ");
  Serial.println(timerCurrent);
  
  // Pulizia e inizializzazione del display
  for(int i = 0; i < LED_MODULES; i++) {
    clear_module_leds(i);
  }
  delay(50);  // Breve pausa per assicurarsi che il display sia pulito
  
  // Mostra il valore attuale
  show_char_noob(timerCurrent);
  delay(50);  // Breve pausa per assicurarsi che il display venga aggiornato
  
  // Ripristina lo stato precedente del timer
  isPaused = wasPaused;
  
  // Se il timer era in esecuzione, mantienilo in esecuzione
  if (wasRunning) {
    isPaused = 0;
    isStarted = 1;
  }
  
  Serial.println("Settings applied immediately!");
  Serial.print("T1: ");
  Serial.println(pokerTimer1);
  Serial.print("T2: ");
  Serial.println(pokerTimer2);
  Serial.print("Mode: ");
  Serial.println(operationMode);
  Serial.print("Buzzer: ");
  Serial.println(buzzerOnOff);
  Serial.print("Table: ");
  Serial.println(tableNumber);
  Serial.print("Players Count: ");
  Serial.println(playersCount);
  Serial.print("Current Timer Value: ");
  Serial.println(timerCurrent);
  Serial.print("Using Timer: ");
  Serial.println(pokerTimer1or2 == pokerTimer1 ? "T1" : "T2");

  diagEEPROM();
}

/*
void readPokerLife(){
  readClockLife = EEPROM.read(memAddressClock);
  readVolt      = EEPROM.read(memAddressVolt);
  readPercent   = EEPROM.read(memAddressPercent);

  Serial.print("PokerClock lived for: ");
  Serial.print(readClockLife);
  Serial.print(" min, ");
  Serial.print(readVolt);
  Serial.print("V, ");
  Serial.print(readPercent);
  Serial.println("%");
}

void writePokerLife(){
  if(currentMillis - previousMillisLife >= timeLife_60){
    previousMillisLife = currentMillis;
    lastClockLife = lastClockLife + 1;
   
    EEPROM.write(memAddressClock, lastClockLife);
    EEPROM.write(memAddressPercent, lastPercent);
    EEPROM.write(memAddressVolt, lastVolt);

    if (EEPROM.commit()) {
      Serial.println("EEPROM successfully committed");
      Serial.print("Life time wrote : ");
      Serial.print(lastClockLife);
      Serial.print(" min, ");
      Serial.print(lastVolt);
      Serial.print("V, ");
      Serial.print(lastPercent);
      Serial.println("%");
    } else {
      Serial.println("ERROR! EEPROM commit failed");
    }
  }
}

*/

//works only on LILYGO Mini D1 Plus
/*
uint32_t readADC_Cal(int ADC_Raw)
{
    esp_adc_cal_characteristics_t adc_chars;

    esp_adc_cal_characterize(ADC_UNIT_1, ADC_ATTEN_DB_11, ADC_WIDTH_BIT_12, 1100, &adc_chars);
    return (esp_adc_cal_raw_to_voltage(ADC_Raw, &adc_chars));
}
*/

void checkIsDischarging(){
    tempVoltageActual = readVoltage(); //Only works on WeMos ESP8266 ESP-WROOM-02
    if (tempVoltageOld > tempVoltageActual){
      Serial.println("Discharging!");
      //Serial.println(tempVoltageOld - tempVoltageActual);
      isDisCharging = 1;
    }
    if (tempVoltageOld < tempVoltageActual){
      Serial.println("Charging!");
      //Serial.println(tempVoltageOld - tempVoltageActual);
      isDisCharging = 0;
    }
    if (tempVoltageOld == tempVoltageActual){
      Serial.println("Stationary Charge!");
      //Serial.println(tempVoltageOld - tempVoltageActual);
      isDisCharging = 0;
    }
    tempVoltageOld = tempVoltageActual;
}

void setTimeScreen(uint8_t time1or2){//This will show "t1" or "t2"
  for(int i = 0; i <= LED_MODULES; i++){
    clear_module_leds(i);
  }

    pixels.setPixelColor(0, pixels.Color(255,255,255));  //B  A  C
    pixels.setPixelColor(1, pixels.Color(0,0,0));  //E  D  F
    pixels.setPixelColor(2, pixels.Color(255,0,255));  //DP  G  NC

  if(time1or2 == 1){
    pixels.setPixelColor(3, pixels.Color(0,255,0));  //B  A  C
    pixels.setPixelColor(4, pixels.Color(255,255,255));  //E  D  F
    pixels.setPixelColor(5, pixels.Color(255,255,255));  //DP  G  NC
  }
  if(time1or2 == 2){
    pixels.setPixelColor(3, pixels.Color(0,0,255));  //B  A  C
    pixels.setPixelColor(4, pixels.Color(0,0,255));  //E  D  F
    pixels.setPixelColor(5, pixels.Color(255,0,255));  //DP  G  NC
  }
    pixels.show();
}

void buzzerOnOffScreen(uint8_t OnOff){//This will show "b0" for "Buzzer OFF" or "b1" for "Buzzer ON"
    pixels.setPixelColor(0, pixels.Color(255,255,0));  //B  A  C
    pixels.setPixelColor(1, pixels.Color(0,0,0));  //E  D  F
    pixels.setPixelColor(2, pixels.Color(255,0,255));  //DP  G  NC

  if(OnOff == 0){
    pixels.setPixelColor(3, pixels.Color(0,0,0));  //B  A  C
    pixels.setPixelColor(4, pixels.Color(0,0,0));  //E  D  F
    pixels.setPixelColor(5, pixels.Color(0,255,0));  //DP  G  NC
  }
  else{
    pixels.setPixelColor(3, pixels.Color(0,255,0));  //B  A  C
    pixels.setPixelColor(4, pixels.Color(255,255,255));  //E  D  F
    pixels.setPixelColor(5, pixels.Color(255,255,255));  //DP  G  NC
  }
    pixels.show();
}

void lowVoltageScreen(){  //This will show "LO" as for "Low voltage"
    pixels.setPixelColor(0, pixels.Color(255,255,255));  //B  A  C
    pixels.setPixelColor(1, pixels.Color(0,0,0));  //E  D  F
    pixels.setPixelColor(2, pixels.Color(255,255,255));  //DP  G  NC

    pixels.setPixelColor(3, pixels.Color(0,0,0));  //B  A  C
    pixels.setPixelColor(4, pixels.Color(0,0,0));  //E  D  F
    pixels.setPixelColor(5, pixels.Color(255,255,255));  //DP  G  NC

    pixels.show();
}

float filterVoltage() {
    float sum = 0;
    for (int i = 0; i < VOLTAGE_SAMPLES; i++) {
        sum += (float)analogRead(voltagePin) * 0.0041015625;
        delay(10);
    }
    return sum / VOLTAGE_SAMPLES;
}

float readVoltage(){//Only works on WeMos ESP8266 ESP-WROOM-02
      //int nVoltageRaw = analogRead(voltagePin);
      //lastVolt = (float)nVoltageRaw * 0.0041015625; //remember to apply 100k ohms resister to the A0 to positive of the battery
      lastVolt = filterVoltage();

      float fVoltageMatrix[22][2] = {
        {4.2,  100},
        {4.15, 95},
        {4.11, 90},
        {4.08, 85},
        {4.02, 80},
        {3.98, 75},
        {3.95, 70},
        {3.91, 65},
        {3.87, 60},
        {3.85, 55},
        {3.84, 50},
        {3.82, 45},
        {3.80, 40},
        {3.79, 35},
        {3.77, 30},
        {3.75, 25},
        {3.73, 20},
        {3.71, 15},
        {3.69, 10},
        {3.61, 5},
        {3.27, 0},
        {0, 0}
      };

    uint8_t i;
    lastPercent = 0;

    for(i = 0; fVoltageMatrix[i][0] > 0; i++) {
      if(lastVolt >= fVoltageMatrix[i][0]) {
        lastPercent = fVoltageMatrix[i][1];
        break;
      }
    }
     
    Serial.println("");
    Serial.print("Voltage ");
    Serial.print(lastVolt);
    Serial.print("V, Charge ");
    Serial.print(lastPercent);
    Serial.println("%");

    return lastVolt;
}


void enableWiFiImmediately() {
  Serial.println("Enabling WiFi immediately...");
  
  // Interrompi la modalità sleep forzata se attiva
  WiFi.forceSleepWake();
  delay(100);
  
  // Assicurati che il WiFi sia in modalità STA (Station)
  WiFi.mode(WIFI_STA);
  delay(100);
  
  // Imposta l'hostname
  WiFi.hostname(hostname);
  
  // Avvia il processo di connessione WiFi
  wifiSetupInProgress = true;
  wifiSetupStartTime = millis();
  
  // Tentativo iniziale di connessione
  if (WiFi.status() != WL_CONNECTED) {
    WiFi.begin();  // Prova a connettersi usando le credenziali salvate
    Serial.println("Attempting to connect to saved WiFi network...");
  }
  
  Serial.println("WiFi enabled successfully");
}


void disableWiFiCompletely() {
  Serial.println("Disabling WiFi completely...");
  
  // Prima disattiviamo l'AP se attivo
  WiFi.softAPdisconnect(true);
  delay(100);
  
  // Poi ci disconnettiamo da qualsiasi rete
  WiFi.disconnect(true);
  delay(100);
  
  // Disattiviamo la modalità Station
  WiFi.mode(WIFI_OFF);
  delay(100);
  
  // Forziamo una disattivazione più profonda chiamando espressamente la funzione di disattivazione
  WiFi.forceSleepBegin();
  delay(100);
  
  wifiAPMode = false;
  wifiSetupInProgress = false;
  
  Serial.println("WiFi disabled and put into deep sleep mode");
}


// Funzione per abilitare/disabilitare il WiFi
void toggleWiFi() {
  wifiEnabled = !wifiEnabled;
  
  if (wifiEnabled) {
    setupWiFi();
  } else {
    WiFi.disconnect(true);
    WiFi.mode(WIFI_OFF);
    Serial.println("WiFi disabled");
  }
  
  // Salva l'impostazione in EEPROM
  EEPROM.write(memAddressWiFiState, wifiEnabled);
  EEPROM.commit();
}





void setupWiFi() {
  // Configurazione WiFi con WiFiManager
  Serial.println("Setting up WiFi...");
  
  // Imposta il nome dell'access point e della password
  wifiManager.setAPStaticIPConfig(IPAddress(192,168,4,1), IPAddress(192,168,4,1), IPAddress(255,255,255,0));
  
  // Crea un nome AP univoco basato sul MAC address
  String uniqueAPName = getUniqueAPName();
  
  wifiManager.setAPCallback([uniqueAPName](WiFiManager *wifiManager) {
    Serial.println("WiFi not configured. Starting config portal...");
    Serial.print("Connect to AP: ");
    Serial.println(uniqueAPName);
  });
  
  // Timeout dopo 3 minuti di configurazione
  wifiManager.setConfigPortalTimeout(180);
  
  // Tenta di connettere alla rete WiFi memorizzata
  // Se fallisce, crea un Access Point con il nome specifico e univoco
  if (!wifiManager.autoConnect(uniqueAPName.c_str())) {
    Serial.println("Failed to connect to WiFi and timeout reached");
    delay(1000);
    ESP.restart();  // Riavvia l'ESP se non riesce a connettersi
  }
  
  // Se siamo qui, ci siamo connessi con successo
  Serial.println("WiFi connected");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
  
  // Imposta il nome host
  WiFi.hostname(hostname);
  
  // Inizializza il server web
  setupWebServer();
}


void setupWebServer() {
  // Rotta per la pagina principale
  server.on("/", HTTP_GET, []() {
    // Rileggi i valori da EEPROM prima di renderizzare la pagina
    readPokerTimerParams();
    
    String html = "<!DOCTYPE html><html><head>";
    html += "<meta name='viewport' content='width=device-width, initial-scale=1'>";
    html += "<title>Poker Timer Setup</title>";
    html += "<style>";
    html += "body{font-family:Arial,sans-serif;margin:0;padding:15px;background:#f5f5f5;color:#333}";
    html += ".container{max-width:700px;margin:0 auto}";
    html += ".card{background:white;border-radius:8px;padding:15px;margin-bottom:15px;box-shadow:0 1px 3px rgba(0,0,0,0.1)}";
    html += "h1,h2{color:#444}h1{text-align:center}";
    html += ".tabs{display:flex;margin-bottom:20px;border-bottom:1px solid #ddd}";
    html += ".tab{padding:10px 20px;cursor:pointer;background:#f8f9fa;border:1px solid #ddd;border-bottom:none;margin-right:5px;border-radius:4px 4px 0 0}";
    html += ".tab.active{background:white;border-bottom:1px solid white;margin-bottom:-1px;font-weight:bold;color:#007bff}";
    html += ".tab-content{display:none;padding:15px 0}";
    html += ".tab-content.active{display:block}";
    html += "label{display:block;margin:10px 0 5px;font-weight:bold}";
    html += "input,select{width:100%;padding:8px;border:1px solid #ddd;border-radius:4px;box-sizing:border-box}";
    html += "button{background:#4CAF50;color:white;padding:10px;border:none;border-radius:4px;cursor:pointer;width:100%;font-size:16px;margin:10px 0}";
    html += "button:hover{background:#45a049}";
    html += "#resetBtn{background:#dc3545;color:white}";
    html += "#resetBtn:hover{background:#c82333}";
    html += ".alert{padding:15px;margin-bottom:20px;border:1px solid transparent;border-radius:4px}";
    html += ".alert-danger{color:#721c24;background-color:#f8d7da;border-color:#f5c6cb}";
    html += "</style></head><body>";
    
    html += "<div class='container'>";
    html += "<h1>Timer Details - Table " + String(tableNumber) + "</h1>";
    
    // Tab navigation - removed Controls tab
    html += "<div class='tabs'>";
    html += "<div class='tab active' onclick='showTab(\"settings\")'>Settings</div>";
    html += "<div class='tab' onclick='showTab(\"advanced\")'>Advanced</div>";
    html += "</div>";
    
    // Settings tab content
    html += "<div id='settings-tab' class='tab-content active'>";
    html += "<h2>Timer Settings</h2>";
    html += "<form id='settings-form' onsubmit='return saveSettings()'>";
    html += "<label for='mode'>Operation Mode:</label>";
    html += "<select id='mode' name='mode'>";
    html += "<option value='1'" + String(operationMode == 1 ? " selected" : "") + ">Mode 1: T1/T2 with automatic start</option>";
    html += "<option value='2'" + String(operationMode == 2 ? " selected" : "") + ">Mode 2: T1/T2 with manual start</option>";
    html += "<option value='3'" + String(operationMode == 3 ? " selected" : "") + ">Mode 3: T1 only with automatic start</option>";
    html += "<option value='4'" + String(operationMode == 4 ? " selected" : "") + ">Mode 4: T1 only with manual start</option>";
    html += "</select>";
    
    html += "<label for='t1'>T1 Value (seconds):</label>";
    html += "<input type='number' id='t1' name='t1' min='5' max='95' step='5' value='" + String(pokerTimer1) + "'>";
    
    html += "<label for='t2'>T2 Value (seconds):</label>";
    html += "<input type='number' id='t2' name='t2' min='5' max='95' step='5' value='" + String(pokerTimer2) + "'>";
    
    html += "<label for='tableNumber'>Table Number (0-99):</label>";
    html += "<input type='number' id='tableNumber' name='tableNumber' min='0' max='99' value='" + String(tableNumber) + "'>";
    
    html += "<label for='buzzer'>Buzzer:</label>";
    html += "<select id='buzzer' name='buzzer'>";
    html += "<option value='1'" + String(buzzerOnOff ? " selected" : "") + ">Enabled</option>";
    html += "<option value='0'" + String(!buzzerOnOff ? " selected" : "") + ">Disabled</option>";
    html += "</select>";
    
    html += "<button type='submit'>Save Settings</button>";
    html += "</form></div>";
    
    // Advanced tab content
    html += "<div id='advanced-tab' class='tab-content'>";
    html += "<h2>Advanced Options</h2>";
    html += "<div class='alert alert-danger'>";
    html += "<strong>Warning:</strong> Factory Reset will restore ALL settings to defaults.<br>This action cannot be undone!";
    html += "</div>";
    html += "<button id='resetBtn' onclick='confirmReset()'>Factory Reset</button>";
    html += "</div>";
    
    // Informazioni sul timer
    html += "<div class='card'>";
    html += "<div style='display:flex;flex-wrap:wrap;gap:10px;margin-bottom:10px'>";
    html += "<div>Mode: " + String(operationMode) + "</div>";
    html += "<div>T1: " + String(pokerTimer1) + "s</div>";
    html += "<div>T2: " + String(pokerTimer2) + "s</div>";
    html += "<div>Battery: " + String(lastPercent) + "%</div>";
    html += "<div>WiFi: " + String(WiFi.RSSI()) + " dBm</div>";
    html += "<div>IP: " + WiFi.localIP().toString() + "</div>";
    html += "<div>Voltage: " + String(lastVolt) + "V</div>";
    html += "<div>Status: " + String(isStarted ? (isPaused ? "Paused" : "Running") : "Stopped") + "</div>";
    html += "</div>";
    html += "</div>";
    
    // JavaScript per la pagina
    html += "<script>";
    // Funzione per cambiare tab
    html += "function showTab(tabName) {";
    html += "  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));";
    html += "  document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));";
    html += "  if (tabName === 'settings') {";
    html += "    document.querySelector('.tab:nth-child(1)').classList.add('active');";
    html += "    document.getElementById('settings-tab').classList.add('active');";
    html += "  } else if (tabName === 'advanced') {";
    html += "    document.querySelector('.tab:nth-child(2)').classList.add('active');";
    html += "    document.getElementById('advanced-tab').classList.add('active');";
    html += "  }";
    html += "}";
    
    // Funzione per salvare le impostazioni
    html += "function saveSettings() {";
    html += "  var form = document.getElementById('settings-form');";
    html += "  var formData = new FormData(form);";
    html += "  var settings = {};";
    html += "  formData.forEach((value, key) => { settings[key] = value; });";
    html += "  console.log('Settings to save: ', settings);";
    html += "  var xhr = new XMLHttpRequest();";
    html += "  xhr.open('POST', '/save');";
    html += "  xhr.onload = function() {";
    html += "    if (xhr.status === 200) {";
    html += "      var response = xhr.responseText;";
    html += "      console.log('Settings saved on server: ', response);";
    html += "      window.location.href = '/?nocache=' + new Date().getTime();";
    html += "    }";
    html += "  };";
    html += "  xhr.send(formData);";
    html += "  return false;"; // Previene l'invio standard del form
    html += "}";
    
    // Funzione per confermare il factory reset
    html += "function confirmReset() {";
    html += "  if (confirm('Are you sure you want to reset all settings to factory defaults? This action cannot be undone.')) {";
    html += "    window.location.href = '/factory-reset';";
    html += "  }";
    html += "}";
    html += "</script>";
    
    html += "</div></body></html>";
    
    server.send(200, "text/html", html);
  });

  // Endpoint API per lo stato attuale
  server.on("/status", HTTP_GET, []() {
    String json = "{";
    json += "\"mode\":" + String(operationMode) + ",";
    json += "\"t1\":" + String(pokerTimer1) + ",";
    json += "\"t2\":" + String(pokerTimer2) + ",";
    json += "\"buzzer\":" + String(buzzerOnOff) + ",";
    json += "\"battery\":" + String(lastPercent) + ",";
    json += "\"voltage\":" + String(lastVolt) + ",";
    json += "\"timer\":" + String(timerCurrent) + ",";
    json += "\"isPaused\":" + String(isPaused) + ",";
    json += "\"isStarted\":" + String(isStarted) + ",";
    json += "\"tableNumber\":" + String(tableNumber) + ",";
    json += "\"wifiSignal\":" + String(WiFi.RSSI());
    json += "}";
    server.send(200, "application/json", json);
  });

  // Rotta per salvare le impostazioni - VERSIONE COMPLETAMENTE RISCRITTA
server.on("/save", HTTP_POST, []() {
  // Leggiamo direttamente i valori dal form
  int newMode = server.hasArg("mode") ? server.arg("mode").toInt() : operationMode;
  int newT1 = server.hasArg("t1") ? server.arg("t1").toInt() : pokerTimer1;
  int newT2 = server.hasArg("t2") ? server.arg("t2").toInt() : pokerTimer2;
  int newTableNumber = server.hasArg("tableNumber") ? server.arg("tableNumber").toInt() : tableNumber;
  uint8_t newBuzzerState = server.hasArg("buzzer") ? (server.arg("buzzer").toInt() ? 1 : 0) : buzzerOnOff;
  
  // Stampiamo i valori ricevuti
  Serial.println("==== Received values from form ====");
  Serial.print("New Mode: "); Serial.println(newMode);
  Serial.print("New T1: "); Serial.println(newT1);
  Serial.print("New T2: "); Serial.println(newT2);
  Serial.print("New Table: "); Serial.println(newTableNumber);
  Serial.print("New Buzzer: "); Serial.println(newBuzzerState);
  
  // Validazione dei valori
  if (newMode < 1 || newMode > 4) {
    Serial.println("Invalid mode value! Using default.");
    newMode = operationMode;
  }
  
  if (newT1 < 5 || newT1 > 95 || newT1 % 5 != 0) {
    Serial.println("Invalid T1 value! Using default.");
    newT1 = pokerTimer1;
  }
  
  if (newT2 < 5 || newT2 > 95 || newT2 % 5 != 0) {
    Serial.println("Invalid T2 value! Using default.");
    newT2 = pokerTimer2;
  }
  
  if (newTableNumber < 0 || newTableNumber > 99) {
    Serial.println("Invalid table number! Using default.");
    newTableNumber = tableNumber;
  }
  
  // Valori originali prima delle modifiche
  Serial.println("==== Original values ====");
  Serial.print("Mode: "); Serial.println(operationMode);
  Serial.print("T1: "); Serial.println(pokerTimer1);
  Serial.print("T2: "); Serial.println(pokerTimer2);
  Serial.print("Table: "); Serial.println(tableNumber);
  Serial.print("Buzzer: "); Serial.println(buzzerOnOff);
  
  // Impostiamo direttamente i valori
  bool settingsChanged = false;
  
  if (newMode != operationMode) {
    operationMode = newMode;
    settingsChanged = true;
  }
  
  if (newT1 != pokerTimer1) {
    pokerTimer1 = newT1;
    settingsChanged = true;
  }
  
  if (newT2 != pokerTimer2) {
    pokerTimer2 = newT2;
    settingsChanged = true;
  }
  
  if (newTableNumber != tableNumber) {
    tableNumber = newTableNumber;
    settingsChanged = true;
  }
  
  if (newBuzzerState != buzzerOnOff) {
    buzzerOnOff = newBuzzerState;
    settingsChanged = true;
  }
  
  if (!settingsChanged) {
    Serial.println("No settings changed, nothing to save.");
    server.send(200, "application/json", "{\"status\":\"success\",\"message\":\"No changes detected\"}");
    return;
  }
  
  // Prima di scrivere in EEPROM, verifichiamo i valori in memoria
  Serial.println("==== Values in memory before write ====");
  Serial.print("Mode: "); Serial.println(operationMode);
  Serial.print("T1: "); Serial.println(pokerTimer1);
  Serial.print("T2: "); Serial.println(pokerTimer2);
  Serial.print("Table: "); Serial.println(tableNumber);
  Serial.print("Buzzer: "); Serial.println(buzzerOnOff);
  
  // Prova a salvare fino a 3 volte se necessario
  bool saveSuccess = false;
  for (int attempt = 1; attempt <= 3 && !saveSuccess; attempt++) {
    Serial.print("EEPROM save attempt #"); 
    Serial.println(attempt);
    
    // Reinizializza EEPROM ad ogni tentativo
    EEPROM.begin(512);
    
    // Scriviamo direttamente in EEPROM
    EEPROM.write(memAddressTimer1, pokerTimer1);
    EEPROM.write(memAddressTimer2, pokerTimer2);
    EEPROM.write(memAddressBuzzerState, buzzerOnOff);
    EEPROM.write(memAddressOperationMode, operationMode);
    EEPROM.write(memAddressTableNumber, tableNumber);
    EEPROM.write(memAddressWiFiState, wifiEnabled ? 1 : 0);
    
    // Committiamo le modifiche
    bool commitSuccess = EEPROM.commit();
    
    if (commitSuccess) {
      Serial.println("EEPROM commit successful");
    } else {
      Serial.println("ERROR: EEPROM commit failed!");
      continue; // Salta alla prossima iterazione se il commit fallisce
    }
    
    // Verifica immediata
    delay(100); // Piccola pausa
    
    uint8_t verifyT1 = EEPROM.read(memAddressTimer1);
    uint8_t verifyT2 = EEPROM.read(memAddressTimer2);
    uint8_t verifyMode = EEPROM.read(memAddressOperationMode);
    uint8_t verifyTable = EEPROM.read(memAddressTableNumber);
    uint8_t verifyBuzzer = EEPROM.read(memAddressBuzzerState);
    
    Serial.println("==== Direct EEPROM verification ====");
    Serial.print("T1 expected: "); Serial.print(pokerTimer1); Serial.print(" | Read: "); Serial.println(verifyT1);
    Serial.print("T2 expected: "); Serial.print(pokerTimer2); Serial.print(" | Read: "); Serial.println(verifyT2);
    Serial.print("Mode expected: "); Serial.print(operationMode); Serial.print(" | Read: "); Serial.println(verifyMode);
    Serial.print("Table expected: "); Serial.print(tableNumber); Serial.print(" | Read: "); Serial.println(verifyTable);
    Serial.print("Buzzer expected: "); Serial.print(buzzerOnOff); Serial.print(" | Read: "); Serial.println(verifyBuzzer);
    
    // Se ci sono problemi con la verifica, passeremo al prossimo tentativo
    if (verifyT1 != pokerTimer1 || verifyT2 != pokerTimer2 || 
        verifyMode != operationMode || verifyTable != tableNumber || 
        verifyBuzzer != buzzerOnOff) {
      
      Serial.println("WARNING: Verification failed, trying again...");
      delay(50); // Pausa prima del prossimo tentativo
    } else {
      // Tutti i valori sono stati correttamente verificati
      Serial.println("All values verified correctly!");
      saveSuccess = true;
    }
  }
  
  if (saveSuccess) {
    Serial.println("EEPROM save successful after attempts");
  } else {
    Serial.println("⚠️ EEPROM save failed after 3 attempts");
  }
  
  // Applica le impostazioni anche se il salvataggio non è riuscito
  // così almeno funzionano nella sessione corrente
  applySettingsImmediately();
  
  // Esegui una diagnostica EEPROM finale
  diagEEPROM();
  
  // Prepara la risposta JSON
  String jsonResponse = "{\"status\":\"" + String(saveSuccess ? "success" : "warning") + 
                        "\", \"message\":\"" + String(saveSuccess ? "Settings saved successfully" : "Settings applied but EEPROM save may have failed") + 
                        "\", \"settings\": {";
  jsonResponse += "\"mode\":" + String(operationMode) + ",";
  jsonResponse += "\"t1\":" + String(pokerTimer1) + ",";
  jsonResponse += "\"t2\":" + String(pokerTimer2) + ",";
  jsonResponse += "\"tableNumber\":" + String(tableNumber) + ",";
  jsonResponse += "\"buzzer\":" + String(buzzerOnOff);
  jsonResponse += "}}";
  
  // Invia risposta al client
  server.send(200, "application/json", jsonResponse);
});


  // Rotta per factory reset
  server.on("/factory-reset", HTTP_GET, []() {
    server.send(200, "text/html", "<html><head><meta http-equiv='refresh' content='5;url=/'><style>body{font-family:Arial;text-align:center;margin-top:50px;}</style></head><body><h3>Factory Reset...</h3><p>Your device will restart in a few seconds.</p></body></html>");
    delay(500);
    performFactoryReset();
  });

  // Endpoint per avviare/riprendere il timer
  server.on("/start", HTTP_GET, []() {
    if (isPaused) {
      isPaused = false;
      isStarted = true;
    } else if (!isStarted) {
      isStarted = true;
      isPaused = false;
      timeExpired = false;
      timerCurrent = pokerTimer1;
    }
    server.send(200, "text/plain", "Timer started");
  });

  // Endpoint per mettere in pausa il timer
  server.on("/pause", HTTP_GET, []() {
    if (isStarted && !isPaused) {
      isPaused = true;
    }
    server.send(200, "text/plain", "Timer paused");
  });

  // Endpoint per comando generico
  server.on("/command", HTTP_POST, []() {
    if (server.hasArg("cmd")) {
      String cmd = server.arg("cmd");
      
      if (cmd == "start") {
        if (isPaused) {
          isPaused = false;
          isStarted = true;
        } else if (!isStarted) {
          isStarted = true;
          isPaused = false;
          timeExpired = false;
          timerCurrent = pokerTimer1;
        }
      } else if (cmd == "pause") {
        if (isStarted && !isPaused) {
          isPaused = true;
        }
      } else if (cmd == "reset") {
        isStarted = false;
        isPaused = true;
        timeExpired = false;
        setTimer(pokerTimer1, 1);
      } else if (cmd == "toggle_buzzer") {
        buzzerOnOff = !buzzerOnOff;
        writePokerTimerParams();
      }
    }
    
    server.send(200, "text/plain", "Command executed");
  });

  // Endpoint per aggiornare il firmware
  server.on("/update", HTTP_GET, []() {
    String html = "<!DOCTYPE html><html><head>";
    html += "<meta name='viewport' content='width=device-width, initial-scale=1'>";
    html += "<title>Firmware Update</title>";
    html += "<style>";
    html += "body{font-family:Arial,sans-serif;margin:0;padding:15px;background:#f5f5f5;color:#333}";
    html += ".container{max-width:700px;margin:0 auto;background:white;padding:20px;border-radius:8px;box-shadow:0 1px 3px rgba(0,0,0,0.1)}";
    html += "h1{text-align:center;color:#444}";
    html += "form{margin:20px 0}";
    html += "input[type=file]{display:block;margin:20px 0}";
    html += "button{background:#4CAF50;color:white;padding:10px 15px;border:none;border-radius:4px;cursor:pointer;font-size:16px}";
    html += ".progress{width:100%;height:20px;background:#f0f0f0;border-radius:4px;margin:20px 0;overflow:hidden}";
    html += ".bar{width:0%;height:100%;background:#4CAF50}";
    html += ".alert{padding:15px;margin:15px 0;border-radius:4px}";
    html += ".alert-info{background:#d1ecf1;color:#0c5460}";
    html += "</style></head><body>";
    
    html += "<div class='container'>";
    html += "<h1>Firmware Update</h1>";
    html += "<div class='alert alert-info'>";
    html += "<strong>Note:</strong> Upload the new firmware file (.bin) to update the device.";
    html += "</div>";
    html += "<form method='POST' action='/update' enctype='multipart/form-data' id='upload-form'>";
    html += "<input type='file' name='update' accept='.bin'>";
    html += "<button type='submit'>Update Firmware</button>";
    html += "</form>";
    html += "<div class='progress'><div class='bar' id='progress-bar'></div></div>";
    html += "<div id='status'></div>";
    html += "</div>";
    
    html += "<script>";
    html += "document.getElementById('upload-form').addEventListener('submit', function(e) {";
    html += "  e.preventDefault();";
    html += "  var form = document.getElementById('upload-form');";
    html += "  var formData = new FormData(form);";
    html += "  var xhr = new XMLHttpRequest();";
    html += "  xhr.open('POST', '/update');";
    html += "  xhr.upload.addEventListener('progress', function(e) {";
    html += "    if (e.lengthComputable) {";
    html += "      var percent = (e.loaded / e.total) * 100;";
    html += "      document.getElementById('progress-bar').style.width = percent + '%';";
    html += "      document.getElementById('status').innerHTML = 'Uploading: ' + Math.round(percent) + '%';";
    html += "    }";
    html += "  });";
    html += "  xhr.onreadystatechange = function() {";
    html += "    if (xhr.readyState === 4) {";
    html += "      if (xhr.status === 200) {";
    html += "        document.getElementById('status').innerHTML = 'Update successful! Device will restart...';";
    html += "      } else {";
    html += "        document.getElementById('status').innerHTML = 'Error during update. Please try again.';";
    html += "      }";
    html += "    }";
    html += "  };";
    html += "  xhr.send(formData);";
    html += "});";
    html += "</script>";
    html += "</body></html>";
    
    server.send(200, "text/html", html);
  });

  // Gestione dell'aggiornamento firmware
  server.on("/update", HTTP_POST, []() {
    server.sendHeader("Connection", "close");
    server.send(200, "text/plain", (Update.hasError()) ? "Update failed!" : "Update successful! Rebooting...");
    delay(1000);
    ESP.restart();
  }, []() {
    HTTPUpload& upload = server.upload();
    if (upload.status == UPLOAD_FILE_START) {
      Serial.printf("Update: %s\n", upload.filename.c_str());
    if (!Update.begin((ESP.getFreeSketchSpace() - 0x1000) & 0xFFFFF000)) {
        Update.printError(Serial);
      }
    } else if (upload.status == UPLOAD_FILE_WRITE) {
      if (Update.write(upload.buf, upload.currentSize) != upload.currentSize) {
        Update.printError(Serial);
      }
    } else if (upload.status == UPLOAD_FILE_END) {
      if (Update.end(true)) { //true to set the size to the current progress
        Serial.printf("Update Success: %u\nRebooting...\n", upload.totalSize);
      } else {
        Update.printError(Serial);
      }
    }
  });

  // Configurazione WiFi
  server.on("/wifi-config", HTTP_GET, []() {
    String html = "<!DOCTYPE html><html><head>";
    html += "<meta name='viewport' content='width=device-width, initial-scale=1'>";
    html += "<title>WiFi Configuration</title>";
    html += "<style>";
    html += "body{font-family:Arial,sans-serif;margin:0;padding:15px;background:#f5f5f5;color:#333}";
    html += ".container{max-width:700px;margin:0 auto;background:white;padding:20px;border-radius:8px;box-shadow:0 1px 3px rgba(0,0,0,0.1)}";
    html += "h1{text-align:center;color:#444}";
    html += "label{display:block;margin:10px 0 5px;font-weight:bold}";
    html += "input{width:100%;padding:8px;border:1px solid #ddd;border-radius:4px;box-sizing:border-box}";
    html += "button{background:#4CAF50;color:white;padding:10px 15px;border:none;border-radius:4px;cursor:pointer;width:100%;font-size:16px;margin:15px 0}";
    html += "#scanBtn{background:#007bff}";
    html += ".networks{border:1px solid #ddd;margin-top:10px;max-height:150px;overflow-y:auto;border-radius:4px;margin-bottom:15px}";
    html += ".network{padding:8px;border-bottom:1px solid #eee;cursor:pointer}";
    html += ".network:hover{background:#f5f5f5}";
    html += ".checkbox{display:flex;align-items:center;margin:10px 0}";
    html += ".checkbox input{width:auto;margin-right:8px}";
    html += "</style></head><body>";
    
    html += "<div class='container'>";
    html += "<h1>WiFi Configuration</h1>";
    html += "<form action='/save-wifi' method='post'>";
    html += "<label for='ssid'>Network Name (SSID):</label>";
    html += "<input type='text' id='ssid' name='ssid' required>";
    
    html += "<label for='password'>Password:</label>";
    html += "<input type='password' id='password' name='password'>";
    
    html += "<div class='checkbox'>";
    html += "<input type='checkbox' id='show-pwd' onclick='togglePassword()'>";
    html += "<label for='show-pwd'>Show password</label>";
    html += "</div>";
    
    html += "<button type='button' id='scanBtn' onclick='scanNetworks()'>Scan for Networks</button>";
    html += "<div class='networks' id='networks'></div>";
    
    html += "<button type='submit'>Save and Connect</button>";
    html += "</form>";
    html += "</div>";
    html += "<script>";
    html += "function togglePassword() {";
    html += "  var pwdField = document.getElementById('password');";
    html += "  pwdField.type = pwdField.type === 'password' ? 'text' : 'password';";
    html += "}";
    
    html += "function scanNetworks() {";
    html += "  document.getElementById('networks').innerHTML = '<p style=\"text-align:center\">Scanning...</p>';";
    html += "  var xhr = new XMLHttpRequest();";
    html += "  xhr.open('GET', '/scan-wifi');";
    html += "  xhr.onload = function() {";
    html += "    if (xhr.status === 200) {";
    html += "      var response = JSON.parse(xhr.responseText);";
    html += "      var html = '';";
    html += "      if (response.networks && response.networks.length) {";
    html += "        for (var i = 0; i < response.networks.length; i++) {";
    html += "          html += '<div class=\"network\" onclick=\"document.getElementById(\\'ssid\\').value=\\'' + response.networks[i] + '\\'\">' + response.networks[i] + '</div>';";
    html += "        }";
    html += "      } else {";
    html += "        html = '<p style=\"text-align:center\">No networks found</p>';";
    html += "      }";
    html += "      document.getElementById('networks').innerHTML = html;";
    html += "    }";
    html += "  };";
    html += "  xhr.send();";
    html += "}";
    html += "</script>";
    html += "</body></html>";
    
    server.send(200, "text/html", html);
  });

  // Rotta per scansionare le reti WiFi
  server.on("/scan-wifi", HTTP_GET, []() {
    String json = "{\"networks\":[";
    int n = WiFi.scanNetworks();
    
    if (n > 0) {
      for (int i = 0; i < n; i++) {
        if (i > 0) json += ",";
        json += "\"" + WiFi.SSID(i) + "\"";
      }
    }
    
    json += "]}";
    server.send(200, "application/json", json);
  });
   
  // Rotta per salvare le impostazioni WiFi
  server.on("/save-wifi", HTTP_POST, []() {
    String ssid = server.arg("ssid");
    String password = server.arg("password");
    
    if (ssid.length() > 0) {
      saveWiFiCredentials(ssid.c_str(), password.c_str());
      
      String html = "<!DOCTYPE html><html><head>";
      html += "<meta http-equiv='refresh' content='10;url=/'>";
      html += "<style>body{font-family:Arial;text-align:center;margin:0;padding:20px;background:#f5f5f5}";
      html += ".container{max-width:700px;margin:0 auto;background:white;padding:20px;border-radius:8px;box-shadow:0 1px 3px rgba(0,0,0,0.1)}";
      html += ".message{color:#155724;margin:20px 0}";
      html += ".spinner{border:4px solid #f3f3f3;border-top:4px solid #3498db;border-radius:50%;width:30px;height:30px;";
      html += "animation:spin 2s linear infinite;margin:15px auto}@keyframes spin{0%{transform:rotate(0deg)}100%{transform:rotate(360deg)}";
      html += "}</style></head><body><div class='container'>";
      html += "<div class='message'><h2>WiFi Configuration Saved</h2>";
      html += "<p>Connecting to <strong>" + ssid + "</strong>...</p>";
      html += "<div class='spinner'></div>";
      html += "<p>The timer will restart shortly.</p></div>";
      html += "</div></body></html>";
      
      server.send(200, "text/html", html);
      delay(1000);
      ESP.restart();
    } else {
      server.sendHeader("Location", "/wifi-config", true);
      server.send(302, "text/plain", "");
    }
  });

  server.on("/reset-eeprom", HTTP_GET, []() {
    resetEEPROM();
    server.send(200, "text/html", "<html><body><h2>EEPROM Reset Complete</h2><p>Device will restart...</p></body></html>");
    delay(1000);
    ESP.restart();
  });

  // Gestisci qualsiasi URL non riconosciuto
  server.onNotFound([]() {
    server.sendHeader("Location", "/", true);
    server.send(302, "text/plain", "");
  });
  
  server.begin();
  Serial.println("Web server started");
}



// Funzione dedicata per verificare se lo stato WiFi è cambiato
bool hasWiFiStateChanged() {
  uint8_t savedWiFiState = EEPROM.read(memAddressWiFiState);
  // Considera 255 (valore di default EEPROM) come 1 (ON)
  if (savedWiFiState == 255) savedWiFiState = 1;
  
  bool previousState = (savedWiFiState == 1);
  return (previousState != wifiEnabled);
}


// Funzione per forzare un reset hardware usando il watchdog timer
void forceHardReset() {
  // Mostra il messaggio di riavvio sul display
  showRestartMessage();
  
  Serial.println("Forcing hard reset via watchdog...");
  delay(1000);  // Tempo per mostrare il messaggio e completare la trasmissione seriale
  
  // Disabilita il watchdog e poi entra in un loop infinito
  // Questo causerà un timeout del watchdog e un reset hardware
  ESP.wdtDisable();
  while(1) {
    // Loop infinito - il watchdog resetterà il dispositivo
  }
  
  // Questa parte non verrà mai eseguita, ma la includiamo per completezza
  Serial.println("Should never reach here!");
}


// Funzione per forzare un reset hardware con un metodo drastico
void forceCrashReset() {
  // Mostra il messaggio di riavvio sul display
  showRestartMessage();
  
  Serial.println("Forcing crash reset...");
  delay(1000);  // Tempo per mostrare il messaggio e completare la trasmissione seriale
  
  // Metodo 1: Puntatore nullo
  int *nullPointer = NULL;
  *nullPointer = 42;  // Questo causerà un crash immediato
  
  // In caso il compilatore ottimizzi via la dereferenziazione del puntatore nullo, 
  // usiamo un metodo alternativo
  
  // Metodo 2: Chiamata a funzione in indirizzo invalido
  void (*resetFunc)() = (void(*)())0xFFFFFFFF;
  resetFunc();  // Salta a un indirizzo invalido, che causerà un crash
  
  // Il codice non dovrebbe mai arrivare qui
  Serial.println("Should never reach here!");
}


// Funzione per mostrare il messaggio di riavvio sul display
void showRestartMessage() {
  // Pulisci il display
  for(int i = 0; i < LED_MODULES; i++) {
    clear_module_leds(i);
  }
  
  // "r" sul primo digit
  pixels.setPixelColor(0, pixels.Color(255,0,0));  // r (simile a n)
  pixels.setPixelColor(1, pixels.Color(255,255,255));  // r
  pixels.setPixelColor(2, pixels.Color(255,0,255));  // r
  
  // "E" sul secondo digit
  pixels.setPixelColor(3, pixels.Color(0,0,0));  // E
  pixels.setPixelColor(4, pixels.Color(0,0,0));  // E
  pixels.setPixelColor(5, pixels.Color(255,0,255));  // E
  pixels.show();
  
  // Beep di conferma
  if(buzzerOnOff) {
    tone(buzzerPin, 800);
    delay(100);
    noTone(buzzerPin);
    delay(50);
    tone(buzzerPin, 1200);
    delay(100);
    noTone(buzzerPin);
  }
}


void saveWiFiCredentials(const char* ssid, const char* password) {
  WiFiCredentials credentials;
  
  // Copiare SSID e password nella struttura
  strncpy(credentials.ssid, ssid, sizeof(credentials.ssid) - 1);
  credentials.ssid[sizeof(credentials.ssid) - 1] = '\0';  // Assicura terminazione
  
  strncpy(credentials.password, password, sizeof(credentials.password) - 1);
  credentials.password[sizeof(credentials.password) - 1] = '\0';  // Assicura terminazione
  
  // Inizializza il filesystem SPIFFS
  if (!SPIFFS.begin()) {
    Serial.println("Failed to mount SPIFFS");
    return;
  }
  
  // Apri il file per scrittura (sovrascrivi se esistente)
  File file = SPIFFS.open("/wifi_credentials.dat", "w");
  if (!file) {
    Serial.println("Failed to open file for writing");
    return;
  }
  
  // Scrivi la struttura nel file
  file.write((uint8_t*)&credentials, sizeof(credentials));
  file.close();
  
  Serial.println("WiFi credentials saved to SPIFFS");
}

// Funzione per caricare le credenziali WiFi da SPIFFS
bool loadWiFiCredentials(char* ssid, char* password) {
  // Inizializza il filesystem SPIFFS
  if (!SPIFFS.begin()) {
    Serial.println("Failed to mount SPIFFS");
    return false;
  }
  
  // Verifica se il file esiste
  if (!SPIFFS.exists("/wifi_credentials.dat")) {
    Serial.println("WiFi credentials file not found");
    return false;
  }
  
  // Apri il file per lettura
  File file = SPIFFS.open("/wifi_credentials.dat", "r");
  if (!file) {
    Serial.println("Failed to open file for reading");
    return false;
  }
  
  // Leggi la struttura dal file
  WiFiCredentials credentials;
  if (file.read((uint8_t*)&credentials, sizeof(credentials)) != sizeof(credentials)) {
    Serial.println("Failed to read WiFi credentials");
    file.close();
    return false;
  }
  
  file.close();
  
  // Copia i valori nei buffer di output
  strncpy(ssid, credentials.ssid, 33);
  strncpy(password, credentials.password, 65);
  
  Serial.print("Loaded SSID: ");
  Serial.println(ssid);
  Serial.println("Loaded password (length): " + String(strlen(password)));
  
  return true;
}

// Funzione per eliminare le credenziali WiFi
void deleteWiFiCredentials() {
  Serial.println("Eliminazione credenziali WiFi...");
  
  // Formatta SPIFFS per eliminare tutti i file
  if (!SPIFFS.begin()) {
    Serial.println("Failed to mount SPIFFS");
    return;
  }
  
  Serial.println("Formatting SPIFFS...");
  SPIFFS.format();
  Serial.println("SPIFFS formatted");
  
  // Elimina anche le credenziali WiFi dal WiFiManager
  WiFi.disconnect(true);
  wifiManager.resetSettings();
  
  Serial.println("WiFi credentials deleted");
}

// Modifica alla funzione handleWiFiSetup
void handleWiFiSetup() {
  if (!wifiSetupInProgress) return;
  
  // Controlliamo lo stato del WiFi solo ogni 1 secondo
  if (millis() - lastWiFiStatusCheck < 1000) return;
  lastWiFiStatusCheck = millis();
  
  // Se siamo già connessi
  if (WiFi.status() == WL_CONNECTED) {
    if (wifiSetupInProgress) {
      Serial.println("WiFi connected!");
      Serial.print("IP address: ");
      Serial.println(WiFi.localIP());
      
      // Inizializza il server Web
      setupWebServer();
      Serial.println("HTTP server started");
      
      wifiSetupInProgress = false;
      wifiAPMode = false;
    }
    return;
  }
  
  // Gestione connessione WiFi
  static uint8_t connectionAttempts = 0;
  static bool credentialsChecked = false;
  static unsigned long connectionStartTime = 0;
  
  // Primo controllo se ci sono credenziali
  if (!credentialsChecked) {
    credentialsChecked = true;
    
    char ssid[33] = {0};
    char password[65] = {0};
    
    if (loadWiFiCredentials(ssid, password)) {
      Serial.print("Credentials found, trying to connect to: ");
      Serial.println(ssid);
      
      // Disconnetti eventuali connessioni precedenti
      WiFi.disconnect();
      delay(100);
      
      WiFi.mode(WIFI_STA);
      WiFi.hostname(hostname);
      
      // Avvia il tentativo di connessione
      WiFi.begin(ssid, password);
      connectionStartTime = millis();
      connectionAttempts = 1;
      
      // Mostra esplicitamente le credenziali usate
      Serial.print("SSID: ");
      Serial.println(ssid);
      Serial.print("Password length: ");
      Serial.println(strlen(password));
    } else {
      Serial.println("No credentials found, starting AP mode directly");
      startAPMode();
      connectionAttempts = 0;
      credentialsChecked = false;  // Reset per il prossimo avvio
      wifiSetupInProgress = false; // Terminato il setup
      return;
    }
  }
  
  // Se abbiamo credenziali, continuiamo a tentare la connessione
  if (connectionAttempts > 0) {
    // Aumentiamo il timeout a 180 tentativi (180 secondi)
    if (connectionAttempts < 180) {
      connectionAttempts++;
      
      // Mostra lo stato del WiFi
      wl_status_t status = WiFi.status();
      Serial.print("Connection attempt ");
      Serial.print(connectionAttempts);
      Serial.print("/180, status: ");
      
      switch (status) {
        case WL_CONNECTED:
          Serial.println("CONNECTED");
          break;
        case WL_NO_SSID_AVAIL:
          Serial.println("SSID NOT FOUND");
          break;
        case WL_CONNECT_FAILED:
          Serial.println("CONNECTION FAILED");
          break;
        case WL_IDLE_STATUS:
          Serial.println("IDLE");
          break;
        case WL_DISCONNECTED:
          Serial.println("DISCONNECTED");
          break;
        default:
          Serial.println(status);
      }
      
      // Se ci connettiamo, esci
      if (status == WL_CONNECTED) {
        connectionAttempts = 0;
        credentialsChecked = false;
      }
      // Se SSID non trovato o connessione fallita, passa subito a modalità AP
      else if (status == WL_NO_SSID_AVAIL || status == WL_CONNECT_FAILED) {
        Serial.println("Critical WiFi error, starting AP mode");
        connectionAttempts = 0;
        credentialsChecked = false;
        startAPMode();
        wifiSetupInProgress = false;
      }
    } else {
      // Dopo 20 tentativi falliti
      Serial.println("Failed to connect after 20 attempts, starting AP mode");
      connectionAttempts = 0;
      credentialsChecked = false;
      startAPMode();
      wifiSetupInProgress = false;
    }
  }
  
  // Timeout dopo 5 minuti
  if (millis() - wifiSetupStartTime > 300000) {
    Serial.println("WiFi setup timeout after 5 minutes");
    if (wifiAPMode) {
      WiFi.softAPdisconnect(true);
      wifiAPMode = false;
    }
    wifiSetupInProgress = false;
    connectionAttempts = 0;
    credentialsChecked = false;
  }
}

// Funzione per inviare lo stato del PokerTimer al server di monitoraggio
void sendStatusToServer() {
  // Verifica che il WiFi sia connesso
  if (WiFi.status() != WL_CONNECTED) {
    return;
  }
  
  // Verifica se il server è stato scoperto, altrimenti tenta la discovery
  if (!serverDiscovered && millis() - lastServerDiscoveryAttempt > SERVER_DISCOVERY_INTERVAL) {
    discoverServer();
  }
  
  // Se ancora non abbiamo trovato il server e non è passato troppo tempo dall'ultimo tentativo, esci
  if (!serverDiscovered) {
    Serial.println("No server discovered yet. Using default URL.");
    // Usa l'URL di default quando non è stato scoperto un server
    discoveredServerUrl = String(defaultMonitorServerUrl);
  }
  
  WiFiClient client;
  HTTPClient http;
  
  Serial.println("Sending status to server: " + discoveredServerUrl);
  
  // Inizializza la connessione HTTP con l'URL scoperto o quello di default
  http.begin(client, discoveredServerUrl);
  http.addHeader("Content-Type", "application/json");
  
  // Ottieni la potenza del segnale WiFi
  int rssi = WiFi.RSSI();
  
  // Costruisci il JSON di stato
  String jsonStatus = "{";
  jsonStatus += "\"device_id\":\"" + getUniqueDeviceId() + "\",";
  jsonStatus += "\"table_number\":" + String(tableNumber) + ",";
  jsonStatus += "\"is_running\":" + String(isStarted) + ",";
  jsonStatus += "\"is_paused\":" + String(isPaused) + ",";
  jsonStatus += "\"current_timer\":" + String(timerCurrent) + ",";
  jsonStatus += "\"time_expired\":" + String(timeExpired) + ",";
  jsonStatus += "\"mode\":" + String(operationMode) + ",";
  jsonStatus += "\"t1_value\":" + String(pokerTimer1) + ",";
  jsonStatus += "\"t2_value\":" + String(pokerTimer2) + ",";
  jsonStatus += "\"battery_level\":" + String(lastPercent) + ",";
  jsonStatus += "\"voltage\":" + String(lastVolt) + ",";
  jsonStatus += "\"wifi_signal\":" + String(rssi) + ",";
  jsonStatus += "\"buzzer\":" + String(buzzerOnOff) + ","; // Aggiunto il campo buzzer
  jsonStatus += "\"players_count\":" + String(playersCount);
  jsonStatus += "}";
  
  Serial.println("Sending payload: " + jsonStatus);
  
  // Invia la richiesta POST
  int httpResponseCode = http.POST(jsonStatus);
  
  if (httpResponseCode > 0) {
    Serial.print("HTTP Response code: ");
    Serial.println(httpResponseCode);
    
    // Leggi la risposta dal server (potrebbe contenere comandi)
    String response = http.getString();
    Serial.println("Server response: " + response);
    
    // Se la connessione è riuscita, segna il server come scoperto
    serverDiscovered = true;
    
    // Processa eventuali comandi dal server
    processServerCommands(response);
  }
  else {
    Serial.print("Error sending status. HTTP Error code: ");
    Serial.println(httpResponseCode);
    
    // Se l'errore è grave, resetta lo stato della discovery per provare un altro server
    if (httpResponseCode <= 0) {
      Serial.println("Connection failed. Will try discovery again.");
      serverDiscovered = false;
    }
  }
  
  // Chiudi la connessione
  http.end();
}

void discoverServer() {
  Serial.println("Attempting to discover server on network...");
  
  // Crea un socket UDP per il broadcast
  WiFiUDP udp;
  udp.begin(DISCOVERY_PORT);
  
  // Invia un messaggio di discovery broadcast
  IPAddress broadcastIP(255, 255, 255, 255);
  udp.beginPacket(broadcastIP, DISCOVERY_PORT);
  const char* discoveryMessage = "POKER_TIMER_DISCOVERY";
  udp.write(discoveryMessage, strlen(discoveryMessage));
  udp.endPacket();
  
  Serial.println("Discovery message sent. Waiting for responses...");
  
  // Aspetta le risposte per un tempo limitato
  unsigned long startTime = millis();
  serverDiscovered = false; // Reset dello stato di discovery
  
  while (millis() - startTime < 3000) { // Attendi risposte per 3 secondi
    int packetSize = udp.parsePacket();
    
    if (packetSize) {
      char packetBuffer[255];
      int len = udp.read(packetBuffer, 255);
      
      if (len > 0) {
        packetBuffer[len] = 0; // Termina la stringa
        String response = String(packetBuffer);
        
        Serial.print("Received response: ");
        Serial.print(response);
        Serial.print(" from IP: ");
        Serial.println(udp.remoteIP().toString());
        
        // Verifica se la risposta è dal nostro server
        if (response.indexOf("POKER_TIMER_SERVER") >= 0) {
          // Costruisci l'URL del server usando l'IP del mittente
          IPAddress remoteIP = udp.remoteIP();
          String serverIP = remoteIP.toString();
          discoveredServerUrl = "http://" + serverIP + ":3000/api/status";
          
          Serial.print("Server discovered! URL: ");
          Serial.println(discoveredServerUrl);
          
          serverDiscovered = true;
          break;
        }
      }
    }
    
    // Pausa breve per evitare di sovraccaricareÉà la CPU
    delay(10);
    yield(); // Permette all'ESP di gestire altri processi
  }
  
  if (!serverDiscovered) {
    Serial.println("No server found during discovery.");
  }
  
  udp.stop();
  lastServerDiscoveryAttempt = millis();
  
  // Opzionale: Salva l'URL scoperto in EEPROM
  saveDiscoveredServerUrl();
}

void saveDiscoveredServerUrl() {
  if (serverDiscovered && discoveredServerUrl.length() > 0) {
    // Usa la stessa tecnica che usi per salvare altre impostazioni
    // Questo è solo un esempio, adatta al tuo sistema di salvataggio
    
    Serial.println("Saving discovered server URL to memory");
    
    // Salva in SPIFFS o altro sistema di storage
    if (SPIFFS.begin()) {
      File file = SPIFFS.open("/server_url.txt", "w");
      if (file) {
        file.println(discoveredServerUrl);
        file.close();
        Serial.println("Server URL saved successfully");
      } else {
        Serial.println("Failed to open file for writing");
      }
    } else {
      Serial.println("Failed to mount file system");
    }
  }
}

void loadDiscoveredServerUrl() {
  Serial.println("Loading discovered server URL from memory");
  
  // Carica da SPIFFS o altro sistema di storage
  if (SPIFFS.begin()) {
    if (SPIFFS.exists("/server_url.txt")) {
      File file = SPIFFS.open("/server_url.txt", "r");
      if (file) {
        String savedUrl = file.readStringUntil('\n');
        file.close();
        
        savedUrl.trim(); // Rimuove spazi e newline
        
        if (savedUrl.length() > 0) {
          discoveredServerUrl = savedUrl;
          serverDiscovered = true;
          Serial.print("Loaded server URL: ");
          Serial.println(discoveredServerUrl);
        }
      }
    } else {
      Serial.println("No saved server URL found");
    }
  } else {
    Serial.println("Failed to mount file system");
  }
}

void processServerCommands(String response) {
  // La risposta è in formato JSON, analizziamola
  Serial.println("Full server response: " + response);
  
  if (response.indexOf("\"command\":\"apply_settings\"") >= 0) {
    Serial.println("Command received: APPLY SETTINGS");
    
    // Verifica se la risposta contiene impostazioni
    if (response.indexOf("\"settings\":{") >= 0) {
      Serial.println("Settings found in response, updating values...");
      
      // Estrai i valori dalla risposta JSON
      bool settingsChanged = false;
      
      // Parse Mode
      if (response.indexOf("\"mode\":") >= 0) {
        int startPos = response.indexOf("\"mode\":") + 7;
        int endPos = response.indexOf(",", startPos);
        if (endPos == -1) endPos = response.indexOf("}", startPos);
        if (endPos > startPos) {
          String modeStr = response.substring(startPos, endPos);
          int newMode = modeStr.toInt();
          if (newMode >= 1 && newMode <= 4 && newMode != operationMode) {
            operationMode = newMode;
            settingsChanged = true;
            Serial.print("Updated operation mode to: ");
            Serial.println(operationMode);
          }
        }
      }
      
      // Parse T1
      if (response.indexOf("\"t1\":") >= 0) {
        int startPos = response.indexOf("\"t1\":") + 5;
        int endPos = response.indexOf(",", startPos);
        if (endPos == -1) endPos = response.indexOf("}", startPos);
        if (endPos > startPos) {
          String t1Str = response.substring(startPos, endPos);
          int newT1 = t1Str.toInt();
          if (newT1 >= 5 && newT1 <= 95 && newT1 % 5 == 0) {
            pokerTimer1 = newT1;
            settingsChanged = true;
            Serial.print("Updated T1 to: ");
            Serial.println(pokerTimer1);
          }
        }
      }
      
      // Parse T2
      if (response.indexOf("\"t2\":") >= 0) {
        int startPos = response.indexOf("\"t2\":") + 5;
        int endPos = response.indexOf(",", startPos);
        if (endPos == -1) endPos = response.indexOf("}", startPos);
        if (endPos > startPos) {
          String t2Str = response.substring(startPos, endPos);
          int newT2 = t2Str.toInt();
          if (newT2 >= 5 && newT2 <= 95 && newT2 % 5 == 0) {
            pokerTimer2 = newT2;
            settingsChanged = true;
            Serial.print("Updated T2 to: ");
            Serial.println(pokerTimer2);
          }
        }
      }
      
      // Parse TableNumber
      if (response.indexOf("\"tableNumber\":") >= 0) {
        int startPos = response.indexOf("\"tableNumber\":") + 14;
        int endPos = response.indexOf(",", startPos);
        if (endPos == -1) endPos = response.indexOf("}", startPos);
        if (endPos > startPos) {
          String tableStr = response.substring(startPos, endPos);
          int newTable = tableStr.toInt();
          if (newTable >= 0 && newTable <= 99) {
            tableNumber = newTable;
            settingsChanged = true;
            Serial.print("Updated table number to: ");
            Serial.println(tableNumber);
          }
        }
      }
      
      // Parse Buzzer - gestione migliorata per vari formati
      if (response.indexOf("\"buzzer\":") >= 0) {
        int startPos = response.indexOf("\"buzzer\":") + 9;
        int endPos = response.indexOf(",", startPos);
        if (endPos == -1) endPos = response.indexOf("}", startPos);
        if (endPos > startPos) {
          String buzzerStr = response.substring(startPos, endPos);
          buzzerStr.trim();  // Rimuove spazi
          
          // Per debug
          Serial.print("Raw buzzer value from server: '");
          Serial.print(buzzerStr);
          Serial.println("'");
          
          // Gestione di diversi formati possibili
          bool newBuzzerState;
          
          if (buzzerStr == "true" || buzzerStr == "1") {
            newBuzzerState = true;
          } else if (buzzerStr == "false" || buzzerStr == "0") {
            newBuzzerState = false;
          } else {
            // Prova a convertire come intero
            int buzzerValue = buzzerStr.toInt();
            newBuzzerState = (buzzerValue != 0);
          }
          
          // Converti in uint8_t per compatibilità con buzzerOnOff
          uint8_t newBuzzer = newBuzzerState ? 1 : 0;
          
          // Verifica se effettivamente cambia
          if (newBuzzer != buzzerOnOff) {
            buzzerOnOff = newBuzzer;
            settingsChanged = true;
            Serial.print("Updated buzzer to: ");
            Serial.println(buzzerOnOff);
          }
        }
      }
      
      // Parse PlayersCount - gestione migliorata
      if (response.indexOf("\"playersCount\":") >= 0) {
        int startPos = response.indexOf("\"playersCount\":") + 15;
        int endPos = response.indexOf(",", startPos);
        if (endPos == -1) endPos = response.indexOf("}", startPos);
        if (endPos > startPos) {
          String playersStr = response.substring(startPos, endPos);
          playersStr.trim();
          
          // Per debug
          Serial.print("Raw players count from server: '");
          Serial.print(playersStr);
          Serial.println("'");
          
          int newPlayers = playersStr.toInt();
          if (newPlayers >= 1 && newPlayers <= 10 && newPlayers != playersCount) {
            playersCount = newPlayers;
            settingsChanged = true;
            Serial.print("Updated players count to: ");
            Serial.println(playersCount);
          }
        }
      }
      
      // Salva tutte le impostazioni modificate nella EEPROM
      if (settingsChanged) {
        // Salva in EEPROM con tentativi multipli
        bool saveSuccess = writePokerTimerParams();
        
        if (saveSuccess) {
          Serial.println("Settings saved to EEPROM successfully");
        } else {
          Serial.println("Warning: Failed to save settings to EEPROM");
        }
        
        // Applica le impostazioni immediatamente
        applySettingsImmediately();
      } else {
        Serial.println("No settings changed, nothing to save.");
      }
    } else {
      // Se non ci sono impostazioni nella risposta, usa i valori esistenti
      Serial.println("No settings found in response, using current values.");
      readPokerTimerParams();
      applySettingsImmediately();
    }
  }
  else if (response.indexOf("\"command\":\"start\"") >= 0) {
    // Comando per avviare il timer
    if (isPaused || !isStarted) {
      isPaused = 0;
      isStarted = 1;
      Serial.println("Command received: START timer");
    }
  }
  else if (response.indexOf("\"command\":\"pause\"") >= 0) {
    // Comando per mettere in pausa il timer
    if (isStarted && !isPaused) {
      isPaused = 1;
      Serial.println("Command received: PAUSE timer");
    }
  }
  else if (response.indexOf("\"command\":\"reset\"") >= 0) {
    // Comando per resettare il timer
    setTimer(pokerTimer1, 1);  // Reset a T1 in stato di pausa
    isStarted = 0;
    isPaused = 1;
    timeExpired = 0;
    Serial.println("Command received: RESET timer");
  }
  else if (response.indexOf("\"command\":\"factory_reset\"") >= 0) {
    // Comando per eseguire il factory reset
    Serial.println("Command received: FACTORY RESET");
    performFactoryReset();  // Chiama la funzione di factory reset esistente
  }
  else if (response.indexOf("\"command\":\"settings\"") >= 0) {
    // Comando per aggiornare le impostazioni
    Serial.println("Command received: SETTINGS update");
    
    // Nota: Questo blocco è simile a quello per "apply_settings", 
    // quindi se modifichi uno, assicurati di aggiornare anche l'altro
    
    // Estrai i valori dalla risposta JSON
    bool settingsChanged = false;
    
    // Parse Mode
    if (response.indexOf("\"mode\":") >= 0) {
      int startPos = response.indexOf("\"mode\":") + 7;
      int endPos = response.indexOf(",", startPos);
      if (endPos == -1) endPos = response.indexOf("}", startPos);
      if (endPos > startPos) {
        String modeStr = response.substring(startPos, endPos);
        int newMode = modeStr.toInt();
        if (newMode >= 1 && newMode <= 4 && newMode != operationMode) {
          operationMode = newMode;
          settingsChanged = true;
          Serial.print("Updated operation mode to: ");
          Serial.println(operationMode);
        }
      }
    }
    
    // Parse T1
    if (response.indexOf("\"t1\":") >= 0) {
      int startPos = response.indexOf("\"t1\":") + 5;
      int endPos = response.indexOf(",", startPos);
      if (endPos == -1) endPos = response.indexOf("}", startPos);
      if (endPos > startPos) {
        String t1Str = response.substring(startPos, endPos);
        int newT1 = t1Str.toInt();
        if (newT1 >= 5 && newT1 <= 95 && newT1 % 5 == 0 && newT1 != pokerTimer1) {
          pokerTimer1 = newT1;
          settingsChanged = true;
          Serial.print("Updated T1 to: ");
          Serial.println(pokerTimer1);
        }
      }
    }
    
    // Parse T2
    if (response.indexOf("\"t2\":") >= 0) {
      int startPos = response.indexOf("\"t2\":") + 5;
      int endPos = response.indexOf(",", startPos);
      if (endPos == -1) endPos = response.indexOf("}", startPos);
      if (endPos > startPos) {
        String t2Str = response.substring(startPos, endPos);
        int newT2 = t2Str.toInt();
        if (newT2 >= 5 && newT2 <= 95 && newT2 % 5 == 0 && newT2 != pokerTimer2) {
          pokerTimer2 = newT2;
          settingsChanged = true;
          Serial.print("Updated T2 to: ");
          Serial.println(pokerTimer2);
        }
      }
    }
    
    // Parse TableNumber
    if (response.indexOf("\"tableNumber\":") >= 0) {
      int startPos = response.indexOf("\"tableNumber\":") + 14;
      int endPos = response.indexOf(",", startPos);
      if (endPos == -1) endPos = response.indexOf("}", startPos);
      if (endPos > startPos) {
        String tableStr = response.substring(startPos, endPos);
        int newTable = tableStr.toInt();
        if (newTable >= 0 && newTable <= 99 && newTable != tableNumber) {
          tableNumber = newTable;
          settingsChanged = true;
          Serial.print("Updated table number to: ");
          Serial.println(tableNumber);
        }
      }
    }
    
    // Parse Buzzer - gestione migliorata per vari formati
    if (response.indexOf("\"buzzer\":") >= 0) {
      int startPos = response.indexOf("\"buzzer\":") + 9;
      int endPos = response.indexOf(",", startPos);
      if (endPos == -1) endPos = response.indexOf("}", startPos);
      if (endPos > startPos) {
        String buzzerStr = response.substring(startPos, endPos);
        buzzerStr.trim();  // Rimuove spazi
        
        // Per debug
        Serial.print("Raw buzzer value from server: '");
        Serial.print(buzzerStr);
        Serial.println("'");
        
        // Gestione di diversi formati possibili
        bool newBuzzerState;
        
        if (buzzerStr == "true" || buzzerStr == "1") {
          newBuzzerState = true;
        } else if (buzzerStr == "false" || buzzerStr == "0") {
          newBuzzerState = false;
        } else {
          // Prova a convertire come intero
          int buzzerValue = buzzerStr.toInt();
          newBuzzerState = (buzzerValue != 0);
        }
        
        // Converti in uint8_t per compatibilità con buzzerOnOff
        uint8_t newBuzzer = newBuzzerState ? 1 : 0;
        
        // Verifica se effettivamente cambia
        if (newBuzzer != buzzerOnOff) {
          buzzerOnOff = newBuzzer;
          settingsChanged = true;
          Serial.print("Updated buzzer to: ");
          Serial.println(buzzerOnOff);
        }
      }
    }
    
    // Parse PlayersCount
    if (response.indexOf("\"playersCount\":") >= 0) {
      int startPos = response.indexOf("\"playersCount\":") + 15;
      int endPos = response.indexOf(",", startPos);
      if (endPos == -1) endPos = response.indexOf("}", startPos);
      if (endPos > startPos) {
        String playersStr = response.substring(startPos, endPos);
        playersStr.trim();
        
        // Per debug
        Serial.print("Raw players count from server: '");
        Serial.print(playersStr);
        Serial.println("'");
        
        int newPlayers = playersStr.toInt();
        if (newPlayers >= 1 && newPlayers <= 10 && newPlayers != playersCount) {
          playersCount = newPlayers;
          settingsChanged = true;
          Serial.print("Updated players count to: ");
          Serial.println(playersCount);
        }
      }
    }
    
    // Salva tutte le impostazioni modificate nella EEPROM
    if (settingsChanged) {
      // Salva in EEPROM con tentativi multipli
      bool saveSuccess = writePokerTimerParams();
      
      if (saveSuccess) {
        Serial.println("Settings saved to EEPROM successfully");
      } else {
        Serial.println("Warning: Failed to save settings to EEPROM");
      }
      
      // Assicuriamoci di rileggere i valori prima di applicarli
      delay(100);
      readPokerTimerParams();
      
      applySettingsImmediately();
    }
  }
  else if (response.indexOf("\"command\":\"firmware_update\"") >= 0) {
    // Comando per aggiornare il firmware
    Serial.println("Command received: FIRMWARE UPDATE");
    
    // Controlla se è incluso un URL nella risposta
    String firmwareUrl = "";
    if (response.indexOf("\"url\":") >= 0) {
      int startPos = response.indexOf("\"url\":") + 6;
      int endPos = response.indexOf("\"", startPos + 1);
      if (endPos > startPos) {
        firmwareUrl = response.substring(startPos + 1, endPos);
        Serial.print("Firmware update URL: ");
        Serial.println(firmwareUrl);
      }
    }
    
    // Se non c'è un URL esplicito, usa quello predefinito
    if (firmwareUrl.length() == 0) {
      // Usa l'indirizzo del server di monitoraggio per costruire l'URL
      String serverHost = discoveredServerUrl;
      // Estrai l'host dall'URL (rimuovi http:// e tutto ciò che segue il primo /)
      int hostStart = serverHost.indexOf("//") + 2;
      int hostEnd = serverHost.indexOf("/", hostStart);
      if (hostEnd == -1) hostEnd = serverHost.length();
      String serverIP = serverHost.substring(hostStart, hostEnd);
      
      // Costruisci l'URL per il firmware
      firmwareUrl = "http://" + serverIP + "/firmware/poker_timer.bin";
      Serial.print("Using default firmware URL: ");
      Serial.println(firmwareUrl);
    }
    
    // Prima di aggiornare, mostriamo un messaggio sul display
    for(int i = 0; i < LED_MODULES; i++) {
      clear_module_leds(i);
    }
    
    // "F" sul primo digit
    pixels.setPixelColor(0, pixels.Color(255,0,255));  //B  A  C
    pixels.setPixelColor(1, pixels.Color(0,255,0));    //E  D  F
    pixels.setPixelColor(2, pixels.Color(255,0,255)); //DP  G  NC
    
    // "u" sul secondo digit (simile a u minuscola)
    pixels.setPixelColor(3, pixels.Color(0,255,0));  //B  A  C
    pixels.setPixelColor(4, pixels.Color(0,0,0));    //E  D  F
    pixels.setPixelColor(5, pixels.Color(255,0,255)); //DP  G  NC
    pixels.show();
    
    // Emetti un suono di notifica che stiamo aggiornando
    if(buzzerOnOff) {
      for(int i = 0; i < 3; i++) {
        tone(buzzerPin, 1000 + i*200);
        delay(100);
        noTone(buzzerPin);
        delay(50);
      }
    }
    
    // Attendi un momento affinché l'utente possa vedere il messaggio
    delay(2000);
    
    // Imposta i callbacks per ESPhttpUpdate
    ESPhttpUpdate.onStart([]() {
      Serial.println("Update start");
      // Mostra progresso
      clear_module_leds(0);
      clear_module_leds(1);
      show_char_noob(0);
    });
    
    ESPhttpUpdate.onEnd([]() {
      Serial.println("Update end");
      // Mostra completamento
      clear_module_leds(0);
      clear_module_leds(1);
      show_char_noob(99);
    });
    
    ESPhttpUpdate.onError([](int error) {
      Serial.printf("Update error: %d\n", error);
      // Mostra errore
      clear_module_leds(0);
      clear_module_leds(1);
      
      // "E" sul primo digit
      pixels.setPixelColor(0, pixels.Color(0,0,0));  //B  A  C
      pixels.setPixelColor(1, pixels.Color(0,0,0));    //E  D  F
      pixels.setPixelColor(2, pixels.Color(255,0,255)); //DP  G  NC
      
      // "r" sul secondo digit
      pixels.setPixelColor(3, pixels.Color(255,255,255));  //B  A  C
      pixels.setPixelColor(4, pixels.Color(0,255,255));    //E  D  F
      pixels.setPixelColor(5, pixels.Color(255,0,255)); //DP  G  NC
      pixels.show();
    });
    
    ESPhttpUpdate.onProgress([](int progress, int total) {
      Serial.printf("Progress: %d%%\r", (progress / (total / 100)));
      
      // Visualizza la percentuale di avanzamento sul display
      int percent = progress / (total / 100);
      clear_module_leds(0);
      clear_module_leds(1);
      
      // Visualizza un numero da 0 a 99 che rappresenta la percentuale
      if (percent > 99) percent = 99; // Limita a 99 per il display
      show_char_noob(percent);
      
      // Lampeggia il LED del pulsante in base all'avanzamento
      if (percent % 10 == 0) {
        LedPulse(buttonLedPin, ledPower100, 100);
      }
    });
    
    // Prima di eseguire l'aggiornamento, impostiamo un timeout più lungo
    WiFiClient client;
    client.setTimeout(60); // 60 secondi (il parametro è in secondi)

    // Esegui l'aggiornamento
    t_httpUpdate_return ret = ESPhttpUpdate.update(client, firmwareUrl);
    
    switch (ret) {
      case HTTP_UPDATE_FAILED:
        Serial.printf("HTTP update failed: Error (%d): %s\n", ESPhttpUpdate.getLastError(), ESPhttpUpdate.getLastErrorString().c_str());
        
        // Mostra errore
        clear_module_leds(0);
        clear_module_leds(1);
        
        // "E" sul primo digit
        pixels.setPixelColor(0, pixels.Color(0,0,0));  //B  A  C
        pixels.setPixelColor(1, pixels.Color(0,0,0));    //E  D  F
        pixels.setPixelColor(2, pixels.Color(255,0,255)); //DP  G  NC
        
        // "r" sul secondo digit
        pixels.setPixelColor(3, pixels.Color(255,255,255));  //B  A  C
        pixels.setPixelColor(4, pixels.Color(0,255,255));    //E  D  F
        pixels.setPixelColor(5, pixels.Color(255,0,255)); //DP  G  NC
        pixels.show();
        
        // Suono di errore
        if(buzzerOnOff) {
          for(int i = 0; i < 3; i++) {
            tone(buzzerPin, 500);
            delay(200);
            noTone(buzzerPin);
            delay(100);
          }
        }
        
        // Attendi un po' prima di tornare al funzionamento normale
        delay(3000);
        show_char_noob(timerCurrent);
        break;
        
      case HTTP_UPDATE_NO_UPDATES:
        Serial.println("No updates available");
        
        // Mostra "no" sul display
        clear_module_leds(0);
        clear_module_leds(1);
        
        // "n" sul primo digit
        pixels.setPixelColor(0, pixels.Color(0,255,0));  //B  A  C
        pixels.setPixelColor(1, pixels.Color(0,0,0));    //E  D  F
        pixels.setPixelColor(2, pixels.Color(255,0,255)); //DP  G  NC
        
        // "o" sul secondo digit
        pixels.setPixelColor(3, pixels.Color(0,0,0));  //B  A  C
        pixels.setPixelColor(4, pixels.Color(0,0,0));    //E  D  F
        pixels.setPixelColor(5, pixels.Color(255,0,255)); //DP  G  NC
        pixels.show();
        
        // Suono di notifica
        if(buzzerOnOff) {
          tone(buzzerPin, 800);
          delay(200);
          noTone(buzzerPin);
        }
        
        // Attendi un po' prima di tornare al funzionamento normale
        delay(2000);
        show_char_noob(timerCurrent);
        break;
        
      case HTTP_UPDATE_OK:
        Serial.println("Update successful");
        // Il dispositivo si riavvierà automaticamente dopo l'aggiornamento
        
        // Mostra "OK" sul display
        clear_module_leds(0);
        clear_module_leds(1);
        
        // "O" sul primo digit
        pixels.setPixelColor(0, pixels.Color(0,0,0));  //B  A  C
        pixels.setPixelColor(1, pixels.Color(0,0,0));    //E  D  F
        pixels.setPixelColor(2, pixels.Color(255,255,255)); //DP  G  NC
        
        // "K" o simbolo simile sul secondo digit
        pixels.setPixelColor(3, pixels.Color(0,255,0));  //B  A  C
        pixels.setPixelColor(4, pixels.Color(0,255,0));    //E  D  F
        pixels.setPixelColor(5, pixels.Color(255,0,255)); //DP  G  NC
        pixels.show();
        
        // Suono di successo
        if(buzzerOnOff) {
          tone(buzzerPin, 1000);
          delay(200);
          noTone(buzzerPin);
          delay(100);
          tone(buzzerPin, 1500);
          delay(200);
          noTone(buzzerPin);
        }
        
        // Non è necessario un delay qui poiché l'ESP si riavvierà automaticamente
        break;
    }
  }
}

void resetEEPROM() {
  Serial.println("Resetting EEPROM...");
  
  EEPROM.begin(512);
  
  // Resetta completamente i primi 200 byte della EEPROM
  for (int i = 0; i < 200; i++) {
    EEPROM.write(i, 255);
  }
  
  EEPROM.commit();
  delay(100);
  
  // Imposta e salva i valori di default
  pokerTimer1 = timerSet_20;
  pokerTimer2 = timerSet_30;
  buzzerOnOff = 1;
  operationMode = OPERATION_MODE_1;
  tableNumber = 1;
  wifiEnabled = true;
  
  writePokerTimerParams();
  
  Serial.println("EEPROM reset complete.");
}

void diagEEPROM() {
  Serial.println("==== EEPROM Diagnostics ====");
  Serial.print("T1 in EEPROM (addr "); Serial.print(memAddressTimer1); Serial.print("): ");
  Serial.println(EEPROM.read(memAddressTimer1));
  
  Serial.print("T2 in EEPROM (addr "); Serial.print(memAddressTimer2); Serial.print("): ");
  Serial.println(EEPROM.read(memAddressTimer2));
  
  Serial.print("Mode in EEPROM (addr "); Serial.print(memAddressOperationMode); Serial.print("): ");
  Serial.println(EEPROM.read(memAddressOperationMode));
  
  Serial.print("Buzzer in EEPROM (addr "); Serial.print(memAddressBuzzerState); Serial.print("): ");
  Serial.println(EEPROM.read(memAddressBuzzerState));
  
  Serial.print("Table in EEPROM (addr "); Serial.print(memAddressTableNumber); Serial.print("): ");
  Serial.println(EEPROM.read(memAddressTableNumber));
  
  Serial.print("WiFi in EEPROM (addr "); Serial.print(memAddressWiFiState); Serial.print("): ");
  Serial.println(EEPROM.read(memAddressWiFiState));
  
  Serial.print("Players in EEPROM (addr "); Serial.print(memAddressPlayersCount); Serial.print("): ");
  Serial.println(EEPROM.read(memAddressPlayersCount));
}

String getUniqueDeviceId() {
  uint8_t mac[6];
  WiFi.macAddress(mac);
  
  // Crea un ID univoco basato sul MAC address
  char deviceId[20];
  sprintf(deviceId, "arduino_%02X%02X%02X", mac[3], mac[4], mac[5]);
  
  return String(deviceId);
}