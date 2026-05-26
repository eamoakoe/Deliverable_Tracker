import streamlit as st
import pandas as pd


# =========================
# PREP DATA (FLASS SAFE)
# =========================
def _prepare(df):
    df = df.copy()
    df.columns = df.columns.astype(str).str.strip()

    # ✅ Dates
    df["Start"] = pd.to_datetime(df.get("Start"), errors="coerce")
    df["Finish"] = pd.to_datetime(df.get("Finish"), errors="coerce")
    df["BL Project Finish"] = pd.to_datetime(df.get("BL Project Finish"), errors="coerce")

    # =========================
    # ✅ FLOAT (hours → whole days)
    # =========================
    if "Total Float(h)" in df.columns:
        float_series = pd.to_numeric(df["Total Float(h)"], errors="coerce")
    else:
        float_series = pd.Series(0, index=df.index)

    df["Float (Days)"] = (
        float_series
        .fillna(0)
        .apply(lambda x: int(round(x / 24)))
    )

    # =========================
    # ✅ % COMPLETE
    # =========================
    if "Activity % Complete" in df.columns:
        pct_series = pd.to_numeric(df["Activity % Complete"], errors="coerce")
    else:
        pct_series = pd.Series(0, index=df.index)

    df["% Complete"] = pct_series.fillna(0).astype(int)

    # =========================
    # ✅ DELTA (USE VARIANCE FIRST)
    # =========================
    if "Variance - BL Project Finish Date(h)" in df.columns:
        var_series = pd.to_numeric(df["Variance - BL Project Finish Date(h)"], errors="coerce")

        df["Δ Change (days)"] = (
            var_series
            .fillna(0)
            .apply(lambda x: int(round(x / 24)))
        )
    else:
        df["Δ Change (days)"] = (
            (df["Finish"] - df["BL Project Finish"])
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

    # =========================
    # ✅ FLAGS
    # =========================
    late_flag = (df["Δ Change (days)"] > 0).any()
    risk_flag = ((df["% Complete"] < 100) & (df["Float (Days)"] <= 0)).any()

    if late_flag or risk_flag:
        st.warning("⚠️ Activities issuing in the next 7 days are delayed or at risk")
    else:
        st.info("✅ Activities issuing in the next 7 days are aligned with programme")

    # =========================
    # TABLE STRUCTURE
    # =========================
    display_df = df[[
        "Activity ID",
        "Activity Name",
        "BL Project Finish",
        "Finish",
        "Δ Change (days)",
        "Float (Days)",
        "% Complete"
    ]].copy()

    display_df = display_df.rename(columns={
        "BL Project Finish": "Baseline Finish",
        "Finish": "Forecast Finish"
    })

    # =========================
    # FORMAT DATES
    # =========================
    display_df["Baseline Finish"] = pd.to_datetime(display_df["Baseline Finish"]).dt.strftime("%d-%b-%Y")
    display_df["Forecast Finish"] = pd.to_datetime(display_df["Forecast Finish"]).dt.strftime("%d-%b-%Y")

    # =========================
    # STATUS
    # =========================
    def status(row):
        if row["% Complete"] == 100:
            if row["Δ Change (days)"] > 0:
                return "🔴 Completed Late"
            return "✅ Completed"

        if row["% Complete"] < 100 and row["Float (Days)"] <= 0:
            return "🔴 At Risk"

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
        elif row["% Complete"] < 75 and row["Δ Change (days)"] > 0:
            return "🟠 Behind Progress"
        elif row["% Complete"] >= 90 and row["Δ Change (days)"] > 0:
            return "⚠️ Near Complete but Late"
        return "🟢 Low Risk"

    display_df["Risk"] = display_df.apply(risk, axis=1)

    # =========================
    # COLOUR FUNCTIONS
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
        elif "✅" in val or "🟢" in val:
            return "background-color:#14532d;color:white"
        return ""

    def colour_risk(val):
        if "🔴" in val:
            return "background-color:#7f1d1d;color:white"
        elif "🟠" in val:
            return "background-color:#ff9800;color:black"
        elif "⚠️" in val:
            return "background-color:#facc15;color:black"
        elif "🟢" in val:
            return "background-color:#14532d;color:white"
        return ""

    # =========================
    # STYLE TABLE
    # =========================
    styled = display_df.style \
        .map(colour_change, subset=["Δ Change (days)"]) \
        .map(colour_float, subset=["Float (Days)"]) \
        .map(colour_status, subset=["Status"]) \
        .map(colour_risk, subset=["Risk"])

    st.markdown(styled.to_html(), unsafe_allow_html=True)
