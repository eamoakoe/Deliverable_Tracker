import streamlit as st
import pandas as pd


# =========================
# PREP DATA
# =========================
def _prepare(df):
    df = df.copy()
    df.columns = df.columns.astype(str).str.strip()

    df["Start"] = pd.to_datetime(df["Start"], errors="coerce")
    df["Finish"] = pd.to_datetime(df["Finish"], errors="coerce")
    df["BL1 Finish"] = pd.to_datetime(df["BL1 Finish"], errors="coerce")

    # ✅ FLOAT → WHOLE DAYS
    df["Total Float"] = (
        pd.to_numeric(df["Total Float"], errors="coerce")
        .fillna(0)
        .apply(lambda x: int(round(x)))  # already in days → just round
    )

    # ✅ CLEAN % COMPLETE
    df["Activity % Complete"] = (
        df["Activity % Complete"]
        .astype(str)
        .str.replace("%", "", regex=False)
    )

    df["Activity % Complete"] = (
        pd.to_numeric(df["Activity % Complete"], errors="coerce")
        .fillna(0)
        .apply(lambda x: int(round(x)))
    )

    # ✅ DELTA (WHOLE NUMBER DAYS)
    df["Change (days)"] = (
        (df["Finish"] - df["BL1 Finish"])
        .dt.days
    )

    return df


# =========================
# FILTER NEXT 7 DAYS
# =========================
def _get_next7days(df):
    df = _prepare(df)

    today = pd.Timestamp.today().normalize()
    lookahead = today + pd.Timedelta(days=7)

    df = df[
        (df["Finish"] >= today) &
        (df["Finish"] <= lookahead)
    ].copy()

    return df.sort_values("Finish")


# =========================
# MAIN RENDER
# =========================
def render_next7days_table(df):

    df = _get_next7days(df)

    if df.empty:
        st.success("✅ No activities issuing in the next 7 days")
        return

    # ✅ FLAGS
    late_flag = (df["Change (days)"] > 0).any()  # positive = delay
    risk_flag = ((df["Activity % Complete"] < 100) & (df["Total Float"] <= 0)).any()

    if late_flag or risk_flag:
        st.warning("⚠️ Some activities issuing in the next 7 days are delayed vs CL32 May or at risk")
    else:
        st.info("✅ Activities issuing in the next 7 days are aligned with the CL32 May programme")

    # =========================
    # TABLE STRUCTURE
    # =========================
    display_df = df[[
        "Activity ID",
        "Activity Name",
        "BL1 Finish",
        "Finish",
        "Change (days)",
        "Total Float",
        "Activity % Complete",
        "Comments"
    ]].copy()

    display_df = display_df.rename(columns={
        "BL1 Finish": "Baseline Finish (CL32 May)",
        "Finish": "Forecast Finish (CL32 May)",
        "Change (days)": "Δ Change vs CL32 May (days)",
        "Total Float": "Float (Days)",
        "Activity % Complete": "% Complete"
    })

    # =========================
    # FORMAT DATES
    # =========================
    display_df["Baseline Finish (CL32 May)"] = \
        pd.to_datetime(display_df["Baseline Finish (CL32 May)"]).dt.strftime("%d-%b-%Y")

    display_df["Forecast Finish (CL32 May)"] = \
        pd.to_datetime(display_df["Forecast Finish (CL32 May)"]).dt.strftime("%d-%b-%Y")

    # =========================
    # STATUS COLUMN (FIXED)
    # =========================
    def status(row):

        # ✅ COMPLETED
        if row["% Complete"] == 100:
            if row["Δ Change vs CL32 May (days)"] > 0:
                return "🔴 Completed Late"
            return "✅ Completed"

        # ✅ AT RISK (CRITICAL)
        if row["% Complete"] < 100 and row["Float (Days)"] <= 0:
            return "🔴 At Risk"

        # ✅ DELAYED
        if row["Δ Change vs CL32 May (days)"] > 0:
            return "🟠 Delayed"

        return "🟢 On Track"

    display_df["Status (CL32 May)"] = display_df.apply(status, axis=1)

    # =========================
    # RISK COLUMN
    # =========================
    def risk(row):
        if row["% Complete"] < 100 and row["Float (Days)"] <= 0:
            return "🔴 High Risk"
        elif row["% Complete"] < 75 and row["Δ Change vs CL32 May (days)"] > 0:
            return "🟠 Behind Progress"
        elif row["% Complete"] >= 90 and row["Δ Change vs CL32 May (days)"] > 0:
            return "⚠️ Near Complete but Late"
        else:
            return "🟢 Low Risk"

    display_df["Risk (Forward Look)"] = display_df.apply(risk, axis=1)

    # =========================
    # COLOUR FUNCTIONS
    # =========================
    def colour_change(val):
        if pd.isna(val):
            return "background-color:#374151;color:white"
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
        elif "✅" in val or "🟢" in val:
            return "background-color:#14532d;color:white"
        return ""

    def colour_risk(val):
        if "🔴" in val:
