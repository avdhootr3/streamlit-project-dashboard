import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
import pyarrow as pa
import pyarrow.parquet as pq
from datetime import datetime

# Load Data
@st.cache_data
def load_data():
    weekly_updates = pd.read_excel("weekly_updates.xlsx", sheet_name="Billing_Summary")
    billing_ytd = pd.read_excel("dashboard_data.xlsx", sheet_name="Billing_YTD")
    current_month = pd.read_excel("dashboard_data.xlsx", sheet_name="CurrentMonthBilling")
    open_billing = pd.read_excel("dashboard_data.xlsx", sheet_name="oPEN bILLING")
    return weekly_updates, billing_ytd, current_month, open_billing

weekly_updates, billing_ytd, current_month, open_billing = load_data()

def style_negative(value, threshold=0):
    return f"color: {'red' if value < threshold else 'gray'}" if value < threshold else None

def make_downloadable(df, file_format="csv"):
    if file_format == "csv":
        return df.to_csv(index=False).encode("utf-8")
    elif file_format == "xlsx":
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False)
        return output.getvalue()

def risk_score(row):
    # Customize this logic for your org's risk scoring
    score = 0
    if pd.notna(row["Challenges / Risks"]) and row["Challenges / Risks"] != "0":
        score += 1
    if row["Open AR"] > 0.1 * row["Total PO Amt"]:
        score += 1
    if row["Open Billing"] > 0.1 * row["Total PO Amt"]:
        score += 1
    return score


st.set_page_config(layout="wide")
st.title("CMS Project & Billing Management Dashboard")

# Date Range
min_date = current_month["Invoice Date"].min().date()
max_date = current_month["Invoice Date"].max().date()
start_date, end_date = st.date_input("Date Range", [min_date, max_date], min_value=min_date, max_value=max_date)

# Filters
region_filter = st.multiselect("Filter by Region", options=weekly_updates["Region"].unique(), default=weekly_updates["Region"].unique())
type_filter = st.multiselect("Filter by Project Type", options=weekly_updates["Type"].unique(), default=weekly_updates["Type"].unique())
n_top = st.slider("Show Top N Projects by Open AR", min_value=1, max_value=20, value=5)

# Data Filtering
weekly_filtered = weekly_updates[
    (weekly_updates["Region"].isin(region_filter)) & 
    (weekly_updates["Type"].isin(type_filter))
].copy()
weekly_filtered["Risk Score"] = weekly_filtered.apply(risk_score, axis=1)
top_open_ar = weekly_filtered.nlargest(n_top, "Open AR").reset_index(drop=True)

# Apply date filter to transactional data
current_month_filtered = current_month[
    (current_month["Invoice Date"] >= pd.to_datetime(start_date)) &
    (current_month["Invoice Date"] <= pd.to_datetime(end_date))
]
billing_ytd_filtered = billing_ytd # (add date filter if required, otherwise use as-is)
open_billing_filtered = open_billing # (no date filter for open billing)

# Summary Tiles
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Projects", len(weekly_filtered))
col2.metric("Total PO Amount (Cr)", weekly_filtered["Total PO Amt"].sum() / 100)
col3.metric("Open AR (Cr)", weekly_filtered["Open AR"].sum() / 100, delta_color="inverse")
col4.metric("Open Billing (Cr)", weekly_filtered["Open Billing"].sum() / 100, delta_color="inverse")

# Download
if st.button("Export Project Summary (Excel)"):
    st.download_button("Download", make_downloadable(weekly_filtered, "xlsx"), "Project_Status.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# Project Portfolio
st.subheader("Project Portfolio Summary")
st.dataframe(
    weekly_filtered[["Project", "Region", "Type", "Total PO Amt", "Billed Till Date", "Open AR", "Open Billing", "Current Month Billing", "Overall Progress", "Risk Score"]]
    .style.applymap(style_negative, subset=["Open AR", "Open Billing"]),
    height=300, use_container_width=True
)

# Project Drill-down
selected_project = st.selectbox("Select Project for Details", options=weekly_filtered["Project"].unique())
proj = weekly_filtered[weekly_filtered["Project"] == selected_project].squeeze()
with st.expander(f"Project Details: {selected_project}"):
    cols = st.columns(2)
    with cols[0]:
        st.metric("PO Amount (Cr)", round(proj["Total PO Amt"] / 100, 2))
        st.metric("Billed Till Date (Cr)", round(proj["Billed Till Date"] / 100, 2))
        st.metric("Open AR (Cr)", round(proj["Open AR"] / 100, 2))
        st.metric("Open Billing (Cr)", round(proj["Open Billing"] / 100, 2))
        st.metric("% Billed", round(100 * proj["Billed"] if pd.notna(proj["Billed"]) else 0, 1))
    with cols[1]:
        st.metric("Project Duration", proj["Project Duration"])
        st.markdown(f"**Milestone:** {proj['Billing Milestone']}")
        st.markdown(f"**Resources:** {proj['Resource Deployed']}")
        st.markdown(f"**Scope:** {proj['Scope'][:200]}..." if pd.notna(proj['Scope']) else "")
        st.markdown(f"**Technology:** {proj['Technology / Tools'][:200]}..." if pd.notna(proj['Technology / Tools']) else "")
    st.markdown(f"**Progress:** {proj['Overall Progress']}")
    st.markdown(f"**Plan:** {proj['Weekly Plan']}")
    st.markdown(f"**Risks:** {proj['Challenges / Risks'] if pd.notna(proj['Challenges / Risks']) and proj['Challenges / Risks'] != '0' else 'No critical risks reported.'}")

# Financial Trend Chart
st.subheader("Monthly Billing Trend")
monthly_trend = current_month_filtered.groupby(pd.to_datetime(current_month_filtered["Invoice Date"]).dt.to_period("M"))["Net value of the billing item"].sum().reset_index()
fig = px.line(monthly_trend, x="Invoice Date", y="Net value of the billing item", title="Total Billing by Month")
st.plotly_chart(fig, use_container_width=True)

# Region-wise Billing
st.subheader("Region-wise Billing (YTD)")
region_billing = billing_ytd_filtered.groupby("State")["Net value of the billing item"].sum().reset_index()
fig2 = px.bar(region_billing, x="State", y="Net value of the billing item", title="Billing by State (YTD)")
st.plotly_chart(fig2, use_container_width=True)

# Open Billing by Customer
if st.checkbox("Show Open Billing Details (Customer-wise)"):
    st.dataframe(open_billing_filtered[["Customer Name", "Material Description", "Open Amt", "City", "State"]], height=300, use_container_width=True)
    if st.button("Export Open Billing (Excel)"):
        st.download_button("Download", make_downloadable(open_billing_filtered, "xlsx"), "Open_Billing.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# Top N Projects by Open AR
st.subheader(f"Top {n_top} Projects by Open AR")
st.dataframe(top_open_ar[["Project", "Region", "Total PO Amt", "Open AR", "Challenges / Risks"]], height=200, use_container_width=True)
