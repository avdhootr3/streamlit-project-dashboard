import streamlit as st
import pandas as pd

# --- Data Loading (with debugging) ---
@st.cache_data
def load_data():
    df = pd.read_excel("weekly_updates.xlsx", sheet_name="Billing_Summary")
    # Print columns for debug (remove in production)
    print(f"Columns after load: {df.columns.tolist()}")
    return df

df = load_data()

# --- Display a few rows (debug) ---
st.header("First 5 rows (for verification)")
st.write(df.head())

# --- Simple Metric (confirm column works) ---
st.header("Basic Metrics")
st.metric("Total PO Amount (₹ Cr)", f"{df['Total PO Amt'].sum() / 100:,.2f}")

# --- Project List Table ---
st.header("Project Portfolio")
st.dataframe(df, height=800, use_container_width=True)
