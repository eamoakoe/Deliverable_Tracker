import pandas as pd
import streamlitimport streamlit as st
# PREP
# =========================
def prepare(df):
    df = df.copy()

    # ✅ Ensure required columns
    if "Finish" not in df.columns:
        df["Finish"] = pd.NaT

    if "Remaining Duration" not in df.columns:
        df["Remaining Duration"] = "0.00d"

    df["Finish"] = pd.to_datetime(df["Finish"], errors="coerce")

    return df


# =========================
# STATUS LOGIC
# =========================
def classify_status(row):

    today = pd.Timestamp.today().normalize()

    finish = row.get("Finish")
    remaining = row.get("Remaining Duration")

    # ✅ Clean remaining duration
    try:
        remaining_val = float(str(remaining).replace("d", "").strip())
    except:
        remaining_val = None

    # ✅ COMPLETED
    if remaining_val == 0:
        return "Completed"

    # ✅ DELAYED
    if pd.notna(finish) and finish < today:
        return "Delayed"

    # ✅ ON TRACK
    return "On Track"


# =========================
# DISPLAY
# =========================
def render_pie(df):

    if df is None or df.empty:
        st.warning("No data available")
        return

    df = prepare(df)

    df["Status"] = df.apply(classify_status, axis=1)

    summary = df["Status"].value_counts()

    # ✅ Display
    st.subheader("Programme Status")
    st.dataframe(summary.rename("Count"))

    # Optional: quick visual
    st.bar_chart(summary)



