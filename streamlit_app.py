import streamlit as st
import pandas as pd
import plotly.express as px

# Load data
df = pd.read_excel("dashboard_data.xlsx", sheet_name="Final_zbill")

st.set_page_config(page_title="Project Financial Dashboard", layout="wide")
st.title("📊 Project Financial Dashboard")

# Convert currency columns to numeric
def clean_currency(col):
    return pd.to_numeric(col.replace("[₹, ]", "", regex=True), errors='coerce')

df["Total PO Amt"] = clean_currency(df["Total PO Amt"])
df["Billed Till Date"] = clean_currency(df["Billed Till Date"])

# Sidebar filters
st.sidebar.header("🔍 Filters")
selected_project = st.sidebar.multiselect("Select Project", options=df["Project"].unique(), default=df["Project"].unique())
selected_region = st.sidebar.multiselect("Select Region", options=df["Region"].unique(), default=df["Region"].unique())

# Filter DataFrame
filtered_df = df[(df["Project"].isin(selected_project)) & (df["Region"].isin(selected_region))]

# Summary Metrics
total_po = filtered_df["Total PO Amt"].sum()
total_billed = filtered_df["Billed Till Date"].sum()
billed_pct = (total_billed / total_po) * 100 if total_po else 0

col1, col2, col3 = st.columns(3)
col1.metric("🧾 Total PO Amount", f"₹ {total_po:,.0f}")
col2.metric("📦 Billed Till Date", f"₹ {total_billed:,.0f}")
col3.metric("✅ % Billed", f"{billed_pct:.1f}%")

st.markdown("---")

# Bar Chart - PO vs Billed
bar_fig = px.bar(
    filtered_df,
    x="Project",
    y=["Total PO Amt", "Billed Till Date"],
    barmode="group",
    title="PO Amount vs Billed Till Date",
    color_discrete_map={"Total PO Amt": "green", "Billed Till Date": "blue"}
)
st.plotly_chart(bar_fig, use_container_width=True)

# Pie Chart - Billing by Region
region_df = filtered_df.groupby("Region")["Billed Till Date"].sum().reset_index()
pie_fig = px.pie(region_df, names="Region", values="Billed Till Date", title="Billed Amount by Region")
st.plotly_chart(pie_fig, use_container_width=True)

# Optional: Show filtered table
with st.expander("🔎 View Filtered Data"):
    st.dataframe(filtered_df)

