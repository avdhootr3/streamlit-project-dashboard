import streamlit as st
import pandas as pd

# Page setup
st.set_page_config(page_title="Project & Billing Dashboard", layout="wide")

# Load data
@st.cache_data
def load_data():
    df = pd.read_excel("weekly_updates.xlsx", sheet_name="Billing_Summary")
    df.columns = df.columns.str.strip().str.replace('\n', '', regex=True).str.replace('\r', '', regex=True)
    return df

df = load_data()

# Title and overview
st.title("📊 Project & Billing Dashboard")
st.success("Data Loaded Successfully")
st.write(f"**Total Projects:** {len(df)}")

# Debug: Show column names
with st.expander("🔍 Show Column Names (for validation)"):
    st.write(df.columns.tolist())

# Preview
st.header("📁 Project Preview")
st.dataframe(df.head(), use_container_width=True)

# Key Metrics
st.header("📌 Key Metrics")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total PO Amount (₹ Cr)", f"{df['Total PO Amt'].sum() / 100:,.2f}")
col2.metric("Open AR (₹ Cr)", f"{df['Open AR'].sum() / 100:,.2f}")
col3.metric("Open Billing (₹ Cr)", f"{df['Open Billing'].sum() / 100:,.2f}")
col4.metric("Current Month Billing (₹ Cr)", f"{df['Current Month Billing'].sum() / 100:,.2f}")

# Filters
st.header("🔍 Filter Projects")
region_filter = st.multiselect("Filter by Region", df["Region"].dropna().unique(), default=df["Region"].dropna().unique())
type_filter = st.multiselect("Filter by Type", df["Type"].dropna().unique(), default=df["Type"].dropna().unique())

filtered = df[(df["Region"].isin(region_filter)) & (df["Type"].isin(type_filter))]

if filtered.empty:
    st.warning("No projects match your filters. Showing all projects.")
    filtered = df.copy()

# Filtered Table
st.header("📋 Filtered Project List")
st.dataframe(filtered, height=800, use_container_width=True)

# Project Drilldown
st.header("🔎 Project Details")
selected_project = st.selectbox("Select a Project for Details", filtered["Project"].dropna().unique())
proj = filtered[filtered["Project"] == selected_project].iloc[0]

with st.expander(f"📌 Details for {selected_project}"):
    cols = st.columns(2)
    with cols[0]:
        st.metric("PO Amount (₹ Cr)", f"{proj['Total PO Amt'] / 100:,.2f}")
        st.metric("Billed Till Date (₹ Cr)", f"{proj['Billed Till Date'] / 100:,.2f}")
        st.metric("Open AR (₹ Cr)", f"{proj['Open AR'] / 100:,.2f}")
        st.metric("Open Billing (₹ Cr)", f"{proj['Open Billing'] / 100:,.2f}")
    with cols[1]:
        st.write(f"**Region:** {proj['Region']}")
        st.write(f"**Type:** {proj['Type']}")
        st.write(f"**Billing Milestone:** {proj['Billing Milestone']}")
        st.write(f"**Project Duration:** {proj['Project Duration']}")
        st.write(f"**Resources:** {proj['Resource Deployed']}")
    st.write(f"**Progress:** {proj['Overall Progress']}")
    st.write(f"**Plan:** {proj['Weekly Plan']}")
    st.write(f"**Risks:** {proj['Challenges / Risks']}")

# Top 5 by Open AR
st.header("🚨 Top 5 Projects by Open AR")
top_ar = filtered.nlargest(5, "Open AR")[["Project", "Region", "Total PO Amt", "Open AR", "Challenges / Risks"]]
st.dataframe(top_ar, use_container_width=True)
