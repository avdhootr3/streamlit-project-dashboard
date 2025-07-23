import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
from datetime import datetime

# --- Data Loading ---
@st.cache_data
def load_data():
    weekly_updates = pd.read_excel("weekly_updates.xlsx", sheet_name="Billing_Summary")
    billing_all = pd.read_excel("dashboard_data.xlsx", sheet_name="Final_zbill")
    billing_ytd = pd.read_excel("dashboard_data.xlsx", sheet_name="Billing_YTD")
    current_month = pd.read_excel("dashboard_data.xlsx", sheet_name="CurrentMonthBilling")
    open_billing = pd.read_excel("dashboard_data.xlsx", sheet_name="oPEN bILLING")
    return weekly_updates, billing_all, billing_ytd, current_month, open_billing

weekly_updates, billing_all, billing_ytd, current_month, open_billing = load_data()

# --- Sanity Check ---
print("Weekly Updates Columns:", weekly_updates.columns)   # Debug: Always print columns after load
print("Billing All Columns:", billing_all.columns)


def style_negative(v, threshold=0):
    return f"color: {'red' if v < threshold else 'green'}" if v < threshold else None

def make_downloadable(df, file_format="csv"):
    if file_format == "csv":
        return df.to_csv(index=False).encode("utf-8")
    elif file_format == "xlsx":
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False)
        return output.getvalue()

def risk_score(row):
    score = 0
    if pd.notna(row["Challenges / Risks"]) and row["Challenges / Risks"] != "0":
        score += 1
    if (row["Open AR"] > 0.1 * row["Total PO Amt"]) or (row["Open Billing"] > 0.1 * row["Total PO Amt"]):
        score += 1
    return score


st.set_page_config(layout="wide")
st.title("Project & Billing Management Dashboard")

# --- Filters ---
region_filter = st.multiselect("Region", weekly_updates["Region"].unique(), default=weekly_updates["Region"].unique())
type_filter = st.multiselect("Project Type", weekly_updates["Type"].unique(), default=weekly_updates["Type"].unique())
n_top = st.slider("Top N Projects by Open AR", 1, 20, 5)

weekly_filtered = weekly_updates[
    (weekly_updates["Region"].isin(region_filter)) & 
    (weekly_updates["Type"].isin(type_filter))
].copy()

if weekly_filtered.empty:
    st.warning("No projects match your filters. Showing all projects.")
    weekly_filtered = weekly_updates.copy()

weekly_filtered["Risk Score"] = weekly_filtered.apply(risk_score, axis=1)
top_open_ar = weekly_filtered.nlargest(n_top, "Open AR")

# --- Metrics ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Projects", len(weekly_filtered))
col2.metric("Total PO Amount (₹ Cr)", round(weekly_filtered["Total PO Amt"].sum() / 100, 2))
col3.metric("Open AR (₹ Cr)", round(weekly_filtered["Open AR"].sum() / 100, 2))
col4.metric("Open Billing (₹ Cr)", round(weekly_filtered["Open Billing"].sum() / 100, 2))

# --- Project Portfolio ---
st.header("Project Portfolio Summary")
st.dataframe(
    weekly_filtered[[
        "Project", "Region", "Type", "Total PO Amt", "Billed Till Date", 
        "Open AR", "Open Billing", "Current Month Billing", 
        "Overall Progress", "Risk Score", "Challenges / Risks"
    ]],
    height=300, use_container_width=True
)

# --- Export ---
if st.button("Export Project Summary (Excel)"):
    st.download_button(
        "Download",
        make_downloadable(weekly_filtered, "xlsx"),
        "Project_Summary.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# --- Project Drill-down ---
selected_project = st.selectbox("Select Project", weekly_filtered["Project"].unique())
proj = weekly_filtered[weekly_filtered["Project"] == selected_project].squeeze()

with st.expander(f"Project Details: {selected_project}"):
    cols = st.columns(2)
    with cols[0]:
        st.metric("PO Amount (₹ Cr)", round(proj["Total PO Amt"] / 100, 2))
        st.metric("Billed Till Date (₹ Cr)", round(proj["Billed Till Date"] / 100, 2))
        st.metric("Open AR (₹ Cr)", round(proj["Open AR"] / 100, 2))
        st.metric("Open Billing (₹ Cr)", round(proj["Open Billing"] / 100, 2))
    with cols[1]:
        st.metric("Project Duration", proj["Project Duration"])
        st.write(f"**Milestone:** {proj['Billing Milestone']}")
        st.write(f"**Resources:** {proj['Resource Deployed']}")
    st.write(f"**Progress:** {proj['Overall Progress']}")
    st.write(f"**Plan:** {proj['Weekly Plan']}")
    st.write(f"**Risks:** {proj['Challenges / Risks']}" if pd.notna(proj['Challenges / Risks']) and proj['Challenges / Risks'] != "0" else "No critical risks reported.")

# --- Billing Trends ---
st.header("Monthly Billing Trend")
current_month["Invoice Date"] = pd.to_datetime(current_month["Invoice Date"])
monthly_trend = current_month.groupby(pd.to_datetime(current_month["Invoice Date"]).dt.to_period("M"))["Net value of the billing item"].sum().reset_index()
fig = px.line(monthly_trend, x="Invoice Date", y="Net value of the billing item", title="Total Billing by Month")
st.plotly_chart(fig, use_container_width=True)

# --- Region-wise Billing ---
st.header("Region-wise Billing (YTD)")
region_billing = billing_ytd.groupby("State")["Net value of the billing item"].sum().reset_index()
fig2 = px.bar(region_billing, x="State", y="Net value of the billing item", title="Billing by State (YTD)")
st.plotly_chart(fig2, use_container_width=True)

# --- Open Billing Details ---
if st.checkbox("Show Open Billing Details"):
    st.dataframe(open_billing[["Customer Name", "Material Description", "Open Amt", "City", "State"]], height=300, use_container_width=True)
    if st.button("Export Open Billing (Excel)"):
        st.download_button(
            "Download",
            make_downloadable(open_billing, "xlsx"),
            "Open_Billing.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# --- Top Projects by Open AR ---
st.header(f"Top {n_top} Projects by Open AR")
st.dataframe(top_open_ar[["Project", "Region", "Total PO Amt", "Open AR", "Challenges / Risks"]], height=200, use_container_width=True)
