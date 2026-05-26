import streamlit as st
import pandas as pd


# =========================
# PREP DATA (ROSSALL SPECIFIC)
# =========================
def _prepare(df):
    df = df.copy()
    df.columns = df.columns.astype(str).str.strip()

    # ✅ Dates
    df["Start"] = pd.to_datetime(df["Start"], errors="coerce")
    df["Finish"] = pd.to_datetime(df["Finish"], errors="coerce")
    df["BL1 Finish"] = pd.to_datetime(df["BL1 Finish"], errors="coerce")

    # ✅ FLOAT (already days for Rossall)
    df["Float (Days)"] = (
        pd.to_numeric(df.get("Total Float", 0), errors="coerce")
        .fillna(0)
        .round(0)
        .astype(int)
    )

    # ✅ % COMPLETE
    pct = df.get("Activity % Complete", 0).astype(str).str.replace("%", "", regex=False)
    df["% Complete"] = pd.to_numeric(pct, errors="coerce").fillna(0).astype(int)

    # ✅ DELTA (correct direction)
    df["Δ Change (days)"] = (
        (df["Finish"] - df["BL1 Finish"])
        .dt.days
    )

    return df


# =========================
# FILTER NEXT 7 DAYS (ROSSALL DM LOGIC)
# =========================
def _get_next7days(df):
    df = _prepare(df)

    today = pd.Timestamp.today().normalize()
    lookahead = today + pd.Timedelta(days=7)

    # ✅ DATE FILTER
    df = df[
        (df["Finish"] >= today) &
        (df["Finish"] <= lookahead)
    ].copy()

    # ✅ ROSSALL DELIVERABLE FILTER (REAL DATA DRIVEN)
    deliverable_ids = ["-KD-", "-DD", "-DR"]

    df = df[
        df["Activity ID"].astype(str).str.contains("|".join(deliverable_ids), na=False)
    ]

    # ✅ REMOVE LONG CONSTRUCTION TASKS
    if "Remaining Duration" in df.columns:
        df["Remaining Duration"] = pd.to_numeric(df["Remaining Duration"], errors="coerce")
        df = df[df["Remaining Duration"] <= 10]

    return df.sort_values("Finish")


# =========================
# MAIN RENDER
# =========================
def render_next7days_table(df):

    df = _get_next7days(df)

    if df.empty:
        st.success("✅ No deliverables issuing in the next 7 days")
        return

    # ✅ FLAGS (FIXED LOGIC)
    late_flag = (df["Δ Change (days)"] > 0).any()
    risk_flag = ((df["% Complete"] < 100) & (df["Float (Days)"] <= 0)).any()

    if late_flag or risk_flag:
        st.warning("⚠️ Key Rossall deliverables are delayed or at risk")
    else:
        st.info("✅ Rossall deliverables are on track")

    # =========================
    # TABLE
    # =========================
    display_df = df[[
        "Activity ID",
        "Activity Name",
        "BL1 Finish",
        "Finish",
        "Δ Change (days)",
        "Float (Days)",
        "% Complete"
    ]].copy()

    display_df = display_df.rename(columns={
        "BL1 Finish": "Baseline Finish",
        "Finish": "Forecast Finish"
    })

    # ✅ FORMAT
    display_df["Baseline Finish"] = pd.to_datetime(display_df["Baseline Finish"]).dt.strftime("%d-%b-%Y")
    display_df["Forecast Finish"] = pd.to_datetime(display_df["Forecast Finish"]).dt.strftime("%d-%b-%Y")

    # =========================
    # STATUS (FIXED + DM LOGIC)
    # =========================
    def status(row):

        # ✅ Completed
        if row["% Complete"] == 100:
            if row["Δ Change (days)"] > 0:
                return "🔴 Completed Late"
            return "✅ Completed"

        # ✅ Critical risk
        if row["Float (Days)"] <= 0:
            return "🔴 At Risk"

        # ✅ Delay
        if row["Δ Change (days)"] > 0:
            return "🟠 Delayed"

        return "🟢 On Track"

    display_df["Status"] = display_df.apply(status, axis=1)

    # =========================
    # RISK
    # =========================
    def risk(row):
        if row["% Complete"] < 100 and row["Float (Days)"] <= 0:
            return "🔴 High Risk"
        elif row["Δ Change (days)"] > 0:
            return "🟠 Programme Risk"
        return "🟢 Low Risk"

    display_df["Risk"] = display_df.apply(risk, axis=1)

    # =========================
    # COLOURS
    # =========================
    def colour_change(val):
        if val > 0:
            return "background-color:#7f1d1d;color:white;font-weight:bold"
        elif val < 0:
            return "background-color:#14532d;color:white;font-weight:bold"
        return "background-color:#374151;color:white"

    def colour_float(val):
        if val <= 0:
            return "background-color:#b00020;color:white"
        return ""

    def colour_status(val):
        if "🔴" in val:
            return "background-color:#b00020;color:white"
        elif "🟠" in val:
            return "background-color:#ff9800;color:black"
        return "background-color:#14532d;color:white"

    def colour_risk(val):
        if "🔴" in val:
            return "background-color:#7f1d1d;color:white"
        elif "🟠" in val:
            return "background-color:#ff9800;color:black"
        return "background-color:#14532d;color:white"

    styled = display_df.style \
        .map(colour_change, subset=["Δ Change (days)"]) \
        .map(colour_float, subset=["Float (Days)"]) \
        .map(colour_status, subset=["Status"]) \
        .map(colour_risk, subset=["Risk"])

    st.markdown(styled.to_html(), unsafe_allow_html=True)
