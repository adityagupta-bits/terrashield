"""
Weather Risk Forecaster
========================
Fetches weather data, fits an ARIMA model per variable, forecasts N days
ahead, and applies threshold rules to flag flood / drought / fire risk.

Usage examples
--------------
# Quick end-to-end test with fake data (no API key or CSV needed):
    python main.py --source synthetic

# Using your own historical CSV (recommended for real use):
    python main.py --source csv --csv-path my_history.csv

# Pulling recent history from OpenWeather (needs OPENWEATHER_API_KEY,
# and a plan with historical access):
    python main.py --source api --lat 17.385 --lon 78.4867
"""

from __future__ import annotations

import argparse
import sys

import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import config
import data_loader
import arima_model
import risk_assessment


def parse_args():
    p = argparse.ArgumentParser(description="ARIMA-based flood/drought/fire risk forecaster")
    p.add_argument("--source", choices=["synthetic", "csv", "api"], default="synthetic",
                    help="Where to load historical weather data from.")
    p.add_argument("--csv-path", type=str, default=None, help="Path to historical CSV (source=csv).")
    p.add_argument("--lat", type=float, default=config.DEFAULT_LAT)
    p.add_argument("--lon", type=float, default=config.DEFAULT_LON)
    p.add_argument("--history-days", type=int, default=config.HISTORY_DAYS_TO_FETCH)
    p.add_argument("--horizon", type=int, default=config.FORECAST_HORIZON_DAYS)
    return p.parse_args()


def load_history(args) -> "pd.DataFrame":
    if args.source == "synthetic":
        print("Using synthetic historical data (for pipeline testing only).")
        df = data_loader.generate_synthetic_history(days=max(365, args.history_days))
    elif args.source == "csv":
        if not args.csv_path:
            sys.exit("--csv-path is required when --source csv")
        print(f"Loading historical data from {args.csv_path}")
        df = data_loader.load_history_csv(args.csv_path)
    else:  # api
        print(f"Fetching {args.history_days} days of history from OpenWeather for ({args.lat}, {args.lon})")
        df = data_loader.fetch_history_from_api(
            args.lat, args.lon, config.OPENWEATHER_API_KEY, days=args.history_days
        )
    return data_loader.clean_and_fill(df)


def main():
    args = parse_args()
    history_df = load_history(args)
    print(f"\nHistory loaded: {len(history_df)} daily records "
          f"({history_df.index.min().date()} to {history_df.index.max().date()})\n")

    print(f"Fitting ARIMA models and forecasting {args.horizon} day(s) ahead...")
    results = arima_model.forecast_all_variables(history_df, args.horizon)
    for name, res in results.items():
        print(f"  {name}: order={res.order}, AIC={res.aic:.1f}")

    forecast_df = arima_model.forecasts_to_dataframe(results)
    print("\nForecast:")
    print(forecast_df.round(2).to_string())

    print("\nRisk assessment:")
    risks = risk_assessment.assess_all(forecast_df)
    for risk_type, assessment in risks.items():
        status = "RISK" if assessment.triggered else "ok"
        print(f"  [{status:4}] {risk_type.upper():8} score={assessment.score}")
        for reason in assessment.reasons:
            print(f"           - {reason}")

    return history_df, forecast_df, risks


if __name__ == "__main__":
    main()
