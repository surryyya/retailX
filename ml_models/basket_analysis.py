import pandas as pd
import os
import sys
from mlxtend.frequent_patterns import apriori, association_rules

# --------------------------------------------------
# PATH FIX
# Always run relative to project root, not the script's folder
# --------------------------------------------------

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(PROJECT_ROOT)

print(f"\nProject root : {PROJECT_ROOT}")
print("Loading transaction dataset...\n")

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

df = pd.read_csv("data/retail_transactions.csv")

print(f"Total rows            : {len(df):,}")
print(f"Unique transactions   : {df['transaction_id'].nunique():,}")
print(f"Unique products       : {df['product'].nunique()}")

# --------------------------------------------------
# SAMPLE CAP
# Apriori on a full-year 400k row dataset is very slow.
# We use the most recent 60 days — enough for strong rules,
# fast enough for Streamlit's timeout window.
# --------------------------------------------------

if "date" in df.columns:
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    latest     = df["date"].max()
    cutoff     = latest - pd.Timedelta(days=60)
    df_recent  = df[df["date"] >= cutoff]
    print(f"Using last 60 days    : {len(df_recent):,} rows  ({cutoff.date()} → {latest.date()})")
else:
    df_recent = df
    print("No date column found — using full dataset")

# Fallback if recent window is too small
if df_recent["transaction_id"].nunique() < 200:
    print("⚠  Recent window too small — using full dataset")
    df_recent = df

# --------------------------------------------------
# CREATE BASKET MATRIX
# --------------------------------------------------

basket = df_recent.pivot_table(
    index="transaction_id",
    columns="product",
    values="quantity",
    aggfunc="sum",
    fill_value=0
)

print(f"\nBasket matrix shape   : {basket.shape}")

# Convert quantities to boolean
basket = basket > 0

# --------------------------------------------------
# FREQUENT ITEMSETS
# --------------------------------------------------

print("Running Apriori...\n")

frequent_items = apriori(
    basket,
    min_support=0.01,       # 1% of recent transactions
    use_colnames=True
)

print(f"Frequent itemsets found : {len(frequent_items)}")

if len(frequent_items) == 0:
    print("\n⚠  No frequent itemsets found. Lowering min_support to 0.005...")
    frequent_items = apriori(basket, min_support=0.005, use_colnames=True)
    print(f"Frequent itemsets found : {len(frequent_items)}")

if len(frequent_items) == 0:
    print("\n❌  Still no itemsets. Dataset may have too few multi-item transactions.")
    sys.exit(1)

# --------------------------------------------------
# ASSOCIATION RULES
# --------------------------------------------------

rules = association_rules(
    frequent_items,
    metric="confidence",
    min_threshold=0.1
)

print(f"Rules generated         : {len(rules)}")

if len(rules) == 0:
    print("⚠  No rules at confidence 0.1 — trying lift metric...")
    rules = association_rules(frequent_items, metric="lift", min_threshold=1.0)
    print(f"Rules generated (lift)  : {len(rules)}")

if len(rules) == 0:
    print("❌  No association rules could be generated.")
    sys.exit(1)

# --------------------------------------------------
# CLEAN & SORT
# --------------------------------------------------

rules = rules[["antecedents", "consequents", "support", "confidence", "lift"]]

# Flatten frozensets to plain strings
rules["antecedents"] = rules["antecedents"].apply(lambda x: ", ".join(sorted(list(x))))
rules["consequents"] = rules["consequents"].apply(lambda x: ", ".join(sorted(list(x))))

rules = rules.sort_values("lift", ascending=False).reset_index(drop=True)

# --------------------------------------------------
# SAVE
# --------------------------------------------------

rules.to_csv("data/basket_rules.csv", index=False)

print(f"\n✅  Basket rules saved → data/basket_rules.csv")
print(f"   Total rules : {len(rules)}")
print(f"\nTop 10 rules by lift:")
print(rules.head(10).to_string(index=False))