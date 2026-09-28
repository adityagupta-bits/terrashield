# Weather Risk Forecaster (ARIMA-based)

Forecasts key weather variables with ARIMA, then applies threshold rules to flag **flood**, **drought**, and **fire** risk.

## How it works

1. **Data in** — historical daily weather (temp, humidity, precipitation, pressure, wind).
2. **ARIMA per variable** (`arima_model.py`) — each variable gets its own ARIMA(p,d,q) model, order chosen automatically by grid-searching AIC. Produces a point forecast + confidence interval for the next N days.
3. **Risk rules** (`risk_assessment.py`) — the forecasted values are compared against tunable thresholds in `config.py` to flag flood/drought/fire risk with a 0–1 severity score and the specific reasons it triggered.

Important: **ARIMA forecasts numbers, not disaster labels.** There's no off-the-shelf "ARIMA flood classifier" — the standard approach (and what this project does) is univariate forecasting of the driving variables, then rule-based (or later, ML-based) interpretation of those forecasts.

## Setup

```bash
pip install -r requirements.txt
```

Then set your API key one of two ways (only needed for `--source api`):

- **`.env` file (recommended):** copy `.env.example` to `.env` and fill in your key. `main.py` loads this automatically on every run.
  ```bash
  cp .env.example .env
  # then edit .env and paste in your key
  ```
- **Environment variable:** `export OPENWEATHER_API_KEY=your_key_here` (Windows PowerShell: `$env:OPENWEATHER_API_KEY="your_key_here"`)

## Usage

```bash
# 1. Sanity-check the whole pipeline with synthetic data (no API/key needed)
python main.py --source synthetic

# 2. Use your own historical CSV (recommended - see format below)
python main.py --source csv --csv-path my_history.csv

# 3. Pull recent history straight from OpenWeather
python main.py --source api --lat 17.385 --lon 78.4867 --history-days 45
```

CSV format expected by `--source csv`:
```
date,temp_max,temp_min,humidity,precipitation,pressure,wind_speed
2024-01-01,29.1,18.4,42,0.0,1013,3.2
...
```

## ⚠️ The historical-data problem (read this before relying on results)

ARIMA needs a reasonably long, gap-free daily series to fit well — as a rule of thumb, aim for **60+ days minimum, ideally a full year or more** so seasonal patterns are represented.

OpenWeather's APIs are built for *current conditions and short-term forecasts*, not deep history:
- The free tier gives you current weather + a few days of forecast, no history.
- The paid **One Call 3.0** plan's `day_summary` endpoint gives daily aggregates one day at a time going back some period — `fetch_history_from_api()` in `data_loader.py` loops over this, but it's slow (one HTTP call per day) and still may not cover a full year depending on your subscription.
- For serious model training, it's much better to source a longer historical record elsewhere and load it via `--source csv`:
  - [NASA POWER](https://power.larc.nasa.gov/data-access-viewer/) — free, decades of daily data by lat/lon, no key needed.
  - Your national meteorological service (e.g. IMD in India, NOAA in the US).
  - A paid OpenWeather historical bulk product if you specifically want that source.

## Tuning the risk rules

Everything that decides "is this a flood/drought/fire risk" lives in `config.py -> THRESHOLDS`. The defaults are generic placeholders, **not calibrated to any real region's climate** — a "hot" day in a desert town and a "hot" day in a temperate one are very different. Adjust:
- `flood`: cumulative/single-day rainfall + humidity thresholds
- `drought`: how little rain + how hot/dry counts as drought over your horizon
- `fire`: heat + dryness + wind combination that constitutes fire-weather danger in your area

If you later get labeled historical disaster events (e.g. "flood occurred on these dates"), you can replace `risk_assessment.py` with a trained classifier (logistic regression, random forest, etc.) fed the same ARIMA forecast outputs as features — the rest of the pipeline (`main.py`, `arima_model.py`) doesn't need to change.

## Files

| File | Purpose |
|---|---|
| `config.py` | API config, location, thresholds |
| `data_loader.py` | Fetch/load/clean historical weather data |
| `arima_model.py` | Per-variable ARIMA fitting + forecasting |
| `risk_assessment.py` | Threshold-based flood/drought/fire classification |
| `main.py` | CLI that runs the full pipeline |

## Limitations to keep in mind

- This is a **starting scaffold**, not a validated disaster-prediction system. Do not use it as the sole basis for real safety decisions.
- ARIMA assumes fairly regular, autocorrelated patterns; it won't anticipate sudden extreme events (a flash flood from an unforecasted storm system) any better than the input data allows.
- Real flood/fire/drought risk models used operationally (e.g. by meteorological agencies) incorporate soil moisture, terrain, upstream river levels, vegetation dryness indices (like the Canadian Fire Weather Index), and multivariate models — well beyond what a handful of univariate ARIMA forecasts can capture. Treat this as an educational/prototype tool.
