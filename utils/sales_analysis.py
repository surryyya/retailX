import pandas as pd

df = pd.read_csv("data/retail_transactions.csv")

df["date"] = pd.to_datetime(df["date"])

df["sales"] = df["quantity"] * df["price"]

top_products = df.groupby("product")["quantity"].sum().sort_values(ascending=False)

print("Top Selling Products:")
print(top_products)

daily_sales = df.groupby(["date","product"])["quantity"].sum().reset_index()

daily_sales.to_csv("data/daily_product_sales.csv", index=False)

print("Processed dataset saved")