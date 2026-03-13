import pandas as pd
from prophet import Prophet

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

df = pd.read_csv("data/daily_product_sales.csv")

products = df["product"].unique()

forecasts = []

# --------------------------------------------------
# FORECAST EACH PRODUCT
# --------------------------------------------------

for product in products:

    product_df = df[df["product"] == product]

    product_df = product_df.rename(
        columns={
            "date": "ds",
            "quantity": "y"
        }
    )

    model = Prophet()

    model.fit(product_df)

    future = model.make_future_dataframe(periods=7)

    forecast = model.predict(future)

    next_week = forecast.tail(7)[["ds", "yhat"]]

    next_week["product"] = product

    forecasts.append(next_week)

# --------------------------------------------------
# SAVE FORECASTS
# --------------------------------------------------

forecast_df = pd.concat(forecasts)

forecast_df.to_csv(
    "data/demand_forecast.csv",
    index=False
)

print("Forecast generated")