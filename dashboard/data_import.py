import streamlit as st
import pandas as pd
import os

def render_import_page():

    st.markdown('<div class="page-title">Import Store Data</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Upload your sales or inventory file — we handle the rest</div>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📦 Sales / Transactions", "🗄️ Current Stock", "📋 Sample Format"])

    # ── TAB 1: Sales Upload ──────────────────────────────────────
    with tab1:
        st.markdown("""
        <div class="alert-info">
        Upload your billing/sales export from Tally, Busy, Marg, GoFrugal, or any POS system.
        Accepted formats: <strong>CSV or Excel (.xlsx)</strong>
        </div>
        """, unsafe_allow_html=True)

        uploaded_sales = st.file_uploader(
            "Upload Sales File",
            type=["csv", "xlsx"],
            key="sales_upload"
        )

        if uploaded_sales:
            try:
                if uploaded_sales.name.endswith(".xlsx"):
                    raw = pd.read_excel(uploaded_sales)
                else:
                    raw = pd.read_csv(uploaded_sales)

                st.success(f"✅ File loaded: {len(raw)} rows detected")
                st.dataframe(raw.head(5), use_container_width=True)

                st.markdown("#### Map Your Columns to RetailX Format")
                st.markdown("Tell us which column in your file corresponds to each field:")

                cols = ["-- select --"] + list(raw.columns)

                c1, c2 = st.columns(2)
                with c1:
                    col_product  = st.selectbox("Product Name column",  cols, key="col_product")
                    col_quantity = st.selectbox("Quantity Sold column",  cols, key="col_qty")
                    col_price    = st.selectbox("Price / Amount column", cols, key="col_price")
                with c2:
                    col_date     = st.selectbox("Date column",           cols, key="col_date")
                    col_txn      = st.selectbox("Transaction / Bill ID (optional)", cols, key="col_txn")
                    col_category = st.selectbox("Category (optional)",   cols, key="col_cat")

                if st.button("✅ Confirm & Import", type="primary"):
                    if "-- select --" in [col_product, col_quantity, col_price, col_date]:
                        st.error("Please map all required fields before importing.")
                    else:
                        mapped = pd.DataFrame()
                        mapped["product"]        = raw[col_product]
                        mapped["quantity"]       = pd.to_numeric(raw[col_quantity], errors="coerce").fillna(0)
                        mapped["price"]          = pd.to_numeric(raw[col_price],    errors="coerce").fillna(0)
                        mapped["date"]           = pd.to_datetime(raw[col_date],    errors="coerce")
                        mapped["transaction_id"] = raw[col_txn] if col_txn != "-- select --" else range(len(raw))
                        mapped["category"]       = raw[col_category] if col_category != "-- select --" else "General"
                        mapped["customer_id"]    = 0  # anonymous if not available

                        mapped = mapped.dropna(subset=["date"])
                        mapped["sales"] = mapped["quantity"] * mapped["price"]

                        # Merge with existing data or replace
                        action = st.radio("What should we do with existing data?",
                                          ["Replace existing data", "Append to existing data"])

                        if action == "Append to existing data" and os.path.exists("data/retail_transactions.csv"):
                            existing = pd.read_csv("data/retail_transactions.csv")
                            mapped   = pd.concat([existing, mapped], ignore_index=True)

                        mapped.to_csv("data/retail_transactions.csv", index=False)
                        st.success(f"✅ {len(mapped)} records imported successfully! Refresh the dashboard to see updated analytics.")
                        st.balloons()

            except Exception as e:
                st.error(f"Error reading file: {e}")

    # ── TAB 2: Stock Upload ──────────────────────────────────────
    with tab2:
        st.markdown("""
        <div class="alert-info">
        Upload your current stock / inventory file so RetailX can calculate real available stock.
        </div>
        """, unsafe_allow_html=True)

        uploaded_stock = st.file_uploader(
            "Upload Stock File",
            type=["csv", "xlsx"],
            key="stock_upload"
        )

        if uploaded_stock:
            try:
                if uploaded_stock.name.endswith(".xlsx"):
                    raw_stock = pd.read_excel(uploaded_stock)
                else:
                    raw_stock = pd.read_csv(uploaded_stock)

                st.success(f"✅ Stock file loaded: {len(raw_stock)} products")
                st.dataframe(raw_stock.head(), use_container_width=True)

                cols_s = ["-- select --"] + list(raw_stock.columns)
                c1, c2 = st.columns(2)
                with c1:
                    s_product = st.selectbox("Product Name column", cols_s, key="s_product")
                with c2:
                    s_stock   = st.selectbox("Stock Quantity column", cols_s, key="s_stock")

                if st.button("✅ Import Stock Data", type="primary"):
                    if "-- select --" in [s_product, s_stock]:
                        st.error("Please map required fields.")
                    else:
                        stock_mapped = pd.DataFrame()
                        stock_mapped["product"]      = raw_stock[s_product]
                        stock_mapped["stock_loaded"] = pd.to_numeric(raw_stock[s_stock], errors="coerce").fillna(0)
                        stock_mapped.to_csv("data/stock_loaded.csv", index=False)
                        st.success("✅ Stock data imported! Inventory Intelligence will now use real stock values.")

            except Exception as e:
                st.error(f"Error: {e}")

    # ── TAB 3: Sample Format ──────────────────────────────────────
    with tab3:
        st.markdown("### Expected Format — Sales File")
        sample_sales = pd.DataFrame({
            "date":           ["2024-01-15", "2024-01-15", "2024-01-16"],
            "product":        ["Amul Milk 500ml", "Britannia Bread", "Maggi Noodles"],
            "quantity":       [2, 1, 3],
            "price":          [30, 40, 15],
            "transaction_id": [1001, 1001, 1002],
            "category":       ["Dairy", "Bakery", "Snacks"]
        })
        st.dataframe(sample_sales, use_container_width=True)

        csv_sample = sample_sales.to_csv(index=False)
        st.download_button("⬇️ Download Sample CSV Template",
                           data=csv_sample,
                           file_name="retailx_sample_template.csv",
                           mime="text/csv")

        st.markdown("### Expected Format — Stock File")
        sample_stock = pd.DataFrame({
            "product":      ["Amul Milk 500ml", "Britannia Bread", "Maggi Noodles"],
            "stock_loaded": [500, 300, 600]
        })
        st.dataframe(sample_stock, use_container_width=True)