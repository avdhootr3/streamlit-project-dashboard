import streamlit as st
import pandas as pd
from io import BytesIO

# --- Data Loading ---
@st.cache_data
def load_data():
    df = pd.read_excel("weekly_updates.xlsx", sheet_name="Billing_Summary")
    # Standardize column names by removing extra spaces
    df.columns = df.columns.str.strip()
    return df

df = load_data()

# --- Sanity Check: Print columns for debugging ---
print("Columns after loading:", df.columns.tolist())


def style_negative(value, threshold=0):
    return f"color: {'red' if value < threshold else '#000000'}" if value < threshold else None

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
    if pd.notna(row["Challenges / Risks"]) and str(row["Challenges / Risks"]).strip() not in ["", "0"]:
        score += 1
    if (row["Open AR"] > 0.1 * row["Total PO Amt"]) or (row["Open Billing"] > 0.1 * row["Total PO Amt"]):
        score += 1
    return score



st.set_page_config(layout="wide")
st.title("Project Portfolio Dashboard (Weekly Updates)")

# --- Filters ---
region_filter = st.multiselect("Filter by Region", df["Region"].unique(), default=df["Region"].unique())
type_filter = st.multiselect("Filter by Type", df["Type"].unique(), default=df["Type"].unique())

n_top = st.slider("Top N Projects by Open AR", 1, 20, 5)

# --- Filter Data ---
filtered_df = df[
    (df["Region"].isin(region_filter)) &
    (df["Type"].isin(type_filter))
].copy()

if filtered_df.empty:
    st.warning("No projects match your filters. Showing all projects.")
    filtered_df = df.copy()

# --- Calculate Risk Score ---
filtered_df["Risk Score"] = filtered_df.apply(risk_score, axis=1)
top_n_open_ar = filtered_df.nlargest(n_top, "Open AR")

# --- Display Key Metrics ---
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Projects", len(filtered_df))
col2.metric("Total PO Amount (₹ Cr)", round(filtered_df["Total PO Amt"].sum() / 100, 2))
col3.metric("Billed Till Date (₹ Cr)", round(filtered_df["Billed Till Date"].sum() / 100, 2))
col4.metric("Open AR (₹ Cr)", round(filtered_df["Open AR"].sum() / 100, 2))
col5.metric("Open Billing (₹ Cr)", round(filtered_df["Open Billing"].sum() / 100, 2))

# --- Main Data Table ---
st.header("Project Portfolio (Filtered)")
columns_to_display = [
    "Project", "Region", "Type", "Total PO Amt", "Billed Till Date",
    "Open AR", "Open Billing", "Current Month Billing", "Project Duration",
    "Billed", "Billing Milestone", "Resource Deployed", "Overall Progress",
    "Risk Score", "Challenges / Risks"
]

styled_df = filtered_df[columns_to_display].style.applymap(
    style_negative, subset=["Open AR", "Open Billing"]
)
st.dataframe(styled_df, height=800, use_container_width=True)

# --- Export Data ---
if st.button("Export Data (Excel)"):
    st.download_button(
        "Download",
        make_downloadable(filtered_df, "xlsx"),
        "weekly_project_status.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# --- Project Drill-Down ---
selected_project = st.selectbox("Select Project for Details", filtered_df["Project"].unique())
proj = filtered_df[filtered_df["Project"] == selected_project].squeeze()

with st.expander(f"**Project Details: {selected_project}**"):
    st.subheader(f"**{selected_project}**")
    cols = st.columns(2)
    with cols[0]:
        st.metric("PO Amount (₹ Cr)", round(proj["Total PO Amt"] / 100, 2))
        st.metric("Billed Till Date (₹ Cr)", round(proj["Billed Till Date"] / 100, 2))
        st.metric("Open AR (₹ Cr)", round(proj["Open AR"] / 100, 2))
        st.metric("Open Billing (₹ Cr)", round(proj["Open Billing"] / 100, 2))
        st.metric("% Billed", f"{proj['Billed'] * 100:.2f}%")
    with cols[1]:
        st.metric("Project Duration", proj["Project Duration"])
        st.metric("Resources Deployed", proj["Resource Deployed"])
        st.metric("Risk Score", proj["Risk Score"])
    st.write("**Milestone:** ", proj["Billing Milestone"])
    st.write("**Scope:** ", proj["Scope"] if pd.notna(proj["Scope"]) else "NA")
    st.write("**Progress:** ", proj["Overall Progress"] if pd.notna(proj["Overall Progress"]) else "NA")
    st.write("**Plan:** ", proj["Weekly Plan"] if pd.notna(proj["Weekly Plan"]) else "NA")
    st.write("**Tech Stack:** ", proj["Technology / tools"] if pd.notna(proj["Technology / tools"]) else "NA")
    risks = proj["Challenges / Risks"]
    st.write("**Risks:** ", risks if pd.notna(risks) and str(risks).strip() not in ["", "0"] else "No critical risks reported.")

# --- Top N Projects by Open AR ---
st.header(f"Top {n_top} Projects by Open AR")
st.dataframe(
    top_n_open_ar[["Project", "Region", "Total PO Amt", "Open AR", "Challenges / Risks"]],
    height=300,
    use_container_width=True
)
