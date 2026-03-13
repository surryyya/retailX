import pandas as pd
import os
import sys

# --------------------------------------------------
# PATH FIX — always run from project root
# --------------------------------------------------

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(PROJECT_ROOT)

print(f"Project root : {PROJECT_ROOT}")

# --------------------------------------------------
# BUILD DAILY SALES FIRST
# --------------------------------------------------

txn = pd.read_csv("data/retail_transactions.csv")
txn["date"] = pd.to_datetime(txn["date"], errors="coerce").dt.date.astype(str)

daily = (
    txn.groupby(["date","product"])["quantity"]
    .sum()
    .reset_index()
)
daily.columns = ["date","product","quantity"]
daily.to_csv("data/daily_product_sales.csv", index=False)
print(f"Daily product sales  : {len(daily):,} rows saved")

# --------------------------------------------------
# PROPHET FORECAST — ALL PRODUCTS
# --------------------------------------------------

try:
    from prophet import Prophet
except ImportError:
    print("❌  prophet not installed. Run: pip install prophet")
    sys.exit(1)

import logging
logging.getLogger("prophet").setLevel(logging.WARNING)
logging.getLogger("cmdstanpy").setLevel(logging.WARNING)

products  = daily["product"].unique()
forecasts = []
failed    = []

print(f"\nForecasting {len(products)} products...\n")

for i, product in enumerate(products, 1):

    try:
        pdata = daily[daily["product"] == product][["date","quantity"]].copy()
        pdata.columns = ["ds","y"]
        pdata["ds"]   = pd.to_datetime(pdata["ds"])
        pdata["y"]    = pd.to_numeric(pdata["y"], errors="coerce").fillna(0)

        # Need at least 30 data points for a reliable forecast
        if len(pdata) < 30:
            print(f"  [{i:>3}/{len(products)}] ⚠  {product} — skipped (only {len(pdata)} days of data)")
            continue

        model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=False,
            seasonality_mode="multiplicative",
            interval_width=0.80
        )
        model.fit(pdata)

        future   = model.make_future_dataframe(periods=7)
        forecast = model.predict(future)

        result              = forecast[["ds","yhat","yhat_lower","yhat_upper"]].copy()
        result["yhat"]      = result["yhat"].clip(lower=0).round(2)
        result["yhat_lower"]= result["yhat_lower"].clip(lower=0).round(2)
        result["yhat_upper"]= result["yhat_upper"].clip(lower=0).round(2)
        result["product"]   = product

        forecasts.append(result)
        print(f"  [{i:>3}/{len(products)}] ✅  {product}")

    except Exception as e:
        failed.append(product)
        print(f"  [{i:>3}/{len(products)}] ❌  {product} — {str(e)[:60]}")

# --------------------------------------------------
# SAVE
# --------------------------------------------------

if forecasts:
    forecast_df = pd.concat(forecasts, ignore_index=True)
    forecast_df.to_csv("data/demand_forecast.csv", index=False)
    print(f"\n✅  Forecast saved → data/demand_forecast.csv")
    print(f"   Products forecasted : {len(forecasts)}")
    print(f"   Total rows          : {len(forecast_df):,}")
    if failed:
        print(f"   Failed              : {len(failed)} → {', '.join(failed[:5])}")
else:
    print("❌  No forecasts generated.")
    sys.exit(1)