import streamlit as st
import pandas as pd
import plotly.express as px


st.set_page_config(page_title="DCCB Loan Dashboard", layout="wide")

st.title("DCCB Loan Analytics Dashboard")

st.markdown("Upload your CSV file to generate insights")

uploaded_file = st.file_uploader("Upload Loan CSV File", type=["csv"])


if uploaded_file is None:
    st.info("👆 Please upload a CSV file to begin")
    st.stop()


try:
    df = pd.read_csv(uploaded_file)
except Exception as e:
    st.error(f"Error reading file: {e}")
    st.stop()


df.columns = df.columns.str.strip()

with st.expander("Debug: Columns in your file"):
    st.write(df.columns.tolist())

required_columns = [
    "Loan Number",
    "Bank Type",
    "Bank Name",
    "Sanction Amount",
    "Disbursement Amount",
    "Total Loan Amount"
]

missing_cols = [col for col in required_columns if col not in df.columns]

if missing_cols:
    st.error(f"Missing columns: {missing_cols}")
    st.stop()

dccb_df = df[df["Bank Type"].astype(str).str.upper() == "DCCB"]

if dccb_df.empty:
    st.warning("⚠️ No DCCB data found in file")
    st.stop()

dccb_df["Sanction Amount"] = pd.to_numeric(dccb_df["Sanction Amount"], errors="coerce")
dccb_df["Disbursement Amount"] = pd.to_numeric(dccb_df["Disbursement Amount"], errors="coerce")
dccb_df["Total Loan Amount"] = pd.to_numeric(dccb_df["Total Loan Amount"], errors="coerce")

report = dccb_df.groupby("Bank Name").agg(
    Total_Applications=("Loan Number", "count"),
    Total_Application_Amount=("Total Loan Amount", "sum"),
    Total_Sanctioned_Count=("Sanction Amount", lambda x: x.notna().sum()),
    Total_Sanctioned_Amount=("Sanction Amount", "sum"),
    Total_Disbursement_Count=("Disbursement Amount", lambda x: x.notna().sum()),
    Total_Disbursement_Amount=("Disbursement Amount", "sum")
).reset_index()


report = report.fillna(0)
report.insert(0, "Sr. No.", range(1, len(report) + 1))

st.markdown("## Key Metrics")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Applications", int(report["Total_Applications"].sum()))
col2.metric("Total Application Amount",f"₹ {int(report['Total_Application_Amount'].sum()):,}")
col3.metric("Total Sanction Amount", f"₹ {int(report['Total_Sanctioned_Amount'].sum()):,}")
col4.metric("Total Disbursement Amount", f"₹ {int(report['Total_Disbursement_Amount'].sum()):,}")


st.markdown("---")

# TABLE 
st.subheader("Bank-wise Summary")

st.dataframe(report, use_container_width=True)


# PIE CHART 
st.subheader("Application Distribution")

fig3 = px.pie(
    report,
    names="Bank Name",
    values="Total_Applications"
)

st.plotly_chart(fig3, use_container_width=True)


# DOWNLOAD 
csv = report.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download Report",
    data=csv,
    file_name="dccb_report.csv",
    mime="text/csv"
)

# #RAW DATA 
# with st.expander("View Raw Data"):
#     st.dataframe(df, use_container_width=True)