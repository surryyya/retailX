import pandas as pd
import numpy as np

df = pd.read_csv("data/retail_transactions.csv")

print("Original rows:", len(df))

# randomly group items into baskets
basket_sizes = np.random.randint(2,5,size=len(df)//3)

new_rows = []
transaction_id = 1
index = 0

for size in basket_sizes:

    basket = df.iloc[index:index+size]

    for _,row in basket.iterrows():
        r = row.copy()
        r["transaction_id"] = transaction_id
        new_rows.append(r)

    transaction_id += 1
    index += size

fixed_df = pd.DataFrame(new_rows)

fixed_df.to_csv("data/retail_transactions.csv",index=False)

print("Transactions regrouped")
print("Unique transactions:", fixed_df["transaction_id"].nunique())