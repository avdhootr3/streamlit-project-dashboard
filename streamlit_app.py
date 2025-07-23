import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide", page_title="Project Dashboard")

# Load Excel file
file_path = "dashboard_data.xlsx"

# Read the required sheets
df_main = pd.read_excel(file_path, sheet_name="Final_zbill")
df_open = pd.read_excel(file_path, sheet_name="oPEN bILLING")
df_month = pd.read_excel(file_path, sheet_name="CurrentMonthBilling")
df_ytd = pd.read_excel(file_path, sheet_name="Billing_YTD")

# Rename "SO No" to "SO Number" in all sheets
for df in [df_main, df_open, df_month, df_ytd]:
    if "SO No" in df.columns:
        df.rename(columns={"SO No": "SO Number"}, inplace=True)
    if "SO Number" in df.columns:
        df["SO Number"] = df["SO Number"].astype(str)

# Merge all dataframes on SO Number
df_merged = df_main.copy()
df_merged = df_merged.merge(df_open, on="SO Number", how="left", suffixes=("", "_open"))
df_merged = df_merged.merge(df_month, on="SO Number", how="left", suffixes=("", "_month"))
df_merged = df_merged.merge(df_ytd, on="SO Number", how="left", suffixes=("", "_ytd"))

# Standardize customer name column
if "Customer name" in df_merged.columns:
    df_merged["Customer name"] = df_merged["Customer name"].fillna("Unknown")
else:
    st.error("❌ Column 'Customer name' not found in merged data.")
    st.stop()

# Sidebar filters
customers = df_merged["Customer name"].dropna().unique().tolist()
selected_customers = st.sidebar.multiselect("Select Customer(s)", options=customers, default=customers)

df_filtered = df_merged[df_merged["Customer name"].isin(selected_customers)]

st.title("📊 Project Billing Dashboard")
st.markdown("Filtered view based on selected customers.")

# KPI Summary
col1, col2, col3 = st.columns(3)
col1.metric("Total PO Amt", f"₹ {df_filtered['Total PO Amt'].sum():,.2f}")
col2.metric("Total Billed", f"₹ {df_filtered['Billed Till Date'].sum():,.2f}")
col3.metric("Open Billing", f"₹ {df_filtered['Open Billing'].sum():,.2f}")


# Bar Chart - Customer-wise Billing
fig1 = px.bar(df_filtered, x="Customer name", y="Billed Till Date", title="Customer-wise Billed Amount")
st.plotly_chart(fig1, use_container_width=True)

# Pie Chart - PO Amt Distribution
fig2 = px.pie(df_filtered, names="Customer name", values="PO AMT", title="PO Amt Share by Customer")
st.plotly_chart(fig2, use_container_width=True)

# Show Raw Data
with st.expander("📂 Show Merged Data"):
    st.dataframe(df_filtered)
