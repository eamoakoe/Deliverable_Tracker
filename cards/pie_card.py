import pandas as pd
P DATAimport streamlit as st
# =========================
def prepare(df):
    df = df.copy()

    # Ensure required columns exist
    if "Finish" not in df.columns:
        df["Finish"] = pd.NaT

    if "Remaining Duration" not in df.columns:
        df["Remaining Duration"] = "0.00d"

    # Convert finish to datetime
    df["Finish"] = pd.to_datetime(df["Finish"], errors="coerce")

    return df


# =========================
# STATUS CLASSIFICATION
# =========================
def classify_status(row):
    today = pd.Timestamp.today().normalize()

    finish = row.get("Finish")
    remaining = row.get("Remaining Duration")

    # Clean remaining duration
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

    # ✅ On Track
    return "On Track"


# =========================
# RENDER CHART
# =========================
def render_pie(df):

    if df is None or df.empty:
        st.warning("No data available")
        return

    df = prepare(df)

    # Apply classification
    df["Status"] = df.apply(classify_status, axis=1)

    # Count values
    summary = df["Status"].value_counts()

    # Display
    st.subheader("Programme Status")

    st.dataframe(summary.rename("Count"))

    # Simple visual
    st.bar_chart(summary)


# =========================
