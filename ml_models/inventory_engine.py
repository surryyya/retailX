import pandas as pd
import os
import sys

# --------------------------------------------------
# PATH FIX
# Always run relative to project root
# --------------------------------------------------

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(PROJECT_ROOT)

print(f"Project root : {PROJECT_ROOT}")

# --------------------------------------------------
# LOAD TRANSACTION DATA
# --------------------------------------------------

transactions = pd.read_csv("data/retail_transactions.csv")
transactions["date"] = pd.to_datetime(transactions["date"], errors="coerce")

print(f"Transactions loaded : {len(transactions):,} rows")

# --------------------------------------------------
# LOAD CURRENT STORE STOCK
# --------------------------------------------------

if os.path.exists("data/stock_loaded.csv"):
    stock_df = pd.read_csv("data/stock_loaded.csv")
    print(f"Stock source        : Real upload ({len(stock_df)} products)")
else:
    stock_loaded = {
        "Amul Milk 500ml": 500,
        "Britannia Bread": 300,
        "Amul Butter": 200,
        "Maggi Noodles": 600,
        "Coca Cola 750ml": 400,
        "Lay's Chips": 500,
        "Aashirvaad Atta 5kg": 200,
        "Tata Salt 1kg": 250,
        "Fortune Sunflower Oil": 200,
        "Parle-G Biscuits": 500,
        "Red Label Tea": 200,
        "Good Day Cookies": 350,
        "Cadbury Dairy Milk": 300
    }
    stock_df = pd.DataFrame(list(stock_loaded.items()), columns=["product", "stock_loaded"])
    print("Stock source        : Demo defaults")

# --------------------------------------------------
# USE ONLY RECENT SALES (LAST 30 DAYS)
# --------------------------------------------------

latest_date  = transactions["date"].max()
recent_sales = transactions[transactions["date"] > latest_date - pd.Timedelta(days=30)]

print(f"Recent sales window : {(latest_date - pd.Timedelta(days=30)).date()} → {latest_date.date()}")
print(f"Recent rows         : {len(recent_sales):,}")

sold = (
    recent_sales
    .groupby("product")["quantity"]
    .sum()
    .reset_index()
)

# --------------------------------------------------
# MERGE STOCK AND SALES
# --------------------------------------------------

inventory              = pd.merge(stock_df, sold, on="product", how="left")
inventory["quantity"]  = inventory["quantity"].fillna(0)

# --------------------------------------------------
# AVAILABLE STOCK
# --------------------------------------------------

inventory["available_stock"] = (
    inventory["stock_loaded"] - inventory["quantity"]
).clip(lower=0)

# --------------------------------------------------
# DAILY DEMAND & DAYS REMAINING
# --------------------------------------------------

inventory["daily_demand"]   = inventory["quantity"] / 30

inventory["days_remaining"] = inventory.apply(
    lambda x: round(x["available_stock"] / x["daily_demand"], 1)
    if x["daily_demand"] > 0 else 999,
    axis=1
)

# --------------------------------------------------
# REORDER POINT LOGIC
# --------------------------------------------------

REORDER_DAYS = 7
SAFETY_STOCK = 20

inventory["reorder_point"] = (inventory["daily_demand"] * REORDER_DAYS) + SAFETY_STOCK

# --------------------------------------------------
# RESTOCK QUANTITY
# --------------------------------------------------

inventory["restock_quantity"] = inventory.apply(
    lambda x: max(0, int(x["reorder_point"] - x["available_stock"]))
    if x["available_stock"] < x["reorder_point"] else 0,
    axis=1
)

# --------------------------------------------------
# PRIORITY LEVEL
# --------------------------------------------------

def priority(row):
    if row["days_remaining"] < 3:   return "High"
    if row["days_remaining"] < 7:   return "Medium"
    return "Low"

inventory["priority"] = inventory.apply(priority, axis=1)

# --------------------------------------------------
# SAVE
# --------------------------------------------------

inventory.to_csv("data/inventory_recommendations.csv", index=False)

print(f"\n✅  Inventory saved → data/inventory_recommendations.csv")
print(f"   Products     : {len(inventory)}")
print(f"   High priority: {len(inventory[inventory['priority']=='High'])}")
print(f"   Med priority : {len(inventory[inventory['priority']=='Medium'])}")
print(f"   Healthy      : {len(inventory[inventory['priority']=='Low'])}")
print()
print(inventory[["product","available_stock","days_remaining","restock_quantity","priority"]].to_string(index=False))