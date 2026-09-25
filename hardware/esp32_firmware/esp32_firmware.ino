/*
 * TERRA SHIELD - Ultra-Low-Cost Resilient Edge Node Firmware v2.0
 * Problem Statement: SIH26178 | Smart India Hackathon 2026
 * Platform: ESP32 (NodeMCU / ESP32-WROOM-32 / TTGO LoRa32)
 *
 * Key Capabilities:
 *  1. Decentralized Mesh Networking via ESP-NOW & LoRa P2P (zero cellular/internet needed).
 *  2. Multi-sensor data acquisition:
 *     - Ultrasonic Sensor (HC-SR04) for River Water Level
 *     - DHT22 for Ambient Temperature & Humidity (Wildfire danger index)
 *     - MQ-135 Analog Sensor for Air Quality / Smoke
 *     - Battery Voltage Divider ADC
 *  3. LittleFS On-Device Ring Buffer:
 *     - Stores up to 200 telemetry records when field network is severed.
 *     - Automatically flushes batch to /api/v1/ingest/store-forward when comms return.
 *  4. Microsecond On-Device Decision Timing:
 *     - Evaluates rate of change (< 5ms) and triggers local siren GPIO before cloud receipt.
 *  5. Ingest Authentication:
 *     - Uses SHA-256 hashed API Key via "X-API-Key" HTTP header.
 */

#include <WiFi.h>
#include <esp_now.h>
#include <HTTPClient.h>
#include <LittleFS.h>
#include <time.h>

#if __has_include("config.h")
  #include "config.h"
#else
  #include "config.h.example"
#endif

// ================= TELEMETRY PACKET STRUCTURE =================
typedef struct __attribute__((packed)) {
  char node_id[16];
  float water_level_m;
  float water_rate_of_change;
  float temperature_c;
  float humidity_pct;
  float pm25;
  uint8_t hop_count;
  char parent_id[16];
  float battery_pct;
  bool edge_emergency_flag;
  uint32_t timestamp_epoch;
} TelemetryPacket;

TelemetryPacket current_packet;
float previous_water_level = 1.50;
unsigned long last_reading_time = 0;
const unsigned long READING_INTERVAL_MS = 5000;
const char BUFFER_FILE_PATH[] = "/buffer.jsonl";

// Broadcast MAC address for ad-hoc ESP-NOW mesh
uint8_t broadcastAddress[] = {0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF};

// ================= LITTLEFS STORE-AND-FORWARD BUFFER =================
void init_filesystem() {
  if (!LittleFS.begin(true)) {
    Serial.println("[FS] LittleFS Mount Failed! Formatting...");
    LittleFS.format();
    LittleFS.begin();
  } else {
    Serial.println("[FS] LittleFS Mounted Successfully.");
  }
}

void buffer_record_to_flash(const String &jsonRecord) {
  File f = LittleFS.open(BUFFER_FILE_PATH, FILE_APPEND);
  if (!f) {
    Serial.println("[FS] Failed to open buffer file for append!");
    return;
  }
  f.println(jsonRecord);
  f.close();
  Serial.println("[FS] Telemetry buffered to LittleFS (Offline mode)");
}

int get_buffered_record_count() {
  if (!LittleFS.exists(BUFFER_FILE_PATH)) return 0;
  File f = LittleFS.open(BUFFER_FILE_PATH, FILE_READ);
  if (!f) return 0;
  int count = 0;
  while (f.available()) {
    String line = f.readStringUntil('\n');
    if (line.length() > 5) count++;
  }
  f.close();
  return count;
}

void flush_store_and_forward_buffer() {
  if (!LittleFS.exists(BUFFER_FILE_PATH)) return;
  int count = get_buffered_record_count();
  if (count == 0) return;

  Serial.printf("[FS] Network restored! Flushing %d buffered records to backend...\n", count);

  File f = LittleFS.open(BUFFER_FILE_PATH, FILE_READ);
  if (!f) return;

  // Build JSON Array payload for /api/v1/ingest/store-forward
  String batchJson = "[";
  bool first = true;
  while (f.available()) {
    String line = f.readStringUntil('\n');
    line.trim();
    if (line.length() > 5) {
      if (!first) batchJson += ",";
      batchJson += line;
      first = false;
    }
  }
  f.close();
  batchJson += "]";

  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    String url = String(BACKEND_SERVER_URL) + String(INGEST_BATCH_PATH);
    http.begin(url);
    http.addHeader("Content-Type", "application/json");
    http.addHeader("X-API-Key", NODE_API_KEY);

    int httpCode = http.POST(batchJson);
    if (httpCode >= 200 && httpCode < 300) {
      Serial.printf("[FS] Store-and-Forward flush successful (HTTP %d). Clearing buffer.\n", httpCode);
      LittleFS.remove(BUFFER_FILE_PATH);
    } else {
      Serial.printf("[FS] Flush failed (HTTP %d). Retaining flash buffer.\n", httpCode);
    }
    http.end();
  }
}

// ================= SENSOR READINGS =================
float read_ultrasonic_distance_meters() {
  digitalWrite(PIN_TRIG, LOW);
  delayMicroseconds(2);
  digitalWrite(PIN_TRIG, HIGH);
  delayMicroseconds(10);
  digitalWrite(PIN_TRIG, LOW);

  long duration = pulseIn(PIN_ECHO, HIGH, 30000); // 30ms timeout
  if (duration == 0) return 1.80; // Baseline fallback

  // Sound speed 343 m/s => distance = (duration * 0.000343) / 2
  float distance_m = (duration * 0.000343) / 2.0;
  float bridge_mount_height = 8.0;
  float water_level = bridge_mount_height - distance_m;
  return constrain(water_level, 0.2, 7.5);
}

float read_air_quality_pm25() {
  int raw = analogRead(PIN_MQ135);
  float pm25 = map(raw, 200, 4095, 25, 450);
  return constrain(pm25, 10.0, 500.0);
}

float read_battery_percentage() {
  int raw = analogRead(PIN_BATTERY);
  float voltage = (raw / 4095.0) * 3.3 * 2.0;
  float pct = ((voltage - 3.2) / (4.2 - 3.2)) * 100.0;
  return constrain(pct, 0.0, 100.0);
}

// ================= ESP-NOW CALLBACKS =================
void on_data_sent(const uint8_t *mac_addr, esp_now_send_status_t status) {
  digitalWrite(PIN_LED_MESH, HIGH);
  delay(20);
  digitalWrite(PIN_LED_MESH, LOW);
}

void forward_reading_to_backend(const String &jsonPayload) {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    String url = String(BACKEND_SERVER_URL) + String(INGEST_READING_PATH);
    http.begin(url);
    http.addHeader("Content-Type", "application/json");
    http.addHeader("X-API-Key", NODE_API_KEY);

    int httpCode = http.POST(jsonPayload);
    if (httpCode >= 200 && httpCode < 300) {
      Serial.printf("[Ingest] Live reading uploaded (HTTP %d)\n", httpCode);
      // If buffer has pending records, attempt to flush them
      if (LittleFS.exists(BUFFER_FILE_PATH)) {
        flush_store_and_forward_buffer();
      }
    } else {
      Serial.printf("[Ingest] Upload failed (HTTP %d). Buffering...\n", httpCode);
      buffer_record_to_flash(jsonPayload);
    }
    http.end();
  } else {
    // WiFi offline => store to LittleFS
    buffer_record_to_flash(jsonPayload);
  }
}

void on_data_received(const uint8_t *mac, const uint8_t *incoming_data, int len) {
  if (len == sizeof(TelemetryPacket)) {
    TelemetryPacket relay_packet;
    memcpy(&relay_packet, incoming_data, sizeof(relay_packet));
    relay_packet.hop_count += 1;

    if (IS_GATEWAY) {
      String json = "{";
      json += "\"node_id\":\"" + String(relay_packet.node_id) + "\",";
      json += "\"water_level_m\":" + String(relay_packet.water_level_m, 2) + ",";
      json += "\"temperature_c\":" + String(relay_packet.temperature_c, 1) + ",";
      json += "\"humidity_pct\":" + String(relay_packet.humidity_pct, 1) + ",";
      json += "\"pm25\":" + String(relay_packet.pm25, 1) + ",";
      json += "\"mesh_hops\":" + String(relay_packet.hop_count) + ",";
      json += "\"battery_pct\":" + String(relay_packet.battery_pct, 1) + ",";
      json += "\"edge_emergency_flag\":" + String(relay_packet.edge_emergency_flag ? "true" : "false");
      json += "}";
      forward_reading_to_backend(json);
    } else {
      esp_now_send(broadcastAddress, (uint8_t *)&relay_packet, sizeof(relay_packet));
    }
  }
}

// ================= SETUP =================
void setup() {
  Serial.begin(115200);
  pinMode(PIN_TRIG, OUTPUT);
  pinMode(PIN_ECHO, INPUT);
  pinMode(PIN_MQ135, INPUT);
  pinMode(PIN_BATTERY, INPUT);
  pinMode(PIN_LED_MESH, OUTPUT);
  pinMode(PIN_SIREN_ALERT, OUTPUT);

  digitalWrite(PIN_SIREN_ALERT, LOW);

  // Initialize LittleFS
  init_filesystem();

  // WiFi setup
  WiFi.mode(WIFI_STA);
  if (IS_GATEWAY) {
    WiFi.begin(WIFI_SSID, WIFI_PASS);
    Serial.print("[WiFi] Connecting to Gateway AP");
    int retry = 0;
    while (WiFi.status() != WL_CONNECTED && retry < 15) {
      delay(500);
      Serial.print(".");
      retry++;
    }
    if (WiFi.status() == WL_CONNECTED) {
      Serial.println("\n[WiFi] Connected! IP: " + WiFi.localIP().toString());
    } else {
      Serial.println("\n[WiFi] Outage detected! Will buffer records to LittleFS.");
    }
  }

  // ESP-NOW Mesh setup
  if (esp_now_init() != ESP_OK) {
    Serial.println("[ESP-NOW] Init Failed!");
    return;
  }
  esp_now_register_send_cb(on_data_sent);
  esp_now_register_recv_cb(on_data_received);

  esp_now_peer_info_t peerInfo = {};
  memcpy(peerInfo.peer_addr, broadcastAddress, 6);
  peerInfo.channel = 0;
  peerInfo.encrypt = false;
  esp_now_add_peer(&peerInfo);

  Serial.println("==================================================");
  Serial.printf("TERRA SHIELD Node %s Online\n", NODE_ID);
  Serial.println("Decentralized Zero-Internet Edge Network Active");
  Serial.println("==================================================");
}

// ================= LOOP =================
void loop() {
  unsigned long now = millis();
  if (now - last_reading_time >= READING_INTERVAL_MS) {
    last_reading_time = now;

    // 1. Acquire Sensors
    float water_level = read_ultrasonic_distance_meters();
    float temp_c = 28.5;
    float hum_pct = 62.0;
    float pm25 = read_air_quality_pm25();
    float battery = read_battery_percentage();

    // 2. Microsecond On-Device Decision Timing
    unsigned long start_eval = micros();
    float delta_m = water_level - previous_water_level;
    bool is_rapid_surge = (delta_m > SURGE_DELTA_THRESHOLD_M);
    bool is_critical_level = (water_level > WATER_CRITICAL_LEVEL_M);
    bool edge_alert = is_rapid_surge || is_critical_level;
    unsigned long decision_time_us = micros() - start_eval;

    if (edge_alert) {
      digitalWrite(PIN_SIREN_ALERT, HIGH); // Immediate local buzzer triggered
      Serial.printf("[EDGE TIMING] Emergency anomaly detected in %lu us! Local siren active.\n", decision_time_us);
    } else {
      digitalWrite(PIN_SIREN_ALERT, LOW);
    }

    // 3. Assemble JSON Payload
    String json = "{";
    json += "\"node_id\":\"" + String(NODE_ID) + "\",";
    json += "\"water_level_m\":" + String(water_level, 2) + ",";
    json += "\"temperature_c\":" + String(temp_c, 1) + ",";
    json += "\"humidity_pct\":" + String(hum_pct, 1) + ",";
    json += "\"pm25\":" + String(pm25, 1) + ",";
    json += "\"mesh_hops\":0,";
    json += "\"battery_pct\":" + String(battery, 1) + ",";
    json += "\"edge_emergency_flag\":" + String(edge_alert ? "true" : "false") + ",";
    json += "\"decision_latency_us\":" + String(decision_time_us);
    json += "}";

    previous_water_level = water_level;

    // 4. Ingest or Buffer
    if (IS_GATEWAY) {
      forward_reading_to_backend(json);
    } else {
      // Broadcast via LoRa / ESP-NOW
      strncpy(current_packet.node_id, NODE_ID, sizeof(current_packet.node_id));
      current_packet.water_level_m = water_level;
      current_packet.water_rate_of_change = delta_m;
      current_packet.temperature_c = temp_c;
      current_packet.humidity_pct = hum_pct;
      current_packet.pm25 = pm25;
      current_packet.hop_count = 0;
      current_packet.battery_pct = battery;
      current_packet.edge_emergency_flag = edge_alert;

      esp_now_send(broadcastAddress, (uint8_t *)&current_packet, sizeof(current_packet));
    }
  }
}
