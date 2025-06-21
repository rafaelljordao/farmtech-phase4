#include <WiFi.h>
#include <HTTPClient.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

// ===== Configurações de Rede e Endpoint =====
const char* WIFI_SSID     = "YOUR_SSID";      // Coloque seu SSID
const char* WIFI_PASSWORD = "YOUR_PASS";      // Coloque sua senha
const char* API_URL       = "http://192.168.1.100:8000/sensor-data/";

// ===== Pinos e Objetos =====
const uint8_t PIN_MOISTURE = 34; // Sensor de umidade
const uint8_t PIN_NUTRIENT = 35; // Sensor de nutrientes (ex. sensor analógico)
const uint8_t PIN_PUMP     = 26; // Saída para bomba (relé)

LiquidCrystal_I2C lcd(0x27, 16, 2);

// ===== Setup Inicial =====
void setup() {
  // Serial para debug e Serial Plotter
  Serial.begin(115200);
  delay(1000);

  // Conecta no WiFi
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Conectando ao WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println(" conectado!");

  // Inicializa LCD I2C
  Wire.begin();
  lcd.init();
  lcd.backlight();

  // Configura pino da bomba
  pinMode(PIN_PUMP, OUTPUT);
  digitalWrite(PIN_PUMP, LOW);
}

// ===== Loop Principal =====
void loop() {
  // 1) Leitura de sensores
  uint16_t rawMoisture  = analogRead(PIN_MOISTURE);
  uint16_t rawNutrient  = analogRead(PIN_NUTRIENT);

  // Conversão para escala percentual
  float moisture_pct = rawMoisture * 100.0 / 4095.0;  // 12-bit ADC
  float nutrient_pct = rawNutrient * 100.0 / 4095.0;

  // 2) Lógica de irrigação (simples threshold)
  bool irrigate = (moisture_pct < 30.0);
  digitalWrite(PIN_PUMP, irrigate ? HIGH : LOW);

  // 3) Saída no Serial Plotter
  Serial.print("Moist:"); Serial.print(moisture_pct,1);
  Serial.print(";Nutri:"); Serial.print(nutrient_pct,1);
  Serial.print(";Pump:");  Serial.println(irrigate ? 1 : 0);

  // 4) Exibição no LCD
  lcd.clear();
  lcd.setCursor(0,0);
  lcd.print("Umid:"); lcd.print((int)moisture_pct); lcd.print("%");
  lcd.setCursor(0,1);
  lcd.print("Nutri:"); lcd.print((int)nutrient_pct); lcd.print("%");
  if (irrigate) lcd.print(" ON"); else lcd.print(" OFF");

  // 5) Envio para API (JSON)
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(API_URL);
    http.addHeader("Content-Type", "application/json");

    String payload = "{";
    payload += "\"soil_moisture\":" + String(moisture_pct,1) + ",";
    payload += "\"temperature\":null,"; // temperatura não disponível no hardware
    payload += "\"humidity\":null,";    // idem
    payload += "\"ph_soil\":null,";
    payload += "\"nutrient_level\":" + String(nutrient_pct,1) + ",";
    payload += "\"rainfall\":null,";
    payload += "\"irrigation_active\":" + String(irrigate ? 1 : 0) + ",";
    payload += "\"system_error\":0";
    payload += "}";

    int code = http.POST(payload);
    // opcional: verificar resposta
    Serial.print("HTTP POST status: "); Serial.println(code);
    http.end();
  }

  // Aguarda próximo ciclo
  delay(5000);
}
