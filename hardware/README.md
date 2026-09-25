# TERRA SHIELD - Hardware & Edge Architecture

**Problem Statement:** SIH26178 | **Theme:** Disaster Management  
**Team:** TERRA SHIELD | **Category:** Hardware / Software Hybrid  

---

## 1. Edge Hardware Overview

Unlike expensive, imported weather stations ($3,000+ per unit), **TERRA SHIELD** is built using indigenous, locally sourced, ultra-low-cost components (~₹1,850 / $22 per node). 

Each node incorporates:
- **ESP32 Microcontroller**: 240MHz dual-core Xtensa chip capable of running localized TinyML inference and decentralized ad-hoc mesh communication.
- **HC-SR04 / JSN-SR04T Waterproof Ultrasonic Sensor**: Measures river and drain water levels with millimeter accuracy.
- **DHT22 / AM2302 Sensor**: Precision ambient temperature and humidity for forest fire risk calculation.
- **MQ-135 / PMS5003 Sensor**: Hazardous gas & PM2.5 / PM10 particulate detection.
- **LoRa SX1278 (433/868 MHz) & ESP-NOW**: Enables long-range peer-to-peer mesh packet hopping across canyons and riverbanks without cellular coverage.
- **SIM800L GSM Module (Gateway Sink Only)**: Fallback cellular uplink when towers are operational.
- **Solar & Li-Ion 18650 Battery System with TP4056 & BMS**: Autonomous field operation for 3+ weeks during prolonged power blackouts.

---

## 2. Pin Mapping Table

| Component | Pin Function | ESP32 GPIO Pin | Operating Voltage |
|---|---|---|---|
| **HC-SR04 Ultrasonic** | Trigger (`TRIG`) | GPIO 5 | 5V / 3.3V |
| **HC-SR04 Ultrasonic** | Echo (`ECHO`) | GPIO 18 | 3.3V (via divider) |
| **DHT22 Temp/Humidity** | Data (`SDA`) | GPIO 4 (10k pullup) | 3.3V |
| **MQ-135 Air Quality** | Analog Out (`AOUT`) | GPIO 34 (ADC1) | 3.3V / 5V |
| **Battery Monitor** | Voltage Divider (`V_BAT`) | GPIO 35 (ADC1) | 3.3V |
| **LoRa SX1278 SPI** | NSS / CS | GPIO 15 | 3.3V |
| **LoRa SX1278 SPI** | SCK / MISO / MOSI | GPIO 14 / 12 / 13 | 3.3V |
| **LoRa SX1278 SPI** | DIO0 (Interrupt) | GPIO 26 | 3.3V |
| **Mesh Activity LED** | Pulse indicator | GPIO 2 (Built-in) | 3.3V |
| **Local Siren / Red LED** | Rapid Surge Emergency | GPIO 19 | 3.3V |

---

## 3. Bill of Materials (BOM) - Cost Feasibility Analysis

| Component | Purpose | Unit Cost (INR) |
|---|---|---|
| ESP32-WROOM-32 Development Board | Edge compute & mesh radio | ₹380 |
| JSN-SR04T Waterproof Ultrasonic Sensor | River water gauge | ₹420 |
| DHT22 Digital Sensor | Temperature & humidity | ₹240 |
| MQ-135 Gas & Smog Sensor | Air quality monitoring | ₹160 |
| SX1278 433MHz LoRa Transceiver | Long-range offline mesh | ₹350 |
| TP4056 Solar Charge Controller + 18650 Cell | Power autonomy | ₹180 |
| IP67 Weatherproof Enclosure & Wiring | Environmental protection | ₹120 |
| **Total Cost Per Node** | | **~₹1,850 ($22 USD)** |

*Comparison: Commercial Hydrological Station = ₹2,50,000+ ($3,000). TERRA SHIELD cuts capital expenditure by **over 95%**, enabling Gram Panchayats to deploy 100+ nodes across entire districts.*

---

## 4. Virtual Simulation via Wokwi

If presenting to hackathon evaluators without live hardware wired on stage:
1. Open [https://wokwi.com/projects/new/esp32](https://wokwi.com/projects/new/esp32).
2. Replace `diagram.json` with the contents of `hardware/wokwi/diagram.json`.
3. Replace the sketch code with `hardware/esp32_firmware/esp32_firmware.ino`.
4. Click **Start Simulation** to observe live sensor readings, mesh packet transmissions, and emergency LED triggers!
