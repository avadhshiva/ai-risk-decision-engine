import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="AI Risk Dashboard", layout="wide")

st.title("AI Risk Decision Dashboard")

# 🔹 Get latest CSV
def get_latest_csv():
    files = [f for f in os.listdir() if f.startswith("results_") and f.endswith(".csv")]
    if not files:
        return None
    files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    return files[0]


# 🔹 Convert newline to HTML break
def clean_format(text):
    if pd.isna(text):
        return ""
    return str(text).replace("\n", "<br>")


latest_file = get_latest_csv()

if latest_file:
    st.success(f"Loaded file: {latest_file}")

    df = pd.read_csv(latest_file)

    # 🔹 Filters
    st.subheader("Filter Data")

    col1, col2 = st.columns(2)

    with col1:
        risk_filter = st.selectbox(
            "Select Risk Level",
            ["All", "LOW", "MEDIUM", "HIGH"]
        )

    with col2:
        category_filter = st.selectbox(
            "Select Category",
            ["All"] + list(df["category"].dropna().unique())
        )

    if risk_filter != "All":
        df = df[df["risk_level"] == risk_filter]

    if category_filter != "All":
        df = df[df["category"] == category_filter]

    # 🔹 Format display
    df_display = df.copy()
    df_display["scenario"] = df_display["scenario"].apply(clean_format)
    df_display["impact"] = df_display["impact"].apply(clean_format)
    df_display["mitigation"] = df_display["mitigation"].apply(clean_format)

    # 🔹 Styling (alignment fix)
    st.markdown(
        """
        <style>
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th {
            text-align: left !important;
            padding: 10px;
            background-color: #f0f2f6;
        }
        td {
            text-align: left !important;
            padding: 10px;
            vertical-align: top;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # 🔹 Render table
    st.subheader("Results")

    st.markdown(
        df_display.to_html(escape=False, index=False),
        unsafe_allow_html=True
    )

    # 🔹 Charts
    st.subheader("Risk Score Distribution")
    st.bar_chart(df["risk_score"])

    st.subheader("Risk Level Count")
    st.bar_chart(df["risk_level"].value_counts())

else:
    st.warning("No results file found. Run app.py first.")