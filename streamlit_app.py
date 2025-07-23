import streamlit as st
import pandas as pd

# Load data (adapt path as needed; for Streamlit Cloud, place file in root)
@st.cache_data
def load_data():
    df = pd.read_excel("weekly_updates.xlsx", sheet_name="Billing_Summary")
    df.columns = df.columns.str.strip()  # Clean column names (best practice)
    return df

df = load_data()

# Title and overview
st.set_page_config(layout="wide")
st.title("Project & Billing Dashboard")
st.header("Data Loaded Successfully")
st.write(f"Total projects: {len(df)}")
st.write("All projects loaded with correct columns.")

# Show column names (debug)
with st.expander("Show Column Names (for validation)"):
    st.write(df.columns.tolist())

# Top 5 rows (preview)
st.header("Project Preview")
st.write(df.head())

# Key metrics
st.header("Key Metrics")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total PO Amount (₹ Cr)", f"{df['Total PO Amt'].sum() / 100:,.2f}")
col2.metric("Open AR (₹ Cr)", f"{df['Open AR'].sum() / 100:,.2f}")
col3.metric("Open Billing (₹ Cr)", f"{df['Open Billing'].sum() / 100:,.2f}")
col4.metric("Current Month Billing (₹ Cr)", f"{df['Current Month Billing'].sum() / 100:,.2f}")

# Filtered view
region_filter = st.multiselect("Filter by Region", df["Region"].unique(), default=df["Region"].unique())
type_filter = st.multiselect("Filter by Type", df["Type"].unique(), default=df["Type"].unique())

filtered = df[
    (df["Region"].isin(region_filter)) &
    (df["Type"].isin(type_filter))
]

if filtered.empty:
    st.warning("No projects match your filters. Showing all projects.")
    filtered = df.copy()

# Display table
st.header("Filtered Project List")
st.dataframe(filtered, height=800, use_container_width=True)

# Optional: Drill down by project
selected_project = st.selectbox("Select a Project for Details", filtered["Project"].unique())
proj = filtered[filtered["Project"] == selected_project].iloc[0]

with st.expander(f"Details for {selected_project}"):
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
top_ar = filtered.nlargest(5, "Open AR")[["Project", "Region", "Total PO Amt", "Open AR", "Challenges / Risks"]]
st.header("Top 5 Projects by Open AR")
st.dataframe(top_ar)
