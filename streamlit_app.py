import streamlit as st
import pandas as pd

st.set_page_config(page_title="Project Dashboard", layout="wide")

st.title("📊 Project Financial & Weekly Dashboard")

# Load data
file_path = "dashboard_data.xlsx"

@st.cache_data
def load_data(sheet_name):
    return pd.read_excel(file_path, sheet_name=sheet_name)

# Sidebar sheet selector
sheet = st.sidebar.selectbox("Select Data Sheet", ["Final_zbill", "oPEN bILLING", "CurrentMonthBilling", "Billing_YTD"])
df = load_data(sheet)

st.markdown(f"### Preview: {sheet}")
st.dataframe(df, use_container_width=True)
