import pandas as pd
import random
from datetime import datetime, timedelta

products = [
"Amul Milk 500ml",
"Britannia Bread",
"Amul Butter",
"Maggi Noodles",
"Coca Cola 750ml",
"Lay's Chips",
"Aashirvaad Atta 5kg",
"Tata Salt 1kg",
"Fortune Sunflower Oil",
"Parle-G Biscuits",
"Red Label Tea",
"Good Day Cookies",
"Cadbury Dairy Milk"
]

categories = {
"Amul Milk 500ml":"Dairy",
"Britannia Bread":"Bakery",
"Amul Butter":"Dairy",
"Maggi Noodles":"Snacks",
"Coca Cola 750ml":"Beverages",
"Lay's Chips":"Snacks",
"Aashirvaad Atta 5kg":"Groceries",
"Tata Salt 1kg":"Groceries",
"Fortune Sunflower Oil":"Groceries",
"Parle-G Biscuits":"Snacks",
"Red Label Tea":"Beverages",
"Good Day Cookies":"Snacks",
"Cadbury Dairy Milk":"Snacks"
}

prices = {
"Amul Milk 500ml":30,
"Britannia Bread":40,
"Amul Butter":55,
"Maggi Noodles":15,
"Coca Cola 750ml":45,
"Lay's Chips":20,
"Aashirvaad Atta 5kg":280,
"Tata Salt 1kg":25,
"Fortune Sunflower Oil":150,
"Parle-G Biscuits":10,
"Red Label Tea":110,
"Good Day Cookies":30,
"Cadbury Dairy Milk":50
}

common_baskets = [
["Amul Milk 500ml","Britannia Bread","Amul Butter"],
["Maggi Noodles","Coca Cola 750ml","Lay's Chips"],
["Aashirvaad Atta 5kg","Tata Salt 1kg","Fortune Sunflower Oil"],
["Parle-G Biscuits","Red Label Tea"],
["Cadbury Dairy Milk","Good Day Cookies"]
]

rows = []
start_date = datetime(2024,1,1)
transaction_id = 1

for i in range(5000):

    basket = random.choice(common_baskets)

    for product in basket:

        sale_time = start_date + timedelta(days=random.randint(0,365))

        rows.append([
            transaction_id,
            random.randint(1000,5000),
            product,
            categories[product],
            random.randint(1,3),
            prices[product],
            sale_time
        ])

    transaction_id += 1

df = pd.DataFrame(rows,columns=[
"transaction_id",
"customer_id",
"product",
"category",
"quantity",
"price",
"date"
])

df.to_csv("data/retail_transactions.csv",index=False)

print("Retail dataset generated")