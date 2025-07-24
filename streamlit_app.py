import streamlit as st
import pandas as pd

# Load Excel data
df = pd.read_excel("weekly_updates.xlsx")


# Project filter
project_names = df["Project"].unique()
selected_project = st.selectbox("Select a Project", project_names)

# Filter selected project data
project_data = df[df["Project"] == selected_project].iloc[0]

# Header Section
st.markdown(f"""
## Project : {project_data['Project']}

**PO Amt (in Lakhs)**: {project_data[' Total PO Amt ']}  
**Billing Done (in Lakhs)**: {project_data['Type']}  
**Open Billing (in Lakhs)**: {project_data['Open Billing']}  
**Billing Milestone**: {project_data['Billing Milestone']}

**Start Date (PO)**: {project_data['Project Dates'].split("::")[0].strip()}  
**End Date (PO)**: {project_data['Project Dates'].split("::")[1].strip()}  
**Duration**: {project_data['Project Duration']}  
**Resources Deployed**: {project_data['Resource Deployed']}  
**Milestone Billing Amount**: {project_data['Milestone billing amount']}
""")

# Two-column layout for details
col1, col2 = st.columns(2)

with col1:
    st.subheader("Scope")
    st.text_area(" ", value=project_data['Scope'], height=300)

    st.subheader("Challenges / Risk")
    st.text_area(" ", value=project_data['Challenges / Risks'], height=200)

with col2:
    st.subheader("Overall Progress")
    st.text_area(" ", value=project_data['Overall Progress'], height=300)

    st.subheader("Weekly Plan")
    st.text_area(" ", value=project_data['Weekly Plan'], height=200)

# Optional: Bar Graph for comparison
st.markdown("### PO Amt vs Billed Till Date")
bar_df = df[["Project", " Total PO Amt ", "Billed Till Date"]].copy()
bar_df.columns = ["Project", "Total PO Amt", "Billed Till Date"]

st.bar_chart(bar_df.set_index("Project"))
