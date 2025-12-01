// Librerías
#include "DHT.h"
#include <WiFi.h>
#include <HTTPClient.h>
#include <WiFiClientSecure.h>
#include <ArduinoJson.h>        
#include <RunningMedian.h>

// Pines
#define DHTPIN 13
#define DHTTYPE DHT11
#define PIRPIN 4
#define LDRPIN 35
#define RELAYPIN 25
#define SOILPIN 32

// Objetos
DHT dht(DHTPIN, DHTTYPE);
RunningMedian tempMed(5);
RunningMedian humMed(5);
RunningMedian ldrMed(5);
RunningMedian soilMed(5);
RunningMedian pirMed(5);

// Constantes
const char* ssid = "iPhone";
const char* password = "soymikel";
String serverBase = "https://bloomjoy-production.up.railway.app";  
const int PLANTA_ID = 1;  
const int MAX_PULSOS = 5; 

// Configuración runtime para las alertas
float HumedadT_min = 30.0;
float HumedadT_max = 60.0;
float Temp_min = -50.0;
float Temp_max = 100.0;
int Luz_min = 0;
int Luz_max = 4095;
float HumAire_min = 0;
float HumAire_max = 100;
float Frecuencia_riego_horas = 24.0;

// Timers
unsigned long nextIrrigationMillis = 0;
unsigned long lastDataSendMillis = 0;
const unsigned long dataIntervalMillis = 15UL * 1000UL; 

// Lecturas de los sensores

float leerTemp(){
  float t = dht.readTemperature();
  if(!isnan(t)) tempMed.add(t);
  return tempMed.getMedian();
}

float leerHum(){
  float h = dht.readHumidity();
  if (!isnan(h)) humMed.add(h);
  return humMed.getMedian();
}

// Leer LDR y convertir a porcentaje 
int leerLDRPct(){
  int raw = analogRead(LDRPIN);
  ldrMed.add(raw);
  int rawMed = ldrMed.getMedian();
  // Convertir rango 0-4095 a 0-100%
  int porcentaje = map(rawMed, 0, 4095, 0, 100);
  return constrain(porcentaje, 0, 100);
}

int leerSoilPct(){
  int raw = analogRead(SOILPIN);
  soilMed.add(raw);
  int rawMed = soilMed.getMedian();
  int humedad = map(rawMed, 1000, 2480, 100, 0); // calibrar si es necesario
  return constrain(humedad, 0, 100);
}

int leerPIRraw(){
  pirMed.add(digitalRead(PIRPIN));
  return pirMed.getMedian();
}

// Retorna el valor numérico del PIR (0 o 1) para enviar a Flask
int leerPIR(){
  return leerPIRraw();
}

// Obtener configuración desde Flask
bool fetchConfigFromServer(){
  if(WiFi.status() != WL_CONNECTED){
    return false;
  }
  // URL del servidor
  String url = serverBase + "/config/" + String(PLANTA_ID);
  
  // Cliente seguro para HTTPS
  WiFiClientSecure client;
  client.setInsecure(); // Acepta cualquier certificado SSL
  
  // Objeto http
  HTTPClient http;
  // Inicia servidor con cliente seguro
  http.begin(client, url);
  // Timeout
  http.setTimeout(10000);
  // Respuesta del servidor (code 200 es el correcto)
  int code = http.GET();
  if(code != 200){
    http.end();
    return false;
  }
  // Payload de la configuración
  String payload = http.getString();
  // Se cierra la conexión y se liberan recursos
  http.end();

  // Parsear JSON
  // Reservar espacio para el JSON
  const size_t capacity = JSON_OBJECT_SIZE(20) + 300; 
  // Objeto documento JSON
  StaticJsonDocument<capacity> doc;
  // Se parsea el payload en doc
  DeserializationError err = deserializeJson(doc, payload);
  // Si err no es nulo, se devuelve false
  if(err) return false;

  // Asignar valores, si existen
  if(doc.containsKey("HumedadT_min")) HumedadT_min = doc["HumedadT_min"];
  if(doc.containsKey("HumedadT_max")) HumedadT_max = doc["HumedadT_max"];
  if(doc.containsKey("Frecuencia_riego_horas")) Frecuencia_riego_horas = doc["Frecuencia_riego_horas"];
  if(doc.containsKey("Temperatura_min")) Temp_min = doc["Temperatura_min"];
  if(doc.containsKey("Temperatura_max")) Temp_max = doc["Temperatura_max"];
  if(doc.containsKey("Humedad_min")) HumAire_min = doc["Humedad_min"];
  if(doc.containsKey("Humedad_max")) HumAire_max = doc["Humedad_max"];
  if(doc.containsKey("Luz_min")) Luz_min = doc["Luz_min"];
  if(doc.containsKey("Luz_max")) Luz_max = doc["Luz_max"];

  // Calcular siguiente riego: si nextIrrigation no estaba inicializado, planearlo ahora
  if(nextIrrigationMillis == 0){
    unsigned long fh_ms = (unsigned long)(Frecuencia_riego_horas * 3600000.0);
    nextIrrigationMillis = millis() + fh_ms;
  }

  return true;
}

// Riego por pulsos
void doIrrigationPulses(){
  int humedad = leerSoilPct();
  int pulsos = 0;
  Serial.println(">> Iniciando riego por pulsos");
  while(humedad < (int)HumedadT_min && pulsos < MAX_PULSOS){
    Serial.printf("Pulso %d - ON 2s\n", pulsos+1);
    digitalWrite(RELAYPIN, HIGH);
    delay(2000);                     // pulso de 2 segundos (modificable)
    digitalWrite(RELAYPIN, LOW);
    delay(1000);                     // espera breve antes de medir
    // medir varias veces para actualizar la mediana
    for(int i=0; i<5; i++){
      leerSoilPct();
      delay(150);
    }
    humedad = leerSoilPct();
    Serial.printf("Humedad después pulso: %d\n", humedad);
    pulsos++;
  }
  Serial.println(">> Riego terminado (por alcance de humedad o límite de pulsos)");
  // Programar siguiente riego
  unsigned long fh_ms = (unsigned long)(Frecuencia_riego_horas * 3600000.0);
  nextIrrigationMillis = millis() + fh_ms;
}

// Enviar datos agrupados a Flask (orden según mapeo en Flask)
void sendDataToServer(float t, float h, int movimiento, int valorLDR, int humedadSuelo, int estadoRel){
  if(WiFi.status() != WL_CONNECTED) return;
  // Objeto http
  HTTPClient http;
  // URL del servidor
  String url = serverBase + "/data";
  
  // Cliente seguro para HTTPS
  WiFiClientSecure client;
  client.setInsecure(); // Acepta cualquier certificado SSL
  
  // Inicializar servidor con cliente seguro
  http.begin(client, url);
  // Cabecera
  http.addHeader("Content-Type", "application/x-www-form-urlencoded");

  // Agrupa los datos en orden: valor_ldr, temperatura, humedad, humedad_suelo, movimiento
  String body = "ID_planta=" + String(PLANTA_ID)
    + "&valor_ldr=" + String(valorLDR)
    + "&temperatura=" + String(t, 2)
    + "&humedad=" + String(h, 2)
    + "&humedad_suelo=" + String(humedadSuelo)
    + "&movimiento=" + String(movimiento)
    + "&relevador=" + String(estadoRel);
  // Respuesta del servidor (code 200 es el correcto)
  int code = http.POST(body);
  Serial.print("POST /data -> ");
  Serial.println(code);
  if(code == 200){
    String resp = http.getString();
    Serial.print("Resp server: ");
    Serial.println(resp);
  }
  // Se cierra la conexión y se liberan recursos
  http.end();
}

void setup(){
  Serial.begin(115200);
  dht.begin();
  pinMode(PIRPIN, INPUT);
  pinMode(RELAYPIN, OUTPUT);
  pinMode(SOILPIN, INPUT);

  pinMode(LDRPIN, INPUT); // CORRECCIÓN: se añadió pinMode para LDR (entrada analógica)

  digitalWrite(RELAYPIN, LOW);

  // WiFi
  WiFi.begin(ssid, password);
  Serial.print("Conectando WiFi");
  unsigned long start = millis();
  while(WiFi.status() != WL_CONNECTED && millis() - start < 15000){
    delay(500);
    Serial.print(".");
  }
  Serial.println();

  if(WiFi.status() == WL_CONNECTED){
    Serial.print("WiFi OK IP: ");
    Serial.println(WiFi.localIP());
    // Pedir configuración al servidor 
    if(!fetchConfigFromServer()){
      Serial.println("No se pudo obtener config, usando defaults.");
    } 
    else{
      Serial.println("Configuración obtenida del servidor.");
    }
  } 
  else{
    Serial.println("WiFi NO conectado, usando valores por defecto (sin config).");
  }

  // Inicializar siguiente riego si no se definió
  if(nextIrrigationMillis == 0){
    unsigned long fh_ms = (unsigned long)(Frecuencia_riego_horas * 3600000.0);
    nextIrrigationMillis = millis() + fh_ms;
  }

  lastDataSendMillis = millis();
}

void loop(){
  // Reconectar WiFi si se cae
  if(WiFi.status() != WL_CONNECTED){
    Serial.println("WiFi desconectado, reconectando...");
    WiFi.reconnect();
    delay(2000);
  }

  // Lecturas filtradas 
  float t = leerTemp();
  float h = leerHum();
  int movimiento = leerPIR();
  int valorLDR = leerLDRPct();  
  int humedadSuelo = leerSoilPct();

  // Control de riego por timer
  unsigned long now = millis();
  if(now >= nextIrrigationMillis){
    Serial.println("Es momento de riego según timer.");
    // Si humedad abajo de min -> hacer pulsos inteligentes
    if(humedadSuelo < (int)HumedadT_min){
      doIrrigationPulses();
    }
    else{
      // Aunque sea tiempo, si humedad ya está en rango se reprograma siguiente riego
      unsigned long fh_ms = (unsigned long)(Frecuencia_riego_horas * 3600000.0);
      nextIrrigationMillis = now + fh_ms;
      Serial.println("Humedad ya en rango, se reprogramó siguiente riego.");
    }
  }

  // Enviar datos periódicamente (no en cada iteración)
  if(now - lastDataSendMillis >= dataIntervalMillis){
    int estadoRel = digitalRead(RELAYPIN);
    sendDataToServer(t, h, movimiento, valorLDR, humedadSuelo, estadoRel);
    lastDataSendMillis = now;
  }

  // Pequeña espera no bloqueante (evita lecturas ultra rápidas)
  delay(300);
}