import streamlit as st
import pandas as pd
import plotly.express as px

# Set page layout
st.set_page_config(page_title="Project Financial Dashboard", layout="wide")
st.title("📊 Project Financial Dashboard (Billing, Open AR, YTD)")

# Load data from Excel file
file_path = "dashboard_data.xlsx"

@st.cache_data
def load_data():
    df_main = pd.read_excel(file_path, sheet_name="Final_zbill")
    df_open = pd.read_excel(file_path, sheet_name="oPEN bILLING")
    df_month = pd.read_excel(file_path, sheet_name="CurrentMonthBilling")
    df_ytd = pd.read_excel(file_path, sheet_name="Billing_YTD")

    return df_main, df_open, df_month, df_ytd

df_main, df_open, df_month, df_ytd = load_data()

# Ensure common key is consistent
for df in [df_main, df_open, df_month, df_ytd]:
    df["SO Number"] = df["SO Number"].astype(str)

# Merge datasets on "SO Number"
df_merged = df_main.merge(df_open, on="SO Number", how="left", suffixes=("", "_open"))
df_merged = df_merged.merge(df_month, on="SO Number", how="left", suffixes=("", "_month"))
df_merged = df_merged.merge(df_ytd, on="SO Number", how="left", suffixes=("", "_ytd"))

# Clean currency columns (₹ symbol, commas, etc.)
def clean_currency(col):
    return pd.to_numeric(col.replace("[₹, ]", "", regex=True), errors="coerce")

currency_columns = ["Total PO Amt", "Billed Till Date", "Open Billing", "Billing YTD FY 25-26"]
for col in currency_columns:
    if col in df_merged.columns:
        df_merged[col] = clean_currency(df_merged[col].astype(str))

# Sidebar filters
st.sidebar.header("🔍 Filters")
customers = df_merged["Customer"].dropna().unique().tolist()
regions = df_merged["Region"].dropna().unique().tolist()

selected_customers = st.sidebar.multiselect("Customer", options=customers, default=customers)
selected_regions = st.sidebar.multiselect("Region", options=regions, default=regions)

df_filtered = df_merged[df_merged["Customer"].isin(selected_customers) & df_merged["Region"].isin(selected_regions)]

# Summary Metrics
total_po = df_filtered["Total PO Amt"].sum()
total_billed = df_filtered["Billed Till Date"].sum()
open_billing = df_filtered["Open Billing"].sum()
billing_ytd = df_filtered["Billing YTD FY 25-26"].sum()

col1, col2, col3, col4 = st.columns(4)
col1.metric("🧾 Total PO Amt", f"₹ {total_po:,.0f}")
col2.metric("✅ Billed Till Date", f"₹ {total_billed:,.0f}")
col3.metric("💼 Open Billing", f"₹ {open_billing:,.0f}")
col4.metric("📅 Billing YTD (FY25-26)", f"₹ {billing_ytd:,.0f}")

st.markdown("---")

# PO vs Billed Bar Chart (by Customer)
fig_po = px.bar(
    df_filtered,
    x="Customer",
    y=["Total PO Amt", "Billed Till Date"],
    barmode="group",
    title="Total PO vs Billed Till Date (by Customer)",
    color_discrete_map={"Total PO Amt": "#2ca02c", "Billed Till Date": "#1f77b4"}
)
st.plotly_chart(fig_po, use_container_width=True)

# Open Billing Pie Chart
df_pie = df_filtered.groupby("Customer")["Open Billing"].sum().reset_index()
df_pie = df_pie[df_pie["Open Billing"] > 0]
if not df_pie.empty:
    pie_fig = px.pie(df_pie, names="Customer", values="Open Billing", title="Open Billing Distribution")
    st.plotly_chart(pie_fig, use_container_width=True)
else:
    st.info("✅ No open billing data to show.")

# YTD Billing Bar Chart
if "Billing YTD FY 25-26" in df_filtered.columns:
    ytd_fig = px.bar(
        df_filtered,
        x="Customer",
        y="Billing YTD FY 25-26",
        title="YTD Billing (FY 2025-26) by Customer",
        color="Customer"
    )
    st.plotly_chart(ytd_fig, use_container_width=True)

# Show filtered table
with st.expander("🔎 View Filtered Data"):
    st.dataframe(df_filtered)

