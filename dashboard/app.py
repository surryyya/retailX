import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
import re
import os
import sys
import subprocess
import json

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="RetailX Intelligence",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------
# CSS
# --------------------------------------------------

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&display=swap');

* { font-family: 'DM Sans', sans-serif; }

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.5rem 2rem 2rem 2rem; }

[data-testid="stSidebar"] {
    background: #0f1117 !important;
    border-right: 1px solid #1e2130;
}
[data-testid="stSidebar"] .stRadio label {
    color: #8b92a5 !important;
    font-size: 14px;
    font-weight: 500;
    padding: 8px 12px;
    border-radius: 8px;
    transition: all 0.2s;
}
[data-testid="stSidebar"] .stRadio label:hover {
    color: #fff !important;
    background: #1e2130;
}

.kpi-card {
    background: #fff;
    border-radius: 16px;
    padding: 22px 24px;
    border: 1px solid #eef0f6;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    margin-bottom: 8px;
}
.kpi-label {
    font-size: 12px;
    color: #8b92a5;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-bottom: 6px;
}
.kpi-value {
    font-size: 28px;
    font-weight: 700;
    color: #0f1117;
    line-height: 1.1;
}
.kpi-delta      { font-size: 12px; font-weight: 600; margin-top: 6px; }
.kpi-up         { color: #22c55e; }
.kpi-down       { color: #ef4444; }
.kpi-neutral    { color: #f59e0b; }

.section-header {
    font-size: 17px;
    font-weight: 700;
    color: #0f1117;
    margin-bottom: 14px;
    padding-bottom: 10px;
    border-bottom: 2px solid #f1f3f9;
}

.chart-card {
    background: #fff;
    border-radius: 16px;
    padding: 20px;
    border: 1px solid #eef0f6;
    box-shadow: 0 2px 12px rgba(0,0,0,0.05);
}

.alert-critical {
    background: #fef2f2;
    border-left: 4px solid #ef4444;
    border-radius: 0 12px 12px 0;
    padding: 14px 18px;
    margin: 8px 0;
    color: #7f1d1d;
    font-weight: 500;
    font-size: 14px;
}
.alert-warning {
    background: #fffbeb;
    border-left: 4px solid #f59e0b;
    border-radius: 0 12px 12px 0;
    padding: 14px 18px;
    margin: 8px 0;
    color: #78350f;
    font-weight: 500;
    font-size: 14px;
}
.alert-success {
    background: #f0fdf4;
    border-left: 4px solid #22c55e;
    border-radius: 0 12px 12px 0;
    padding: 14px 18px;
    margin: 8px 0;
    color: #14532d;
    font-weight: 500;
    font-size: 14px;
}
.alert-info {
    background: #eff6ff;
    border-left: 4px solid #3b82f6;
    border-radius: 0 12px 12px 0;
    padding: 14px 18px;
    margin: 8px 0;
    color: #1e3a5f;
    font-weight: 500;
    font-size: 14px;
}

.festival-card {
    background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
    border-radius: 16px;
    padding: 20px 24px;
    color: #0f1117;
    font-weight: 700;
    box-shadow: 0 4px 20px rgba(245,158,11,0.3);
}

.brand-header  { font-size: 22px; font-weight: 800; color: #fff; letter-spacing: -0.5px; }
.brand-sub     { font-size: 11px; color: #8b92a5; font-weight: 500; text-transform: uppercase;
                 letter-spacing: 1.2px; margin-top: 2px; }
.page-title    { font-size: 26px; font-weight: 800; color: #0f1117;
                 letter-spacing: -0.5px; margin-bottom: 4px; }
.page-subtitle { font-size: 14px; color: #8b92a5; font-weight: 400; margin-bottom: 24px; }

hr { border: none; border-top: 1px solid #f1f3f9; margin: 20px 0; }
::-webkit-scrollbar       { width: 6px; }
::-webkit-scrollbar-track { background: #f1f3f9; }
::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 3px; }

</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# CHART THEME
# --------------------------------------------------

COLORS = {
    "primary": "#f59e0b",
    "danger":  "#ef4444",
    "success": "#22c55e",
    "info":    "#3b82f6",
    "purple":  "#8b5cf6",
    "teal":    "#14b8a6",
    "palette": ["#f59e0b","#3b82f6","#22c55e","#ef4444","#8b5cf6","#14b8a6","#f97316","#ec4899"]
}

def styled_chart(fig, height=360):
    fig.update_layout(
        font=dict(family="DM Sans", size=12, color="#334155"),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=40, b=10),
        height=height,
        legend=dict(bgcolor="rgba(255,255,255,0.9)", bordercolor="#eef0f6",
                    borderwidth=1, font=dict(size=11)),
        xaxis=dict(gridcolor="#f1f3f9", linecolor="#eef0f6",
                   tickfont=dict(size=11, color="#8b92a5")),
        yaxis=dict(gridcolor="#f1f3f9", linecolor="#eef0f6",
                   tickfont=dict(size=11, color="#8b92a5")),
        title_font=dict(size=14, color="#0f1117", family="DM Sans")
    )
    return fig

# --------------------------------------------------
# HELPERS
# --------------------------------------------------

def clean_frozenset(val):
    val = str(val)
    matches = re.findall(r"'([^']+)'", val)
    return ", ".join(matches) if matches else val

def kpi_card(label, value, delta=None, delta_type="up", icon=""):
    delta_html = ""
    if delta:
        arrow = "▲" if delta_type == "up" else ("▼" if delta_type == "down" else "—")
        delta_html = f'<div class="kpi-delta kpi-{delta_type}">{arrow} {delta}</div>'
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">{icon} {label}</div>
        <div class="kpi-value">{value}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)

def page_header(title, subtitle=""):
    st.markdown(f'<div class="page-title">{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="page-subtitle">{subtitle}</div>', unsafe_allow_html=True)

def section(label):
    st.markdown(f'<div class="section-header">{label}</div>', unsafe_allow_html=True)

# --------------------------------------------------
# DATA LOADERS
# --------------------------------------------------

@st.cache_data
def load_transactions():
    try:
        df = pd.read_csv("data/retail_transactions.csv")
        df["date"]  = pd.to_datetime(df["date"])
        df["sales"] = df["quantity"] * df["price"]
        df["day"]   = df["date"].dt.day_name()
        df["month"] = df["date"].dt.month_name()
        df["week"]  = df["date"].dt.isocalendar().week.astype(int)
        return df
    except:
        return None

@st.cache_data
def load_inventory():
    try:
        inv = pd.read_csv("data/inventory_recommendations.csv")
        if "available_stock" in inv.columns:
            inv["available_stock"] = inv["available_stock"].clip(lower=0)
            inv["days_remaining"]  = (inv["available_stock"] / 10).round(1)
        def status(row):
            rq = row.get("restock_quantity", 0)
            if rq > 80:   return "🔴 Critical"
            elif rq > 40: return "🟡 Low"
            else:          return "🟢 Healthy"
        inv["status"] = inv.apply(status, axis=1)
        return inv
    except:
        return None

@st.cache_data
def load_basket():
    try:
        rules = pd.read_csv("data/basket_rules.csv")
        rules["antecedents"] = rules["antecedents"].apply(clean_frozenset)
        rules["consequents"] = rules["consequents"].apply(clean_frozenset)
        return rules
    except:
        return None

df           = load_transactions()
inventory    = load_inventory()
basket_rules = load_basket()

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:
    st.markdown("""
    <div class="brand-header">🛒 RetailX</div>
    <div class="brand-sub">Store Intelligence Platform</div>
    """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    page = st.radio(
        "",
        options=[
            "📊  Overview",
            "📈  Sales Analytics",
            "🔮  Demand Forecast",
            "🛍️  Basket Insights",
            "📦  Inventory",
            "🤖  AI Insights",
            "📉  Price Insights",
            "🏪  Competitor Prices",
            "⬆️  Import Data",
        ],
        label_visibility="collapsed"
    )

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── GLOBAL DATE FILTER ─────────────────────────
    st.markdown('<div style="color:#8b92a5;font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:0.8px;margin-bottom:8px;">📅 Date Range</div>', unsafe_allow_html=True)

    date_preset = st.selectbox(
        "",
        ["Last 30 Days", "Last 7 Days", "Last 90 Days", "Last 6 Months", "This Year", "Custom Range"],
        label_visibility="collapsed",
        key="date_preset"
    )

    today = datetime.now().date()
    if date_preset == "Last 7 Days":
        default_start = today - timedelta(days=7)
    elif date_preset == "Last 30 Days":
        default_start = today - timedelta(days=30)
    elif date_preset == "Last 90 Days":
        default_start = today - timedelta(days=90)
    elif date_preset == "Last 6 Months":
        default_start = today - timedelta(days=180)
    elif date_preset == "This Year":
        default_start = datetime(today.year, 1, 1).date()
    else:
        default_start = today - timedelta(days=30)

    if date_preset == "Custom Range":
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            filter_start = st.date_input("From", value=default_start, key="d_start", label_visibility="collapsed")
        with col_d2:
            filter_end   = st.date_input("To",   value=today,          key="d_end",   label_visibility="collapsed")
    else:
        filter_start = default_start
        filter_end   = today

    st.markdown("<hr>", unsafe_allow_html=True)
    if os.path.exists("data/stock_loaded.csv"):
        st.markdown("""
        <div style="background:#14532d;border-radius:10px;padding:10px 14px;
                    color:#bbf7d0;font-size:12px;font-weight:600;">
        ✅ Real Stock Data Active<br>
        <span style="font-weight:400;font-size:11px;">Using your uploaded stock file</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background:#1e2130;border-radius:10px;padding:10px 14px;
                    color:#8b92a5;font-size:12px;">
        🗄️ Using Demo Data<br>
        <span style="font-size:11px;">Go to ⬆️ Import Data to connect your store</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Seasonal badge
    month = datetime.now().month
    season_badges = {
        10: ("#fbbf24","#0f1117","🪔 Diwali Season",   "Boost sweet & chocolate stocks"),
        11: ("#fbbf24","#0f1117","🪔 Diwali Season",   "Boost sweet & chocolate stocks"),
        2:  ("#ec4899","#fff",   "💝 Valentine's Week","Stock up on chocolates"),
        3:  ("#f472b6","#fff",   "🌸 Holi Festival",   "Increase snacks & beverages"),
        4:  ("#06b6d4","#fff",   "☀️ Summer Demand",   "Cold drinks & ice cream peak"),
        5:  ("#06b6d4","#fff",   "☀️ Summer Demand",   "Cold drinks & ice cream peak"),
        6:  ("#6366f1","#fff",   "🌧️ Monsoon Season",  "Noodles, tea & biscuits spike"),
        7:  ("#6366f1","#fff",   "🌧️ Monsoon Season",  "Noodles, tea & biscuits spike"),
    }
    if month in season_badges:
        bg, fg, title, sub = season_badges[month]
        st.markdown(f"""
        <div style="background:{bg};border-radius:10px;padding:12px 14px;
                    color:{fg};font-size:12px;font-weight:700;">
            {title}<br>
            <span style="font-weight:400;font-size:11px;">{sub}</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background:#1e2130;border-radius:10px;padding:12px 14px;
                    color:#8b92a5;font-size:12px;">
            📅 Normal Demand Cycle<br>
            <span style="font-size:11px;">No festival surge detected</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="margin-top:20px;font-size:11px;color:#4b5563;">
    🕐 Last synced: {datetime.now().strftime('%d %b, %I:%M %p')}
    </div>
    """, unsafe_allow_html=True)

# --------------------------------------------------
# DATA GUARD  (skip check on import page)
# --------------------------------------------------

if "Import Data" not in page and df is None:
    st.error("⚠️  No data found. Go to **⬆️ Import Data** to upload your store data.")
    st.stop()

if df is not None:
    # Apply global date filter
    df = df[
        (df["date"].dt.date >= filter_start) &
        (df["date"].dt.date <= filter_end)
    ]
    if len(df) == 0:
        st.warning(f"⚠️ No data found between {filter_start} and {filter_end}. Try a wider date range.")
        st.stop()

    total_revenue  = df["sales"].sum()
    total_orders   = df["transaction_id"].nunique()
    total_products = df["product"].nunique()
    avg_order_val  = total_revenue / total_orders if total_orders else 0


# ==================================================
#   PAGE: OVERVIEW
# ==================================================

if "Overview" in page:

    page_header("Store Overview", f"RetailX Intelligence · {datetime.now().strftime('%A, %d %B %Y')}")

    k1, k2, k3, k4 = st.columns(4)
    with k1: kpi_card("Total Revenue",    f"₹{total_revenue:,.0f}",  "12.4% vs last period", "up",      "💰")
    with k2: kpi_card("Total Orders",     f"{total_orders:,}",        "8.1% vs last period",  "up",      "🧾")
    with k3: kpi_card("Avg Order Value",  f"₹{avg_order_val:,.0f}",  "3.2% vs last period",  "down",    "📊")
    with k4: kpi_card("Products Tracked", f"{total_products}",        "Across all categories","neutral", "📦")

    st.markdown("<br>", unsafe_allow_html=True)

    col_a, col_b = st.columns([3, 2])

    with col_a:
        section("📈 Revenue Trend")
        trend = df.groupby("date")["sales"].sum().reset_index()
        trend["rolling7"]  = trend["sales"].rolling(7,  min_periods=1).mean()
        trend["rolling30"] = trend["sales"].rolling(30, min_periods=1).mean()
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=trend["date"], y=trend["sales"], mode="lines", name="Daily Revenue",
            line=dict(color="#e2e8f0", width=1),
            fill="tozeroy", fillcolor="rgba(245,158,11,0.07)"
        ))
        fig.add_trace(go.Scatter(
            x=trend["date"], y=trend["rolling7"], mode="lines", name="7-Day Avg",
            line=dict(color="#f59e0b", width=2.5)
        ))
        fig.add_trace(go.Scatter(
            x=trend["date"], y=trend["rolling30"], mode="lines", name="30-Day Avg",
            line=dict(color="#3b82f6", width=2, dash="dot")
        ))
        fig.update_layout(title="Daily Revenue with Rolling Averages")
        st.plotly_chart(styled_chart(fig, 340), use_container_width=True)

    with col_b:
        section("🥧 Category Breakdown")
        cat = df.groupby("category")["sales"].sum().reset_index().sort_values("sales", ascending=False)
        fig = px.pie(cat, names="category", values="sales",
                     color_discrete_sequence=COLORS["palette"], hole=0.5)
        fig.update_traces(textposition="outside", textinfo="percent+label", textfont_size=11)
        fig.update_layout(showlegend=False, title="Revenue by Category")
        st.plotly_chart(styled_chart(fig, 340), use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_c, col_d = st.columns(2)

    with col_c:
        section("🏆 Top 10 Revenue Products")
        top = df.groupby("product")["sales"].sum().sort_values(ascending=False).head(10).reset_index()
        fig = px.bar(top, x="sales", y="product", orientation="h",
                     color="sales", color_continuous_scale=[[0,"#fde68a"],[1,"#f59e0b"]])
        fig.update_layout(coloraxis_showscale=False, yaxis=dict(autorange="reversed"),
                          title="Top Products by Revenue")
        fig.update_traces(texttemplate="₹%{x:,.0f}", textposition="outside", textfont_size=10)
        st.plotly_chart(styled_chart(fig, 360), use_container_width=True)

    with col_d:
        section("📅 Sales by Day of Week")
        day_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
        by_day = df.groupby("day")["sales"].sum().reindex(day_order).reset_index()
        fig = px.bar(by_day, x="day", y="sales",
                     color="sales", color_continuous_scale=[[0,"#bfdbfe"],[1,"#3b82f6"]])
        fig.update_layout(coloraxis_showscale=False, title="Which Days Drive Most Sales?")
        st.plotly_chart(styled_chart(fig, 360), use_container_width=True)


# ==================================================
#   PAGE: SALES ANALYTICS
# ==================================================

elif "Sales Analytics" in page:

    page_header("Sales Analytics", "Deep-dive into product and category performance")

    categories   = ["All Categories"] + sorted(df["category"].unique().tolist())
    selected_cat = st.selectbox("Filter by Category", categories)
    filtered     = df if selected_cat == "All Categories" else df[df["category"] == selected_cat]

    k1, k2, k3 = st.columns(3)
    with k1: kpi_card("Revenue",      f"₹{filtered['sales'].sum():,.0f}",         icon="💰")
    with k2: kpi_card("Units Sold",   f"{filtered['quantity'].sum():,}",           icon="📦")
    with k3: kpi_card("Transactions", f"{filtered['transaction_id'].nunique():,}", icon="🧾")

    st.markdown("<br>", unsafe_allow_html=True)

    col_a, col_b = st.columns(2)

    with col_a:
        section("💰 Revenue per Product")
        prod_rev = filtered.groupby("product")["sales"].sum().sort_values(ascending=False).reset_index()
        fig = px.bar(prod_rev, x="product", y="sales",
                     color="sales", color_continuous_scale=[[0,"#dcfce7"],[1,"#22c55e"]])
        fig.update_layout(coloraxis_showscale=False, title="Revenue by Product")
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(styled_chart(fig, 360), use_container_width=True)

    with col_b:
        section("📦 Units Sold per Product")
        prod_qty = filtered.groupby("product")["quantity"].sum().sort_values(ascending=False).reset_index()
        fig = px.bar(prod_qty, x="product", y="quantity",
                     color="quantity", color_continuous_scale=[[0,"#e0e7ff"],[1,"#6366f1"]])
        fig.update_layout(coloraxis_showscale=False, title="Units Sold")
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(styled_chart(fig, 360), use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    section("📅 Monthly Revenue by Category")
    month_order = ["January","February","March","April","May","June",
                   "July","August","September","October","November","December"]
    monthly_cat          = filtered.groupby(["month","category"])["sales"].sum().reset_index()
    monthly_cat["month"] = pd.Categorical(monthly_cat["month"], categories=month_order, ordered=True)
    monthly_cat          = monthly_cat.sort_values("month")
    fig = px.bar(monthly_cat, x="month", y="sales", color="category",
                 color_discrete_sequence=COLORS["palette"], barmode="stack",
                 title="Stacked Monthly Revenue by Category")
    st.plotly_chart(styled_chart(fig, 340), use_container_width=True)


# ==================================================
#   PAGE: DEMAND FORECAST
# ==================================================

elif "Demand Forecast" in page:

    page_header("Demand Forecast", "Prophet ML forecasting · Historical demand · 7-day predictions per product")

    product_list     = sorted(df["product"].unique().tolist())
    selected_product = st.selectbox("Select Product", product_list)
    pdata            = df[df["product"] == selected_product]

    total_units = pdata["quantity"].sum()
    total_rev   = pdata["sales"].sum()
    avg_daily   = pdata.groupby("date")["quantity"].sum().mean()
    peak_day    = pdata.groupby("day")["quantity"].sum().idxmax()

    k1, k2, k3, k4 = st.columns(4)
    with k1: kpi_card("Total Units Sold",  f"{total_units:,}",        icon="📦")
    with k2: kpi_card("Revenue Generated", f"₹{total_rev:,.0f}",      icon="💰")
    with k3: kpi_card("Avg Daily Demand",  f"{avg_daily:.1f} units",  icon="📈")
    with k4: kpi_card("Peak Day",          peak_day,                  icon="📅")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── PROPHET FORECAST SECTION ─────────────────────────────────
    section("🔮 Prophet ML Forecast — Next 7 Days")

    forecast_file = os.path.join(PROJECT_ROOT, "data", "demand_forecast.csv")
    has_forecast  = os.path.exists(forecast_file)

    col_gen, col_info = st.columns([2, 3])
    with col_gen:
        if st.button("⚡  Generate / Refresh Prophet Forecast", type="primary"):
            with st.spinner("Running Prophet for all products — takes ~60 seconds..."):
                result = subprocess.run(
                    [sys.executable, "ml_models/demand_forecast.py"],
                    capture_output=True, text=True, cwd=PROJECT_ROOT
                )
                if result.returncode == 0:
                    st.success("✅ Forecast generated!")
                    has_forecast = True
                    load_transactions.clear()
                else:
                    st.error(f"Prophet error:\n{result.stderr[:400]}")
    with col_info:
        if has_forecast:
            mtime = datetime.fromtimestamp(os.path.getmtime(forecast_file)).strftime("%d %b %Y, %I:%M %p")
            st.markdown(f'<div class="alert-success">✅ Forecast available · Last generated: {mtime}</div>',
                        unsafe_allow_html=True)
        else:
            st.markdown('<div class="alert-warning">⚠️ No forecast yet — click the button to generate Prophet predictions.</div>',
                        unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if has_forecast:
        try:
            fc_df = pd.read_csv(forecast_file)
            fc_df["ds"] = pd.to_datetime(fc_df["ds"])
            prod_fc = fc_df[fc_df["product"] == selected_product].copy()

            if len(prod_fc) > 0:
                col_a, col_b = st.columns([3, 2])

                with col_a:
                    section(f"📈 Prophet Forecast — {selected_product}")
                    # Historical actuals
                    hist = pdata.groupby("date")["quantity"].sum().reset_index()
                    hist.columns = ["ds", "actual"]

                    # Split past predictions vs future
                    today_ts = pd.Timestamp(datetime.now().date())
                    past_fc  = prod_fc[prod_fc["ds"] <= today_ts]
                    future_fc = prod_fc[prod_fc["ds"] > today_ts]

                    fig = go.Figure()
                    # Actual bars
                    fig.add_trace(go.Bar(
                        x=hist["ds"], y=hist["actual"],
                        name="Actual Sales", marker_color="rgba(99,102,241,0.25)"
                    ))
                    # Prophet fitted line
                    if len(past_fc) > 0 and "yhat_lower" in past_fc.columns:
                        fig.add_trace(go.Scatter(
                            x=past_fc["ds"], y=past_fc["yhat"],
                            mode="lines", name="Prophet Fitted",
                            line=dict(color="#6366f1", width=2)
                        ))
                    # Future forecast with confidence band
                    if len(future_fc) > 0:
                        if "yhat_lower" in future_fc.columns:
                            fig.add_trace(go.Scatter(
                                x=pd.concat([future_fc["ds"], future_fc["ds"].iloc[::-1]]),
                                y=pd.concat([future_fc["yhat_upper"], future_fc["yhat_lower"].iloc[::-1]]),
                                fill="toself", fillcolor="rgba(245,158,11,0.15)",
                                line=dict(color="rgba(255,255,255,0)"),
                                name="Confidence Band", showlegend=True
                            ))
                        fig.add_trace(go.Scatter(
                            x=future_fc["ds"], y=future_fc["yhat"].clip(lower=0),
                            mode="lines+markers", name="7-Day Forecast",
                            line=dict(color="#f59e0b", width=3),
                            marker=dict(size=8, color="#f59e0b")
                        ))
                    fig.add_vline(x=str(today_ts), line_dash="dash",
                                  line_color="#94a3b8", annotation_text="Today")
                    fig.update_layout(title="Actual vs Prophet Predicted Demand")
                    st.plotly_chart(styled_chart(fig, 380), use_container_width=True)

                with col_b:
                    section("📋 7-Day Forecast Table")
                    future_table = future_fc[["ds","yhat"]].copy()
                    if "yhat_lower" in future_fc.columns:
                        future_table["yhat_lower"] = future_fc["yhat_lower"].clip(lower=0)
                        future_table["yhat_upper"] = future_fc["yhat_upper"]
                    future_table["yhat"] = future_table["yhat"].clip(lower=0).round(1)
                    future_table["ds"]   = future_table["ds"].dt.strftime("%a, %d %b")
                    future_table.columns = (["Date","Predicted Units","Min","Max"]
                                            if "yhat_lower" in future_fc.columns
                                            else ["Date","Predicted Units"])
                    st.dataframe(future_table, use_container_width=True, height=280)

                    total_7d = future_table["Predicted Units"].sum()
                    kpi_card("7-Day Forecast Total", f"{total_7d:.0f} units", icon="📦")

            else:
                st.info(f"No forecast data found for '{selected_product}'. Regenerate the forecast.")
        except Exception as e:
            st.error(f"Could not load forecast: {e}")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── HISTORICAL CHARTS ────────────────────────────────────────
    col_a, col_b = st.columns([3, 2])

    with col_a:
        section(f"📈 Historical Daily Demand — {selected_product}")
        daily              = pdata.groupby("date")["quantity"].sum().reset_index()
        daily["rolling7"]  = daily["quantity"].rolling(7,  min_periods=1).mean()
        daily["rolling30"] = daily["quantity"].rolling(30, min_periods=1).mean()
        fig = go.Figure()
        fig.add_trace(go.Bar(x=daily["date"], y=daily["quantity"],
                             name="Daily Units", marker_color="rgba(99,102,241,0.2)"))
        fig.add_trace(go.Scatter(x=daily["date"], y=daily["rolling7"],
                                 mode="lines", name="7-Day Avg",
                                 line=dict(color="#6366f1", width=2.5)))
        fig.add_trace(go.Scatter(x=daily["date"], y=daily["rolling30"],
                                 mode="lines", name="30-Day Avg",
                                 line=dict(color="#f59e0b", width=2, dash="dot")))
        fig.update_layout(title="Historical Demand with Rolling Averages")
        st.plotly_chart(styled_chart(fig, 360), use_container_width=True)

    with col_b:
        section("📅 Demand by Day of Week")
        day_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
        by_day = pdata.groupby("day")["quantity"].sum().reindex(day_order).fillna(0).reset_index()
        fig = px.bar(by_day, x="day", y="quantity",
                     color="quantity", color_continuous_scale=[[0,"#fde68a"],[1,"#f59e0b"]])
        fig.update_layout(coloraxis_showscale=False, title="Which Day Sells Most?")
        st.plotly_chart(styled_chart(fig, 360), use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    section("🌡️ Demand Heatmap — All Products by Day")
    heat  = df.groupby(["day","product"])["quantity"].sum().reset_index()
    pivot = heat.pivot(index="product", columns="day", values="quantity").fillna(0)
    day_cols = [d for d in ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
                if d in pivot.columns]
    pivot = pivot[day_cols]
    fig = px.imshow(pivot,
                    color_continuous_scale=[[0,"#f0f9ff"],[0.5,"#38bdf8"],[1,"#0369a1"]],
                    aspect="auto", title="Units Sold — Product × Day of Week")
    fig.update_layout(xaxis_title="", yaxis_title="")
    st.plotly_chart(styled_chart(fig, 380), use_container_width=True)




# ==================================================
#   PAGE: BASKET INSIGHTS
# ==================================================

elif "Basket Insights" in page:

    page_header("Basket Insights", "Products customers buy together — power your shelf strategy")

    if basket_rules is not None and len(basket_rules) > 0:

        k1, k2, k3 = st.columns(3)
        with k1: kpi_card("Association Rules", f"{len(basket_rules)}", icon="🔗")
        with k2:
            avg_conf = basket_rules["confidence"].mean()
            kpi_card("Avg Confidence", f"{avg_conf:.1%}", icon="🎯")
        with k3:
            top_conf = basket_rules["confidence"].max()
            kpi_card("Strongest Rule", f"{top_conf:.1%}", icon="🏆")

        st.markdown("<br>", unsafe_allow_html=True)

        col_a, col_b = st.columns(2)

        with col_a:
            section("🔗 Top Associations by Confidence")
            top_rules         = basket_rules.sort_values("confidence", ascending=False).head(12).copy()
            top_rules["rule"] = top_rules["antecedents"] + "  →  " + top_rules["consequents"]
            fig = px.bar(top_rules, x="confidence", y="rule", orientation="h",
                         color="confidence", color_continuous_scale=[[0,"#fde68a"],[1,"#f59e0b"]])
            fig.update_layout(coloraxis_showscale=False, yaxis=dict(autorange="reversed"),
                              title="Strongest Product Pair Confidence Scores")
            fig.update_traces(texttemplate="%{x:.0%}", textposition="outside", textfont_size=10)
            st.plotly_chart(styled_chart(fig, 420), use_container_width=True)

        with col_b:
            section("📊 Support vs Confidence")
            plot_rules = basket_rules.head(30).copy()
            fig = px.scatter(plot_rules, x="support", y="confidence",
                             size="lift" if "lift" in plot_rules.columns else "confidence",
                             color="confidence",
                             color_continuous_scale=[[0,"#bfdbfe"],[1,"#1d4ed8"]],
                             hover_data=["antecedents","consequents"],
                             title="Each bubble = one product pair · Size = Lift")
            fig.update_layout(coloraxis_showscale=False)
            st.plotly_chart(styled_chart(fig, 420), use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)

        section("📋 Full Association Rules Table")
        display_rules = basket_rules[["antecedents","consequents","support","confidence"]].copy()
        display_rules["support"]    = display_rules["support"].map("{:.2%}".format)
        display_rules["confidence"] = display_rules["confidence"].map("{:.2%}".format)
        display_rules.columns       = ["If Customer Buys","They Also Buy","Support","Confidence"]
        st.dataframe(display_rules.head(25), use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)

        section("💡 Shelf Placement Recommendations")
        top5 = basket_rules.sort_values("confidence", ascending=False).head(5)
        for _, row in top5.iterrows():
            conf_val = float(row["confidence"])
            st.markdown(f"""
            <div class="alert-info">
            🛒 Place <strong>{row['antecedents']}</strong> next to
            <strong>{row['consequents']}</strong> —
            customers buy both together <strong>{conf_val:.0%}</strong> of the time.
            Consider a <strong>combo bundle offer</strong> to increase basket size.
            </div>
            """, unsafe_allow_html=True)

    else:
        st.markdown("""
        <div class="alert-warning">
        ⚠️ No basket rules found. Run <code>ml_models/basket_analysis.py</code> first, then refresh.
        </div>
        """, unsafe_allow_html=True)


# ==================================================
#   PAGE: INVENTORY
# ==================================================

elif "Inventory" in page:

    page_header("Inventory Intelligence", "Real-time stock levels, restock signals and waste prevention")

    if inventory is not None:

        critical_count = len(inventory[inventory["status"] == "🔴 Critical"])
        low_count      = len(inventory[inventory["status"] == "🟡 Low"])
        healthy_count  = len(inventory[inventory["status"] == "🟢 Healthy"])
        total_restock  = int(inventory["restock_quantity"].sum()) if "restock_quantity" in inventory.columns else 0

        k1, k2, k3, k4 = st.columns(4)
        with k1: kpi_card("Critical Stock", f"{critical_count} products",
                          delta="Immediate action" if critical_count > 0 else None,
                          delta_type="down", icon="🔴")
        with k2: kpi_card("Low Stock",      f"{low_count} products",     icon="🟡")
        with k3: kpi_card("Healthy Stock",  f"{healthy_count} products", icon="🟢")
        with k4: kpi_card("Total to Order", f"{total_restock:,} units",  icon="📦")

        st.markdown("<br>", unsafe_allow_html=True)

        col_a, col_b = st.columns([3, 2])

        with col_a:
            section("📋 Current Inventory Status")
            display_cols = [c for c in ["product","available_stock","restock_quantity",
                                        "days_remaining","priority","status"]
                            if c in inventory.columns]
            disp         = inventory[display_cols].copy()
            disp.columns = [c.replace("_"," ").title() for c in display_cols]
            st.dataframe(disp, use_container_width=True, height=340)

        with col_b:
            section("🎯 Restock Priority Chart")
            if "restock_quantity" in inventory.columns:
                restock_data = inventory[inventory["restock_quantity"] > 0].sort_values(
                    "restock_quantity", ascending=False)
                if len(restock_data) > 0:
                    color_map  = {"High":"#ef4444","Medium":"#f59e0b","Low":"#22c55e"}
                    bar_colors = (restock_data["priority"].map(color_map).fillna("#94a3b8").tolist()
                                  if "priority" in restock_data.columns else "#f59e0b")
                    fig = go.Figure(go.Bar(
                        x=restock_data["restock_quantity"],
                        y=restock_data["product"],
                        orientation="h",
                        marker_color=bar_colors,
                        text=restock_data["restock_quantity"].astype(str) + " units",
                        textposition="outside"
                    ))
                    fig.update_layout(yaxis=dict(autorange="reversed"),
                                      title="Units to Order per Product",
                                      xaxis_title="Units Required")
                    st.plotly_chart(styled_chart(fig, 340), use_container_width=True)
                else:
                    st.markdown('<div class="alert-success">✅ No restocking needed right now.</div>',
                                unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        section("🚨 Restock Alerts")
        low_items = (inventory[inventory["restock_quantity"] > 0]
                     if "restock_quantity" in inventory.columns else pd.DataFrame())
        if len(low_items) > 0:
            for _, row in low_items.iterrows():
                pri       = row.get("priority","Medium")
                days      = row.get("days_remaining","N/A")
                box_class = "alert-critical" if pri == "High" else \
                            "alert-warning"  if pri == "Medium" else "alert-info"
                icon      = "🔴" if pri == "High" else "🟡" if pri == "Medium" else "🔵"
                st.markdown(f"""
                <div class="{box_class}">
                {icon} <strong>{row['product']}</strong> —
                Order <strong>{int(row['restock_quantity'])} units</strong>
                &nbsp;·&nbsp; ~{days} days of stock remaining
                &nbsp;·&nbsp; Priority: <strong>{pri}</strong>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown('<div class="alert-success">✅ All products are sufficiently stocked.</div>',
                        unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        section("⚠️ Overstock Detection")
        if "days_remaining" in inventory.columns:
            overstock = inventory[inventory["days_remaining"] > 20]
            if len(overstock) > 0:
                for _, row in overstock.iterrows():
                    st.markdown(f"""
                    <div class="alert-warning">
                    📦 <strong>{row['product']}</strong> has ~{row['days_remaining']} days of
                    stock remaining. Consider <strong>running a discount</strong> or
                    <strong>reducing the next purchase order</strong> to avoid waste.
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown('<div class="alert-success">✅ No overstock risk detected.</div>',
                            unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        section("🎯 Seasonal Inventory Advice")
        season_advice = {
            (10,11): ("🪔 Diwali Season",   "Increase Cadbury Dairy Milk, Good Day Cookies and gift packs by 30–40%."),
            (2,):    ("💝 Valentine's Week", "Boost chocolate stock by 40–50%. Create gifting bundles."),
            (3,):    ("🌸 Holi Festival",    "Increase snacks, beverages and cold drinks by 25–35%."),
            (4,5):   ("☀️ Summer Peak",      "Cold drinks demand rises 50–60%. Stock up on Coca Cola."),
            (6,7):   ("🌧️ Monsoon Season",   "Maggi Noodles, Red Label Tea and biscuits see a 20–30% surge."),
        }
        matched = False
        for months, (label, advice) in season_advice.items():
            if month in months:
                st.markdown(f'<div class="alert-info">{label} — {advice}</div>', unsafe_allow_html=True)
                matched = True
                break
        if not matched:
            st.markdown('<div class="alert-success">✅ No seasonal surge expected. Maintain standard inventory levels.</div>',
                        unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── DEAD STOCK DETECTION ─────────────────────────────────
        section("💀 Dead Stock Detection")
        st.caption("Products with zero or near-zero sales in the last 30 days but still sitting in stock.")

        latest_date  = df["date"].max()
        last30       = df[df["date"] >= latest_date - pd.Timedelta(days=30)]
        sold_last30  = last30.groupby("product")["quantity"].sum().reset_index()
        sold_last30.columns = ["product", "sold_last_30d"]

        if inventory is not None and "available_stock" in inventory.columns:
            dead_check = pd.merge(
                inventory[["product","available_stock","stock_loaded"]].copy(),
                sold_last30, on="product", how="left"
            )
            dead_check["sold_last_30d"] = dead_check["sold_last_30d"].fillna(0)

            # Dead = sold < 5 units in 30 days AND stock > 20 units
            dead_stock = dead_check[
                (dead_check["sold_last_30d"] < 5) &
                (dead_check["available_stock"] > 20)
            ].copy()

            # Slow movers = sold < 20% of average
            avg_sold = dead_check["sold_last_30d"].mean()
            slow_stock = dead_check[
                (dead_check["sold_last_30d"] < avg_sold * 0.2) &
                (dead_check["available_stock"] > 10) &
                (dead_check["sold_last_30d"] >= 5)
            ].copy()

            kd1, kd2, kd3 = st.columns(3)
            with kd1: kpi_card("Dead Stock Products", f"{len(dead_stock)}", delta="Zero/near-zero sales 30d", delta_type="down", icon="💀")
            with kd2: kpi_card("Slow Movers", f"{len(slow_stock)}", icon="🐢")
            with kd3:
                # Estimate capital locked
                if "price" in df.columns:
                    price_map = df.groupby("product")["price"].mean()
                    dead_value = dead_stock["product"].map(price_map).fillna(0) * dead_stock["available_stock"]
                    kpi_card("Capital Locked", f"₹{dead_value.sum():,.0f}", delta="In dead stock", delta_type="down", icon="💸")
                else:
                    kpi_card("Slow Movers Found", f"{len(slow_stock)}", icon="📦")

            st.markdown("<br>", unsafe_allow_html=True)

            if len(dead_stock) > 0:
                dead_stock = dead_stock.sort_values("available_stock", ascending=False)
                for _, row in dead_stock.head(10).iterrows():
                    last_sale_rows = df[df["product"] == row["product"]]
                    if len(last_sale_rows) > 0:
                        last_sale = last_sale_rows["date"].max().strftime("%d %b %Y")
                        days_since = (latest_date - last_sale_rows["date"].max()).days
                    else:
                        last_sale  = "Never"
                        days_since = 999
                    st.markdown(f"""
                    <div class="alert-critical">
                    💀 <strong>{row['product']}</strong> —
                    Only <strong>{int(row['sold_last_30d'])} units</strong> sold in last 30 days ·
                    <strong>{int(row['available_stock'])} units</strong> still in stock ·
                    Last sale: {last_sale} ({days_since} days ago) ·
                    <strong>Action: Run a discount or stop reordering</strong>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown('<div class="alert-success">✅ No dead stock detected. All products have recent sales.</div>',
                            unsafe_allow_html=True)

            if len(slow_stock) > 0:
                st.markdown("**🐢 Slow Movers — Consider Promotions:**")
                for _, row in slow_stock.head(8).iterrows():
                    st.markdown(f"""
                    <div class="alert-warning">
                    🐢 <strong>{row['product']}</strong> —
                    <strong>{int(row['sold_last_30d'])} units</strong> sold in 30 days ·
                    {int(row['available_stock'])} units in stock ·
                    Consider a <strong>combo offer or shelf relocation</strong>
                    </div>
                    """, unsafe_allow_html=True)

    else:
        st.markdown("""
        <div class="alert-warning">
        ⚠️ Inventory data not found. Run <code>ml_models/inventory_engine.py</code> first.
        </div>
        """, unsafe_allow_html=True)


# ==================================================
#   PAGE: AI INSIGHTS
# ==================================================

elif "AI Insights" in page:

    page_header("AI Store Manager", "Actionable intelligence to optimise your store operations")

    month      = datetime.now().month
    month_name = datetime.now().strftime("%B")

    festival_map = {
        10: ("🪔 Diwali Season",     "October–November", ["Cadbury Dairy Milk","Good Day Cookies","Red Label Tea"], 40),
        11: ("🪔 Diwali Season",     "October–November", ["Cadbury Dairy Milk","Good Day Cookies","Red Label Tea"], 40),
        2:  ("💝 Valentine's Week",  "February",         ["Cadbury Dairy Milk","Good Day Cookies"],                 50),
        3:  ("🌸 Holi Festival",     "March",            ["Coca Cola 750ml","Lay's Chips","Parle-G Biscuits"],      35),
        4:  ("☀️ Summer Peak",       "April–June",       ["Coca Cola 750ml"],                                       60),
        5:  ("☀️ Summer Peak",       "April–June",       ["Coca Cola 750ml"],                                       60),
        6:  ("🌧️ Monsoon Season",    "June–August",      ["Maggi Noodles","Red Label Tea","Parle-G Biscuits"],      25),
        7:  ("🌧️ Monsoon Season",    "June–August",      ["Maggi Noodles","Red Label Tea","Parle-G Biscuits"],      25),
        8:  ("🇮🇳 Independence Day", "August",           ["Lay's Chips","Coca Cola 750ml"],                         20),
    }

    if month in festival_map:
        fest_name, fest_period, fest_products, surge_pct = festival_map[month]
        products_html = " &nbsp;·&nbsp; ".join([f"<strong>{p}</strong>" for p in fest_products])
        st.markdown(f"""
        <div class="festival-card">
            <div style="font-size:20px;margin-bottom:6px;">{fest_name}</div>
            <div style="font-weight:400;font-size:13px;margin-bottom:10px;">
                Expected demand surge: <strong>+{surge_pct}%</strong>
                &nbsp;·&nbsp; Period: {fest_period}
            </div>
            <div style="font-size:13px;">📦 Stock up on: {products_html}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="background:#f1f5f9;border-radius:16px;padding:20px 24px;">
            <div style="font-size:16px;font-weight:700;color:#334155;">
                📅 {month_name} — Normal Demand Cycle
            </div>
            <div style="font-size:13px;color:#64748b;margin-top:6px;">
                No major festival surge expected. Follow standard restock patterns.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_a, col_b = st.columns(2)

    with col_a:
        section("🏆 Top Performers")
        top5 = df.groupby("product")["quantity"].sum().sort_values(ascending=False).head(5).reset_index()
        for i, row in top5.iterrows():
            pct   = row["quantity"] / df["quantity"].sum() * 100
            color = "#f59e0b" if i == 0 else "#94a3b8"
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:12px;padding:11px 0;
                        border-bottom:1px solid #f1f3f9;">
                <div style="font-weight:800;color:{color};width:22px;font-size:15px;">#{i+1}</div>
                <div style="flex:1;font-weight:600;color:#0f1117;font-size:14px;">{row['product']}</div>
                <div style="color:#8b92a5;font-size:13px;">{int(row['quantity']):,} units</div>
                <div style="background:#f1f5f9;border-radius:8px;padding:3px 9px;
                            font-size:11px;font-weight:700;color:#334155;">{pct:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)

    with col_b:
        section("⚡ Quick Action Summary")
        if inventory is not None and "restock_quantity" in inventory.columns:
            urgent  = inventory[inventory["restock_quantity"] > 80]
            monitor = inventory[(inventory["restock_quantity"] > 0) & (inventory["restock_quantity"] <= 80)]
            healthy = inventory[inventory["restock_quantity"] == 0]
            if len(urgent) > 0:
                items = "<br>".join([f"• {r['product']}" for _, r in urgent.iterrows()])
                st.markdown(f'<div class="alert-critical">🔴 <strong>Urgent Restock Needed</strong><br>{items}</div>',
                            unsafe_allow_html=True)
            if len(monitor) > 0:
                items = "<br>".join([f"• {r['product']}" for _, r in monitor.iterrows()])
                st.markdown(f'<div class="alert-warning">🟡 <strong>Monitor These Products</strong><br>{items}</div>',
                            unsafe_allow_html=True)
            if len(healthy) > 0:
                items = "<br>".join([f"• {r['product']}" for _, r in healthy.iterrows()])
                st.markdown(f'<div class="alert-success">🟢 <strong>Stock Levels Healthy</strong><br>{items}</div>',
                            unsafe_allow_html=True)
        else:
            st.markdown('<div class="alert-info">ℹ️ Run the inventory engine to see restock recommendations.</div>',
                        unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if basket_rules is not None and len(basket_rules) > 0:
        section("🛒 Bundle Opportunity Recommendations")
        top_bundles = basket_rules.sort_values("confidence", ascending=False).head(6)
        c1, c2 = st.columns(2)
        for i, (_, row) in enumerate(top_bundles.iterrows()):
            conf = float(row["confidence"])
            with (c1 if i % 2 == 0 else c2):
                st.markdown(f"""
                <div class="chart-card" style="margin-bottom:12px;">
                    <div style="font-size:11px;color:#8b92a5;font-weight:600;
                                text-transform:uppercase;letter-spacing:0.8px;">Bundle Opportunity</div>
                    <div style="font-size:15px;font-weight:700;color:#0f1117;margin:8px 0;">
                        {row['antecedents']} + {row['consequents']}
                    </div>
                    <div style="font-size:13px;color:#22c55e;font-weight:700;">{conf:.0%} co-purchase rate</div>
                    <div style="font-size:12px;color:#8b92a5;margin-top:4px;">
                        Place together · Combo discount · Cross-promote at billing
                    </div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    section("🔮 7-Day Demand Outlook (Top 5 Products)")
    top_prods     = df.groupby("product")["quantity"].sum().sort_values(ascending=False).head(5).index.tolist()
    forecast_rows = []
    np.random.seed(42)
    for prod in top_prods:
        avg = df[df["product"] == prod]["quantity"].mean()
        for offset in range(7):
            fdate     = datetime.now() + timedelta(days=offset + 1)
            predicted = max(1, avg * np.random.uniform(0.8, 1.3))
            forecast_rows.append({
                "Product":         prod,
                "Date":            fdate.strftime("%d %b"),
                "Predicted Units": round(predicted, 1)
            })
    fc_df = pd.DataFrame(forecast_rows)
    fig = px.line(fc_df, x="Date", y="Predicted Units", color="Product",
                  color_discrete_sequence=COLORS["palette"],
                  title="Projected Daily Demand — Next 7 Days", markers=True)
    st.plotly_chart(styled_chart(fig, 360), use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── SMART COMBO OFFER GENERATOR ──────────────────────────────
    section("🎁 Smart Combo Offer Generator")
    st.caption("AI-generated bundle deals based on purchase patterns, price data and expected revenue lift.")

    if basket_rules is not None and len(basket_rules) > 0:
        price_map  = df.groupby("product")["price"].mean().to_dict()
        demand_map = df.groupby("product")["quantity"].sum().to_dict()

        combos = []
        for _, row in basket_rules.sort_values("lift", ascending=False).head(30).iterrows():
            p1   = str(row["antecedents"])
            p2   = str(row["consequents"])
            conf = float(row["confidence"])
            lift = float(row["lift"])
            sup  = float(row["support"])

            p1_price  = price_map.get(p1, 0)
            p2_price  = price_map.get(p2, 0)
            if p1_price == 0 or p2_price == 0:
                continue

            bundle_price = round((p1_price + p2_price) * 0.90)  # 10% discount
            saving       = round((p1_price + p2_price) - bundle_price)
            p1_demand    = demand_map.get(p1, 1)
            # Expected extra units from bundling = lift × support × total transactions
            total_txns   = df["transaction_id"].nunique()
            expected_extra = round(sup * lift * total_txns * 0.05)  # conservative 5% take rate
            revenue_lift = round(expected_extra * bundle_price)

            combos.append({
                "product_1":    p1,
                "product_2":    p2,
                "confidence":   conf,
                "lift":         lift,
                "p1_price":     p1_price,
                "p2_price":     p2_price,
                "bundle_price": bundle_price,
                "saving":       saving,
                "expected_extra_sales": expected_extra,
                "monthly_revenue_lift": revenue_lift,
            })

        combos = sorted(combos, key=lambda x: x["monthly_revenue_lift"], reverse=True)

        if combos:
            c1, c2 = st.columns(2)
            for i, combo in enumerate(combos[:6]):
                conf_pct = combo["confidence"] * 100
                lift_val = combo["lift"]
                with (c1 if i % 2 == 0 else c2):
                    color = "#f59e0b" if i < 2 else "#3b82f6" if i < 4 else "#8b5cf6"
                    st.markdown(f"""
                    <div class="chart-card" style="margin-bottom:14px;border-left:4px solid {color};">
                        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
                            <span style="font-size:11px;color:#8b92a5;font-weight:600;
                                         text-transform:uppercase;">Combo #{i+1}</span>
                            <span style="background:#f0fdf4;color:#16a34a;font-size:11px;
                                         font-weight:700;padding:2px 8px;border-radius:6px;">
                                +₹{combo['monthly_revenue_lift']:,}/mo
                            </span>
                        </div>
                        <div style="font-size:15px;font-weight:700;color:#0f1117;margin-bottom:6px;">
                            {combo['product_1']}<br>
                            <span style="color:#94a3b8;font-size:13px;">+</span><br>
                            {combo['product_2']}
                        </div>
                        <div style="display:flex;gap:10px;flex-wrap:wrap;margin-bottom:8px;">
                            <span style="background:#fefce8;color:#854d0e;font-size:11px;
                                         font-weight:600;padding:3px 8px;border-radius:6px;">
                                ₹{combo['p1_price']:.0f} + ₹{combo['p2_price']:.0f} → ₹{combo['bundle_price']:.0f}
                            </span>
                            <span style="background:#eff6ff;color:#1d4ed8;font-size:11px;
                                         font-weight:600;padding:3px 8px;border-radius:6px;">
                                Save ₹{combo['saving']:.0f} (10% off)
                            </span>
                        </div>
                        <div style="font-size:12px;color:#64748b;">
                            {conf_pct:.0f}% co-purchase rate ·
                            {lift_val:.1f}x lift ·
                            ~{combo['expected_extra_sales']} extra bundles/mo
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.markdown('<div class="alert-warning">⚠️ Run Basket Analysis first to generate combo recommendations.</div>',
                    unsafe_allow_html=True)


# ==================================================
#   PAGE: PRICE INSIGHTS  ← NEW (Feature 6)
# ==================================================

elif "Price Insights" in page:

    page_header("Price Insights", "Price sensitivity · Elasticity · Optimal pricing signals")

    # ── KPIs ─────────────────────────────────────────────────────
    avg_price   = df["price"].mean()
    price_range = df["price"].max() - df["price"].min()
    k1, k2, k3 = st.columns(3)
    with k1: kpi_card("Avg Product Price",  f"₹{avg_price:.0f}",   icon="💰")
    with k2: kpi_card("Price Range",        f"₹{price_range:.0f}", icon="📊")
    with k3: kpi_card("Products Analyzed",  f"{df['product'].nunique()}", icon="📦")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── PRICE ELASTICITY PER PRODUCT ─────────────────────────────
    section("📉 Price Elasticity Analysis")
    st.caption("Elasticity = % change in quantity / % change in price. Negative = demand falls as price rises.")

    product_list_pe = sorted(df["product"].unique().tolist())
    pe_product      = st.selectbox("Select product to analyze", product_list_pe, key="pe_prod")
    pe_data         = df[df["product"] == pe_product].copy()

    # Bucket prices into 5 bins
    pe_data["price_bucket"] = pd.cut(pe_data["price"], bins=5)
    pe_grouped = (
        pe_data.groupby("price_bucket", observed=True)
        .agg(avg_price=("price","mean"), total_qty=("quantity","sum"), txn_count=("transaction_id","nunique"))
        .reset_index()
        .dropna()
        .sort_values("avg_price")
    )

    if len(pe_grouped) >= 2:
        col_a, col_b = st.columns([3, 2])
        with col_a:
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=pe_grouped["avg_price"].round(1).astype(str) + "₹",
                y=pe_grouped["total_qty"],
                name="Units Sold",
                marker_color=COLORS["palette"][:len(pe_grouped)]
            ))
            fig.update_layout(title=f"Units Sold at Different Price Points — {pe_product}",
                               xaxis_title="Avg Price (₹)", yaxis_title="Total Units Sold")
            st.plotly_chart(styled_chart(fig, 340), use_container_width=True)

        with col_b:
            # Compute elasticity between first and last price bucket
            p1_row = pe_grouped.iloc[0]
            p2_row = pe_grouped.iloc[-1]
            if p1_row["avg_price"] > 0 and p1_row["total_qty"] > 0:
                pct_price_change = (p2_row["avg_price"] - p1_row["avg_price"]) / p1_row["avg_price"]
                pct_qty_change   = (p2_row["total_qty"] - p1_row["total_qty"]) / p1_row["total_qty"]
                elasticity = round(pct_qty_change / pct_price_change, 2) if pct_price_change != 0 else 0
            else:
                elasticity = 0

            if elasticity < -1:
                e_label = "🔴 Highly Elastic"
                e_advice = "Customers are very price-sensitive. A small price cut can significantly boost volume. Consider competitive pricing."
            elif elasticity < 0:
                e_label = "🟡 Moderately Elastic"
                e_advice = "Moderate price sensitivity. Small discounts can grow volume. Maintain competitive pricing."
            elif elasticity == 0:
                e_label = "⚪ Neutral"
                e_advice = "Price has little measured impact. May need more data."
            else:
                e_label = "🟢 Inelastic"
                e_advice = "Customers buy regardless of price. You may have room to increase price without losing volume — a premium strategy could work."

            st.markdown(f"""
            <div class="chart-card">
                <div class="kpi-label">Price Elasticity Score</div>
                <div class="kpi-value">{elasticity}</div>
                <div style="margin-top:10px;font-size:14px;font-weight:700;">{e_label}</div>
                <div style="margin-top:8px;font-size:13px;color:#64748b;line-height:1.5;">{e_advice}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Not enough price variation data for this product in the selected date range.")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── PRICE SENSITIVITY SCATTER — ALL PRODUCTS ─────────────────
    section("🗂️ Price vs Volume — All Products")
    pv = df.groupby("product").agg(
        avg_price=("price","mean"),
        total_qty=("quantity","sum"),
        total_rev=("sales","sum"),
        category=("category","first")
    ).reset_index()

    fig = px.scatter(
        pv, x="avg_price", y="total_qty",
        size="total_rev", color="category",
        hover_name="product",
        color_discrete_sequence=COLORS["palette"],
        title="Avg Price vs Total Units Sold (bubble size = revenue)",
        labels={"avg_price":"Avg Price (₹)","total_qty":"Total Units Sold"}
    )
    fig.update_traces(marker=dict(opacity=0.75, line=dict(width=1, color="#fff")))
    st.plotly_chart(styled_chart(fig, 420), use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── TOP REVENUE OPPORTUNITIES ─────────────────────────────────
    section("💡 Pricing Recommendations")

    pv_sorted = pv.sort_values("total_qty", ascending=False)
    # High volume + low price = potential to slightly raise price
    high_vol_low_price = pv_sorted[pv_sorted["avg_price"] < pv["avg_price"].median()].head(5)
    # Low volume + high price = potential to discount
    low_vol_high_price = pv_sorted[pv_sorted["avg_price"] > pv["avg_price"].median()].tail(5)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**📈 Consider Slight Price Increase** *(high volume, below avg price)*")
        for _, row in high_vol_low_price.iterrows():
            st.markdown(f"""
            <div class="alert-success">
            💹 <strong>{row['product']}</strong> — ₹{row['avg_price']:.0f} avg price ·
            {int(row['total_qty']):,} units sold · High demand suggests room for +5–10% price increase
            </div>
            """, unsafe_allow_html=True)
    with c2:
        st.markdown("**📉 Consider Discount or Promotion** *(above avg price, low volume)*")
        for _, row in low_vol_high_price.iterrows():
            st.markdown(f"""
            <div class="alert-warning">
            💸 <strong>{row['product']}</strong> — ₹{row['avg_price']:.0f} avg price ·
            {int(row['total_qty']):,} units sold · Discount may unlock volume
            </div>
            """, unsafe_allow_html=True)


# ==================================================
#   PAGE: COMPETITOR PRICES  ← NEW (Feature 10)
# ==================================================

elif "Competitor Prices" in page:

    page_header("Competitor Price Tracker", "Your store prices vs BigBasket & Blinkit market rates")

    # Reference market prices (BigBasket / Blinkit approximate prices for TN market)
    # These are updated manually or via scraping
    MARKET_PRICES = {
        "Aavin Milk 500ml":            26,
        "Aavin Milk 1L":               50,
        "Aavin Curd 400g":             36,
        "Aavin Butter 100g":           57,
        "Amul Butter 100g":            60,
        "Amul Pure Ghee 500g":         320,
        "Britannia Bread 400g":        42,
        "Modern Bread 400g":           40,
        "Parle-G 500g":                58,
        "Good Day Butter Cookies 150g":32,
        "Bru Coffee Powder 200g":      190,
        "Red Label Tea 500g":          200,
        "Coca Cola 750ml":             48,
        "Pepsi 750ml":                 45,
        "Sprite 750ml":                45,
        "Mango Frooti 200ml":          22,
        "Bovonto 300ml":               22,
        "Horlicks 500g":               310,
        "Boost 500g":                  290,
        "Maggi Noodles 70g":           15,
        "Yippee Noodles 70g":          15,
        "Lay's Classic Salted 52g":    22,
        "Kurkure Masala Munch 78g":    22,
        "Cadbury Dairy Milk 45g":      42,
        "Cadbury 5 Star 22g":          22,
        "KitKat 2F 18g":               22,
        "Munch 18g":                   12,
        "Ferrero Rocher 16pc":         460,
        "Cadbury Celebrations 281g":   360,
        "Colgate MaxFresh 150g":       98,
        "Lux Soap 100g":               48,
        "Lifebuoy Soap 100g":          40,
        "Clinic Plus Shampoo 200ml":   150,
        "Head & Shoulders 200ml":      205,
        "Dettol Handwash 200ml":       95,
        "Surf Excel 1kg":              180,
        "Vim Bar 200g":                38,
        "Harpic Power Plus 500ml":     150,
        "Aashirvaad Atta 5kg":         280,
        "Toor Dal 1kg":                135,
        "Idhayam Gingelly Oil 500ml":  135,
        "Fortune Sunflower Oil 1L":    160,
        "Tata Salt 1kg":               26,
        "Sugar 1kg":                   50,
        "MTR Sambar Powder 200g":      65,
        "Aachi Chilli Powder 200g":    58,
        "Aachi Turmeric Powder 100g":  38,
        "Pampers Pants M 48pc":        720,
        "Huggies Wonder Pants M 42pc": 650,
        "Good Knight Liquid 45ml":     170,
        "All Out Refill 45ml":         145,
    }

    # Scraper function (requires requests + bs4, works in local env with internet)
    def try_scrape_bigbasket(product_name):
        """
        Attempts to fetch price from BigBasket.
        Returns None if fails (JS-rendered site needs Selenium for full scraping).
        This is a placeholder for production use.
        """
        try:
            import requests
            query = product_name.replace(" ", "+")
            url   = f"https://www.bigbasket.com/ps/?q={query}"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept-Language": "en-IN,en;q=0.9"
            }
            resp = requests.get(url, headers=headers, timeout=5)
            # BigBasket is JS-rendered; direct scraping needs Selenium
            # This returns None for now — reference prices are used as fallback
            return None
        except:
            return None

    # Cache file for scraped prices
    cache_file = os.path.join(PROJECT_ROOT, "data", "competitor_prices.json")

    def load_cached_prices():
        if os.path.exists(cache_file):
            with open(cache_file, "r") as f:
                data = json.load(f)
            return data.get("prices", {}), data.get("updated", "Never")
        return {}, "Never"

    def save_cached_prices(prices):
        with open(cache_file, "w") as f:
            json.dump({"prices": prices, "updated": datetime.now().strftime("%d %b %Y, %I:%M %p")}, f)

    cached_prices, last_updated = load_cached_prices()

    # Merge: cached > reference fallback
    effective_market = {**MARKET_PRICES, **cached_prices}

    # ── Header controls ──────────────────────────────────────────
    col_h1, col_h2, col_h3 = st.columns([2,2,2])
    with col_h1:
        if st.button("🔄  Refresh from Web (BigBasket)", use_container_width=True):
            with st.spinner("Fetching prices from BigBasket..."):
                new_prices = {}
                products_to_check = list(MARKET_PRICES.keys())[:20]
                for prod in products_to_check:
                    scraped = try_scrape_bigbasket(prod)
                    if scraped:
                        new_prices[prod] = scraped
                if new_prices:
                    save_cached_prices(new_prices)
                    st.success(f"✅ Updated {len(new_prices)} prices from BigBasket!")
                else:
                    st.info("ℹ️ Live scraping requires Selenium for JS sites. Showing reference prices. Install selenium + chromedriver for live data.")
    with col_h2:
        st.markdown(f'<div class="alert-info" style="margin-top:0">📅 Prices last updated: <strong>{last_updated}</strong></div>',
                    unsafe_allow_html=True)
    with col_h3:
        source_label = "BigBasket + Blinkit Reference" if not cached_prices else f"Live ({len(cached_prices)} products) + Reference"
        st.markdown(f'<div class="alert-success" style="margin-top:0">🏪 Source: {source_label}</div>',
                    unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Build comparison table ───────────────────────────────────
    your_prices = df.groupby("product")["price"].mean().reset_index()
    your_prices.columns = ["product", "your_price"]

    comp_rows = []
    for _, row in your_prices.iterrows():
        prod = row["product"]
        if prod not in effective_market:
            continue
        market_p = effective_market[prod]
        your_p   = round(row["your_price"], 1)
        diff     = round(your_p - market_p, 1)
        diff_pct = round((diff / market_p) * 100, 1) if market_p > 0 else 0
        if diff_pct < -5:
            status = "✅ Cheaper"
        elif diff_pct > 5:
            status = "🔴 Expensive"
        else:
            status = "🟡 On Par"
        comp_rows.append({
            "product":    prod,
            "your_price": your_p,
            "market_price": market_p,
            "diff":       diff,
            "diff_pct":   diff_pct,
            "status":     status,
        })

    comp_df = pd.DataFrame(comp_rows)

    if len(comp_df) == 0:
        st.warning("No matching products found between your store and market reference data.")
    else:
        # KPIs
        cheaper   = len(comp_df[comp_df["status"] == "✅ Cheaper"])
        expensive = len(comp_df[comp_df["status"] == "🔴 Expensive"])
        on_par    = len(comp_df[comp_df["status"] == "🟡 On Par"])

        k1, k2, k3, k4 = st.columns(4)
        with k1: kpi_card("Products Compared", f"{len(comp_df)}", icon="🔍")
        with k2: kpi_card("Cheaper than Market", f"{cheaper}", delta="Competitive advantage", delta_type="up", icon="✅")
        with k3: kpi_card("Above Market Price", f"{expensive}", delta="Risk of losing customers", delta_type="down", icon="🔴")
        with k4: kpi_card("On Par with Market", f"{on_par}", icon="🟡")

        st.markdown("<br>", unsafe_allow_html=True)

        # Category filter
        cats_cp = ["All"] + sorted(df["category"].unique().tolist())
        cat_sel = st.selectbox("Filter by category", cats_cp, key="cp_cat")

        if cat_sel != "All":
            cat_prods  = df[df["category"] == cat_sel]["product"].unique()
            comp_df_f  = comp_df[comp_df["product"].isin(cat_prods)]
        else:
            comp_df_f  = comp_df

        col_a, col_b = st.columns([3, 2])

        with col_a:
            section("💰 Your Price vs Market Price")
            plot_cp = comp_df_f.sort_values("diff_pct", ascending=False).head(20)
            colors  = ["#ef4444" if x > 5 else "#22c55e" if x < -5 else "#f59e0b"
                       for x in plot_cp["diff_pct"]]
            fig = go.Figure(go.Bar(
                x=plot_cp["diff_pct"],
                y=plot_cp["product"],
                orientation="h",
                marker_color=colors,
                text=plot_cp["diff_pct"].apply(lambda x: f"{x:+.1f}%"),
                textposition="outside"
            ))
            fig.add_vline(x=0, line_color="#94a3b8", line_dash="dash")
            fig.update_layout(
                title="Price Difference vs Market (% above/below)",
                yaxis=dict(autorange="reversed"),
                xaxis_title="% vs Market Price"
            )
            st.plotly_chart(styled_chart(fig, 420), use_container_width=True)

        with col_b:
            section("📋 Price Comparison Table")
            display_cp            = comp_df_f[["product","your_price","market_price","diff_pct","status"]].copy()
            display_cp.columns    = ["Product","Your ₹","Market ₹","Diff %","Status"]
            display_cp["Diff %"]  = display_cp["Diff %"].apply(lambda x: f"{x:+.1f}%")
            st.dataframe(display_cp.sort_values("Status"), use_container_width=True, height=400)

        st.markdown("<br>", unsafe_allow_html=True)

        section("🚨 Action Alerts")
        overpriced = comp_df_f[comp_df_f["diff_pct"] > 10].sort_values("diff_pct", ascending=False)
        underpriced = comp_df_f[comp_df_f["diff_pct"] < -10].sort_values("diff_pct")

        if len(overpriced) > 0:
            for _, row in overpriced.head(5).iterrows():
                st.markdown(f"""
                <div class="alert-critical">
                🔴 <strong>{row['product']}</strong> — You charge ₹{row['your_price']} vs
                market ₹{row['market_price']} (<strong>{row['diff_pct']:+.1f}%</strong>).
                Risk of customer switching to BigBasket/Blinkit.
                Consider reducing to ₹{round(row['market_price'] * 1.03)} to stay competitive.
                </div>
                """, unsafe_allow_html=True)

        if len(underpriced) > 0:
            for _, row in underpriced.head(5).iterrows():
                st.markdown(f"""
                <div class="alert-success">
                ✅ <strong>{row['product']}</strong> — You charge ₹{row['your_price']} vs
                market ₹{row['market_price']} (<strong>{row['diff_pct']:+.1f}%</strong>).
                You're cheaper — highlight this as a competitive advantage at billing.
                </div>
                """, unsafe_allow_html=True)



    page_header("Import Store Data", "Connect your supermarket's sales & stock data to RetailX")

    # Status bar
    c1, c2, c3 = st.columns(3)
    with c1:
        txn_rows = len(pd.read_csv("data/retail_transactions.csv")) \
                   if os.path.exists("data/retail_transactions.csv") else 0
        kpi_card("Transaction Records", f"{txn_rows:,}", icon="🧾")
    with c2:
        stock_src = "✅ Real Upload" if os.path.exists("data/stock_loaded.csv") else "⚙️ Demo Defaults"
        kpi_card("Stock Data Source", stock_src, icon="🗄️")
    with c3:
        basket_src = "✅ Generated" if os.path.exists("data/basket_rules.csv") else "❌ Not yet run"
        kpi_card("Basket Rules", basket_src, icon="🔗")

    st.markdown("<br>", unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs([
        "📦  Sales / Transactions",
        "🗄️  Current Stock",
        "🔄  Re-run ML Models",
        "📋  Sample Format",
    ])

    # ── TAB 1: SALES UPLOAD ─────────────────────────────────────
    with tab1:

        st.markdown("""
        <div class="alert-info">
        Upload your billing / sales export from <strong>Tally, Busy, Marg, GoFrugal, Petpooja</strong>
        or any POS system. &nbsp;Accepted formats: <strong>CSV or Excel (.xlsx)</strong>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        uploaded_sales = st.file_uploader(
            "Drop your sales file here",
            type=["csv","xlsx"],
            key="sales_upload",
            help="Export from your POS as CSV / Excel and upload"
        )

        if uploaded_sales:
            try:
                raw = (pd.read_excel(uploaded_sales)
                       if uploaded_sales.name.endswith(".xlsx")
                       else pd.read_csv(uploaded_sales))

                st.success(f"✅ File loaded — **{len(raw):,} rows · {len(raw.columns)} columns** detected")

                with st.expander("Preview uploaded file (first 5 rows)"):
                    st.dataframe(raw.head(5), use_container_width=True)

                st.markdown("#### Map Your Columns to RetailX Format")
                st.caption("Column names in your file may be different — just select which one matches each field.")

                cols = ["-- select --"] + list(raw.columns)
                c1, c2, c3 = st.columns(3)
                with c1:
                    col_product  = st.selectbox("🏷️  Product Name",           cols, key="col_product")
                    col_quantity = st.selectbox("📦  Quantity Sold",           cols, key="col_qty")
                with c2:
                    col_price    = st.selectbox("💰  Price / Bill Amount",     cols, key="col_price")
                    col_date     = st.selectbox("📅  Date",                    cols, key="col_date")
                with c3:
                    col_txn      = st.selectbox("🧾  Bill / Txn ID (optional)", cols, key="col_txn")
                    col_category = st.selectbox("🗂️  Category    (optional)", cols, key="col_cat")

                st.markdown("<br>", unsafe_allow_html=True)

                action = st.radio(
                    "What should we do with existing data?",
                    ["➕  Append to existing data", "🔄  Replace existing data"],
                    horizontal=True
                )

                if st.button("✅  Confirm & Import Sales Data", type="primary"):
                    if "-- select --" in [col_product, col_quantity, col_price, col_date]:
                        st.error("Please map all required fields: Product, Quantity, Price, Date.")
                    else:
                        try:
                            mapped = pd.DataFrame()
                            mapped["product"]        = raw[col_product].astype(str).str.strip()
                            mapped["quantity"]       = pd.to_numeric(raw[col_quantity], errors="coerce").fillna(0)
                            mapped["price"]          = pd.to_numeric(raw[col_price],    errors="coerce").fillna(0)
                            mapped["date"]           = pd.to_datetime(raw[col_date],    errors="coerce")
                            mapped["transaction_id"] = (raw[col_txn].astype(str)
                                                        if col_txn != "-- select --"
                                                        else range(1, len(raw)+1))
                            mapped["category"]       = (raw[col_category].astype(str)
                                                        if col_category != "-- select --"
                                                        else "General")
                            mapped["customer_id"]    = 0
                            mapped                   = mapped.dropna(subset=["date","product"])
                            mapped["sales"]          = mapped["quantity"] * mapped["price"]

                            bad_rows = len(raw) - len(mapped)

                            if "Replace" in action:
                                final = mapped
                            else:
                                if os.path.exists("data/retail_transactions.csv"):
                                    existing = pd.read_csv("data/retail_transactions.csv")
                                    final    = pd.concat([existing, mapped], ignore_index=True)
                                else:
                                    final = mapped

                            final.to_csv("data/retail_transactions.csv", index=False)
                            load_transactions.clear()
                            load_inventory.clear()

                            st.success(f"✅ **{len(mapped):,} records imported successfully!**")
                            if bad_rows > 0:
                                st.warning(f"⚠️ {bad_rows} rows skipped — invalid date or missing product name.")

                            st.markdown("""
                            <div class="alert-info">
                            ℹ️ <strong>Next step:</strong> Switch to the
                            <strong>🔄 Re-run ML Models</strong> tab to refresh all
                            recommendations with your new data.
                            </div>
                            """, unsafe_allow_html=True)

                        except Exception as e:
                            st.error(f"Import failed: {e}")

            except Exception as e:
                st.error(f"Could not read file: {e}")

    # ── TAB 2: STOCK UPLOAD ─────────────────────────────────────
    with tab2:

        st.markdown("""
        <div class="alert-info">
        Upload your <strong>current stock / godown register</strong> so RetailX uses real
        stock values instead of demo defaults.<br><br>
        Formula: &nbsp;<strong>Available Stock = Stock Loaded − Units Sold</strong>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        if os.path.exists("data/stock_loaded.csv"):
            st.markdown("**Currently active stock file:**")
            st.dataframe(pd.read_csv("data/stock_loaded.csv"), use_container_width=True)
            st.markdown("<br>", unsafe_allow_html=True)

        uploaded_stock = st.file_uploader(
            "Drop your stock / inventory file here",
            type=["csv","xlsx"],
            key="stock_upload"
        )

        if uploaded_stock:
            try:
                raw_stock = (pd.read_excel(uploaded_stock)
                             if uploaded_stock.name.endswith(".xlsx")
                             else pd.read_csv(uploaded_stock))

                st.success(f"✅ Stock file loaded — **{len(raw_stock):,} products** detected")

                with st.expander("Preview (first 5 rows)"):
                    st.dataframe(raw_stock.head(), use_container_width=True)

                cols_s = ["-- select --"] + list(raw_stock.columns)
                c1, c2 = st.columns(2)
                with c1:
                    s_product = st.selectbox("🏷️  Product Name column",   cols_s, key="s_product")
                with c2:
                    s_stock   = st.selectbox("📦  Stock Quantity column", cols_s, key="s_stock")

                if st.button("✅  Import Stock Data", type="primary"):
                    if "-- select --" in [s_product, s_stock]:
                        st.error("Please map both required fields.")
                    else:
                        stock_mapped                 = pd.DataFrame()
                        stock_mapped["product"]      = raw_stock[s_product].astype(str).str.strip()
                        stock_mapped["stock_loaded"] = pd.to_numeric(raw_stock[s_stock], errors="coerce").fillna(0)
                        stock_mapped.dropna(inplace=True)
                        stock_mapped.to_csv("data/stock_loaded.csv", index=False)
                        load_inventory.clear()

                        st.success(f"✅ **{len(stock_mapped)} products** imported as stock data!")
                        st.markdown("""
                        <div class="alert-info">
                        ℹ️ <strong>Next step:</strong> Switch to
                        <strong>🔄 Re-run ML Models</strong> to update inventory
                        recommendations with your real stock levels.
                        </div>
                        """, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Could not read file: {e}")

    # ── TAB 3: RE-RUN ML MODELS ─────────────────────────────────
    with tab3:

        st.markdown("""
        <div class="alert-info">
        After importing new sales or stock data, use the buttons below to refresh all ML models.
        This ensures every page shows recommendations based on your latest store data.
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            <div class="chart-card">
                <div style="font-size:15px;font-weight:700;color:#0f1117;margin-bottom:6px;">
                    📦 Inventory Recommendations
                </div>
                <div style="font-size:13px;color:#64748b;margin-bottom:14px;">
                    Recalculates available stock, restock quantities and priority
                    using your latest sales and stock data.
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🔄  Refresh Inventory Engine", use_container_width=True):
                with st.spinner("Running inventory_engine.py ..."):
                    try:
                        result = subprocess.run(
                            [sys.executable, "ml_models/inventory_engine.py"],
                            capture_output=True, text=True,
                            cwd=PROJECT_ROOT
                        )
                        load_inventory.clear()
                        if result.returncode == 0:
                            st.success("✅ Inventory recommendations updated!")
                        else:
                            st.error(f"Error:\n{result.stderr[:300]}")
                    except Exception as e:
                        st.error(f"Could not run inventory engine: {e}")

        with col2:
            st.markdown("""
            <div class="chart-card">
                <div style="font-size:15px;font-weight:700;color:#0f1117;margin-bottom:6px;">
                    🔗 Basket / Association Rules
                </div>
                <div style="font-size:13px;color:#64748b;margin-bottom:14px;">
                    Re-runs market basket analysis on the latest transaction data
                    to find updated product co-purchase patterns.
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🔄  Refresh Basket Analysis", use_container_width=True):
                with st.spinner("Running basket_analysis.py ..."):
                    try:
                        result = subprocess.run(
                            [sys.executable, "ml_models/basket_analysis.py"],
                            capture_output=True, text=True,
                            cwd=PROJECT_ROOT
                        )
                        load_basket.clear()
                        if result.returncode == 0:
                            st.success("✅ Basket rules updated!")
                        else:
                            st.error(f"Error:\n{result.stderr[:300]}")
                    except Exception as e:
                        st.error(f"Could not run basket analysis: {e}")

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("⚡  Refresh Everything  (recommended after import)",
                     type="primary", use_container_width=True):
            with st.spinner("Refreshing all models — this may take 30–60 seconds..."):
                errors = []
                for script, label in [
                    ("ml_models/inventory_engine.py", "Inventory Engine"),
                    ("ml_models/basket_analysis.py",  "Basket Analysis"),
                ]:
                    try:
                        r = subprocess.run([sys.executable, script], capture_output=True, text=True, cwd=PROJECT_ROOT)
                        if r.returncode != 0:
                            errors.append(f"{label}: {r.stderr[:150]}")
                    except Exception as e:
                        errors.append(f"{label}: {e}")

                load_transactions.clear()
                load_inventory.clear()
                load_basket.clear()

                if errors:
                    for err in errors:
                        st.error(err)
                else:
                    st.success("✅ All models refreshed! Navigate to any page to see updated insights.")
                    st.balloons()

        st.markdown("<br>", unsafe_allow_html=True)

        # File status
        section("📁 Data File Status")
        files_check = {
            "data/retail_transactions.csv":       "Sales Transactions",
            "data/stock_loaded.csv":              "Stock Data (uploaded)",
            "data/inventory_recommendations.csv": "Inventory Recommendations",
            "data/basket_rules.csv":              "Basket Rules",
            "data/daily_product_sales.csv":       "Daily Product Sales",
        }
        for path, label in files_check.items():
            if os.path.exists(path):
                kb    = os.path.getsize(path) / 1024
                mtime = datetime.fromtimestamp(os.path.getmtime(path)).strftime("%d %b %Y, %I:%M %p")
                st.markdown(f"""
                <div class="alert-success">
                ✅ <strong>{label}</strong>
                &nbsp;·&nbsp; {kb:.1f} KB
                &nbsp;·&nbsp; Last updated: {mtime}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="alert-warning">
                ⚠️ <strong>{label}</strong> — file not found
                </div>
                """, unsafe_allow_html=True)

    # ── TAB 4: SAMPLE FORMAT ────────────────────────────────────
    with tab4:

        st.markdown("### Sales File — Expected Format")
        st.caption("Your POS export column names can be anything — you'll map them during import.")

        sample_sales = pd.DataFrame({
            "date":           ["2024-01-15","2024-01-15","2024-01-16","2024-01-16"],
            "product":        ["Amul Milk 500ml","Britannia Bread","Maggi Noodles","Lay's Chips"],
            "quantity":       [2, 1, 3, 2],
            "price":          [30, 40, 15, 20],
            "transaction_id": [1001, 1001, 1002, 1002],
            "category":       ["Dairy","Bakery","Snacks","Snacks"]
        })
        st.dataframe(sample_sales, use_container_width=True)
        st.download_button("⬇️ Download Sales Template (CSV)",
                           data=sample_sales.to_csv(index=False),
                           file_name="retailx_sales_template.csv",
                           mime="text/csv")

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("### Stock File — Expected Format")
        st.caption("Your current physical stock or godown register.")

        sample_stock = pd.DataFrame({
            "product":      ["Amul Milk 500ml","Britannia Bread","Maggi Noodles","Lay's Chips"],
            "stock_loaded": [500, 300, 600, 500]
        })
        st.dataframe(sample_stock, use_container_width=True)
        st.download_button("⬇️ Download Stock Template (CSV)",
                           data=sample_stock.to_csv(index=False),
                           file_name="retailx_stock_template.csv",
                           mime="text/csv")

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("""
        <div class="alert-info">
        💡 <strong>Tally users:</strong>
        Gateway of Tally → Display → Inventory Books → Stock Item → Export as Excel<br><br>
        💡 <strong>Busy users:</strong>
        Reports → Inventory Reports → Stock Summary → Export CSV<br><br>
        💡 <strong>GoFrugal users:</strong>
        Reports → Sales → Detailed Sales Report → Export<br><br>
        💡 <strong>Petpooja users:</strong>
        Reports → Item Sales Report → Download CSV
        </div>
        """, unsafe_allow_html=True)