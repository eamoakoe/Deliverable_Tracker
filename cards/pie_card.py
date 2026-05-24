import pandas as pd
import streamlit as st


# =========================
# PREP DATA
# =================["Finish"] = pd.NaT# =========================

    if "Remaining Duration" not in df.columns:
        df["Remaining Duration"] = "0.00d"

    df["Finish"] = pd.to_datetime(df["Finish"], errors="coerce")

    return df


# =========================
# STATUS CLASSIFICATION
# =========================
def classify_status(row):
    today = pd.Timestamp.today().normalize()

    finish = row.get("Finish")
    remaining = row.get("Remaining Duration")

    try:
        remaining_val = float(str(remaining).replace("d", "").strip())
    except:
        remaining_val = None

    # ✅ Completed
    if remaining_val == 0:
        return "Completed"

    # ✅ Delayed
    if pd.notna(finish) and finish < today:
        return "Delayed"

    return "On Track"


# =========================
# RENDER
# =========================
def render_pie(df):

    if df is None or df.empty:
        st.warning("No data available")
        return

    df = prepare(df)

    df["Status"] = df.apply(classify_status, axis=1)

    summary = df["Status"].value_counts()

    st.subheader("Programme Status")

    st.dataframe(summary.rename("Count"))

    st.bar_chart(summary)
def prepare(df):
    df = df.copy()

    if "Finish" not in df.columns:
