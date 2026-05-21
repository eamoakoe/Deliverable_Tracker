import streamlit as st
import pandas as pd


# =========================
# DATA PREP
# =========================
def _prepare(df):
    df = df.copy()

    df.columns = df.columns.astype(str).str.strip()

    df["Start"] = pd.to_datetime(df["Start"], errors="coerce")
    df["Finish"] = pd.to_datetime(df["Finish"], errors="coerce")

    df["Activity % Complete"] = (
        df["Activity % Complete"]
        .astype(str)
        .str.replace("%", "", regex=False)
    )

    df["Activity % Complete"] = pd.to_numeric(
        df["Activity % Complete"], errors="coerce"
    ).fillna(0)

    return df


# =========================
# FEATURE ENGINEERING (ML-LITE)
# =========================
def _engineer_features(df):

    today = pd.Timestamp.today().normalize()

    df["Duration"] = (df["Finish"] - df["Start"]).dt.days
    df["Elapsed"] = (today - df["Start"]).dt.days.clip(lower=0)

    df["Expected %"] = (
        (df["Elapsed"] / df["Duration"]) * 100
    ).clip(upper=100)

    df["Efficiency"] = (
        df["Activity % Complete"] / df["Expected %"]
    ).replace([float("inf")], 0).fillna(0)

    return df


# =========================
# RISK PANEL
# =========================
def render_delivery_intelligence(df):

    df = _prepare(df)
    df = _engineer_features(df)

    if df.empty:
        return

    # ✅ Confidence score
    score = (
        (df["Activity % Complete"] > 80).astype(int) +
        (df["Efficiency"] >= 1).astype(int)
    ) / 2 * 100

    confidence = int(score.mean())

    # ✅ Hidden risks
    hidden_risk = df[
        (df["Activity % Complete"] < 75) &
        (df["Expected %"] > df["Activity % Complete"])
    ]

    # ✅ Trend
    trend = int((df["Finish"] - pd.Timestamp.today()).dt.days.mean())

    # ✅ Driver
    if (df["Efficiency"] < 0.8).sum() > 2:
        driver = "Slow Progress"
    elif (df["Activity % Complete"] < 50).sum() > 2:
        driver = "Low Completion"
    else:
        driver = "Stable"

    # =========================
    # DISPLAY PANEL
    # =========================
    st.markdown("### 🤖 Delivery Intelligence (CL32 May)")

    col1, col2 = st.columns(2)

    col1.metric("Confidence", f"{confidence}%")
    col1.metric("Hidden Risks", len(hidden_risk))

    col2.metric("Trend (Days)", trend)
    col2.metric("Main Driver", driver)

    # =========================
    # EXPLANATION (CRITICAL)
    # =========================
    st.caption("""
    **Guide:**
    • Confidence → likelihood of delivering on time based on progress vs expected  
    • Hidden Risks → activities that appear on track but are progressing slower than expected  
    • Trend → overall programme movement (negative = drifting late)  
    • Main Driver → dominant factor affecting current delivery performance  
    """)


# =========================
# DELAY TABLE (YOUR ORIGINAL)
# =========================
def _get_delayed(df):
    df = _prepare(df)

    today = pd.Timestamp.today().normalize()

    delayed = df[
        (df["Finish"].notna()) &
        (df["Finish"] < today) &
        (df["Activity % Complete"] < 100)
    ].copy()

    delayed["Delay (Days)"] = (today - delayed["Finish"]).dt.days

    return delayed.sort_values("Delay (Days)", ascending=False)


# =========================
# RENDER TABLE
# =========================
def render_delayed_table(df):

    # ✅ ADD ML PANEL FIRST
    render_delivery_intelligence(df)

    delayed = _get_delayed(df)

    if delayed.empty:
        st.success("No delayed deliverables 🎯")
        return

    display_df = delayed[[
        "Activity ID",
        "Activity Name",
        "Start",
        "Finish",
        "Delay (Days)",
        "Comments"
    ]].copy()

    display_df.rename(columns={
        "Activity ID": "ID",
        "Activity Name": "Activity",
        "Start": "Start Date",
        "Finish": "Finish Date",
        "Comments": "Remarks"
    }, inplace=True)

    display_df["Start Date"] = display_df["Start Date"].dt.strftime("%d-%b-%Y")
    display_df["Finish Date"] = display_df["Finish Date"].dt.strftime("%d-%b-%Y")

    # =========================
    # COLOUR DELAYS
    # =========================
    def colour_delay(val):
        if val >= 50:
            return "background-color:#d32f2f;color:white"
        elif val >= 30:
            return "background-color:#f57c00;color:white"
        elif val >= 15:
            return "background-color:#fbc02d;color:black"
        else:
            return "background-color:#c8e6c9;color:black"

    styled = display_df.style.map(colour_delay, subset=["Delay (Days)"])

    st.markdown(
        f"<span style='color:#d32f2f;font-weight:600;font-size:15px'>🔴 {len(display_df)} Delayed Activities</span>",
        unsafe_allow_html=True
    )

    st.write(styled)