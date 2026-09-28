# Model 2: Edge Hydrological ARIMA(2,1,1) & Residual Anomaly Z-Score

**Module Location:** [`backend/app/ai_engine.py`](file:///c:/Users/ASUS/sih/backend/app/ai_engine.py#L8-L221)  
**Service Endpoint:** `POST /api/simulation/trigger` (`scenario="FLASH_FLOOD"`) & `POST /api/v1/ingest/reading`  
**Problem Statement:** SIH26178 | **Theme:** Disaster Management  
**Historical Calibration:** Assam 16 June 2024 Flood Deluge (Kopili River at Kampur Embankment)

---

## 1. Executive Summary & Purpose

A major flaw in legacy early warning systems is the reliance on rigid, static water level thresholds. A water stage of $3.5\text{m}$ is normal during heavy monsoon rains, whereas an unpredicted rapid rise of $+0.8\text{m}$ in a dry morning signals an acute upstream cloudburst or embankment breach.

**Model 2** implements an **in-memory, online ARIMA(2,1,1) Hydrological Surge Engine** coupled with **Standardized Residual Anomaly Z-Score Scoring**. It predicts river stage trajectories up to 3 hours in advance, isolates abnormal non-linear surges, and determines the exact minute-level **Time-to-Overflow** before embankment overtopping occurs.

```mermaid
graph TD
    SENS[Ultrasonic Transducer Reading Y_t] --> AR_DIFF[Differencing d=1<br>Y'_t = Y_t - Y_{t-1}]
    AR_DIFF --> AR_EST[Ordinary Least Squares<br>AR(2) Coefficients φ₁, φ₂]
    AR_DIFF --> MA_EST[MA(1) Innovation Filter<br>Residual Error Decay θε_{t-1}]
    AR_EST & MA_EST --> BASELINE[Project Expected ARIMA Baseline Ŷ_{arima}]
    SENS & BASELINE --> RESID[Compute Physical Residual Error<br>e_t = Y_actual - Ŷ_{arima}]
    RESID --> Z_SCORE[Standardized Anomaly Scoring<br>Z_t = |e_t - μ_e| / σ_e]
    Z_SCORE --> DECISION{Z_t ≥ 3.0σ OR<br>Stage ≥ 4.0m?}
    DECISION -->|YES| CRIT[EMERGENCY BREACH ALERT<br>Calc Time-to-Overflow mins<br>Trigger WhatsApp Verification]
    DECISION -->|NO| WATCH{Z_t ≥ 2.0σ OR<br>Stage ≥ 3.0m?}
    WATCH -->|YES| CAUTION[ELEVATED WATCH ALERT]
    WATCH -->|NO| NORM[SYSTEM OPTIMAL - Track Baseline]
```

---

## 2. Mathematical Formulation: ARIMA(2, 1, 1)

### 2.1. First-Order Differencing ($d = 1$)
Cancels diurnal tidal drift and catchment elevation baselines to achieve series stationarity:
$$Y'_t = Y_t - Y_{t-1}$$

### 2.2. Second-Order AutoRegressive Fit ($p = 2$) via OLS
Estimates the hydraulic momentum coefficients $\phi_1, \phi_2$ over a rolling window ($n \ge 5$ observations):
$$\mathbf{X} = \begin{bmatrix} 1 & Y'_{t-1} & Y'_{t-2} \\ 1 & Y'_{t-2} & Y'_{t-3} \\ \vdots & \vdots & \vdots \end{bmatrix}, \quad \mathbf{Y} = \begin{bmatrix} Y'_t \\ Y'_{t-1} \\ \vdots \end{bmatrix}$$
$$\begin{bmatrix} c \\ \phi_1 \\ \phi_2 \end{bmatrix} = (\mathbf{X}^T \mathbf{X})^{-1} \mathbf{X}^T \mathbf{Y}$$

### 2.3. Moving Average Decay ($q = 1$)
Filters ultrasonic surface wave splashing:
$$\theta = 0.4 \cdot \bar{\epsilon}_{t-1}$$

### 2.4. Recursive Out-of-Sample Horizon Projections
For projection horizons $h \in \{0.5, 1.0, 1.5, 2.0, 3.0\}$ hours, Model 2 iteratively steps the differenced forecast:
$$\hat{Y}'_{t+h} = c + \phi_1 \hat{Y}'_{t+h-1} + \phi_2 \hat{Y}'_{t+h-2} + \theta^{(h)} \epsilon_t$$
Restoring absolute physical river stage:
$$\hat{Y}_{t+h} = \max\left(0.2, \; \hat{Y}_{t+h-1} + \hat{Y}'_{t+h} + \Delta_{momentum}\right)$$
Where surge momentum acceleration is modeled as:
$$\Delta_{momentum} = \frac{1}{2} a h^2, \quad a = 0.12 \times \left(\frac{\Delta Y_{30m}}{0.5}\right)$$

---

## 3. Residual Anomaly Z-Score Scoring

The physical residual between the measured sensor observation and the ARIMA expected baseline represents unmodeled external hydraulic force (dam release or flash deluge):
$$e_t = Y_{actual} - \hat{Y}_{arima}$$

The standardized anomaly score $Z_t$ is computed against the standard deviation of residuals $\sigma_e$:
$$\boxed{Z_t = \frac{|e_t - \mu_e|}{\sigma_e}}$$
Where $\sigma_e = \max(0.12\text{m}, \; \text{std}(\mathbf{e}))$ sets a minimum physical noise floor of $12\text{cm}$ to avoid false alarms from light ripples.

### Hazard Decision Boundaries:
| Anomaly Metric | Physical Gauge Condition | Decision Classification | UI Badge Color | System Action |
| :--- | :--- | :--- | :--- | :--- |
| **$Z_t \ge 3.0\sigma$** | Or Stage $\ge 4.0\text{m}$ | **`EMERGENCY`** | `RED (#dc2626)` | Flash siren, auto-dispatch WhatsApp verification to Gaonburah |
| **$2.0\sigma \le Z_t < 3.0\sigma$** | Or Stage $\ge 3.0\text{m}$ | **`CAUTION`** | `AMBER (#d97706)` | Elevated hydrological watch, increase sensor sampling rate |
| **$Z_t < 2.0\sigma$** | And Stage $< 3.0\text{m}$ | **`NORMAL`** | `GREEN (#16a34a)` | System optimal, normal heartbeat telemetry |

---

## 4. Assam 16 June Incident Calibration

On **16 June 2024**, extreme monsoonal downpours in the Dima Hasao hills caused the **Kopili River** to surge dramatically at Kampur (Nagaon District):
- **Historical Highest Flood Level (HFL)**: $4.75\text{m}$
- **Simulated Peak Surge**: $4.85\text{m}$ (+10cm above HFL)
- **30-Minute Rate of Change**: $+1.92\text{m}$ rise
- **Primary Node**: [`PHY-03`](file:///c:/Users/ASUS/sih/backend/scripts/seed.py#L66) (Kampur Embankment Critical Sentry, Hardware)
- **Calculated Z-Score**: $Z_t = \frac{|4.85 - 0.20|}{0.12} = \mathbf{38.75\sigma}$ (Critical Anomaly)
- **Time to Overflow**: **35 minutes** before embankment overtopping

```json
{
  "status": "triggered",
  "scenario": "FLASH_FLOOD",
  "node_id": "PHY-03",
  "alert_id": 5,
  "model_type": "ARIMA(2,1,1) + Residual Anomaly",
  "anomaly_z_score": 38.75,
  "residual_error_m": 4.65,
  "time_to_overflow_mins": 35,
  "message": "Kopili flood deluge injected at Kampur Embankment Critical Sentry (Hardware). WhatsApp Gaonburah verification dispatched!"
}
```

---

## 5. Live Simulation Trigger Verification

```bash
# Trigger the 16 June Kopili flood wave simulation
curl -X POST http://127.0.0.1:8000/api/simulation/trigger \
  -H "Content-Type: application/json" \
  -d '{"scenario": "FLASH_FLOOD", "target_node_id": "PHY-03"}'
```
