import streamlit as st
import pandas as pd


# =========================
# PREP (ROSSALL REAL DATA)
# =========================
def _prepare(df):

    df = df.copy()
    df.columns = df.columns.astype(str).str.strip()

    # ✅ Dates (handle "A", "*" etc.)
    df["Finish"] = (
        df["Finish"]
        .astype(str)
        .str.replace("A", "", regex=False)
        .str.replace("*", "", regex=False)
        .str.strip()
    )

    df["Finish"] = pd.to_datetime(df["Finish"], errors="coerce", dayfirst=True)

    # ✅ FLOAT (already days)
    df["Float (Days)"] = (
        pd.to_numeric(df.get("Total Float"), errors="coerce")
        .fillna(0)
        .round(0)
        .astype(int)
    )

    # ✅ % COMPLETE (often missing → treat as 0)
    if "Activity % Complete" in df.columns:
        pct = df["Activity % Complete"].astype(str).str.replace("%", "", regex=False)
        pct = pd.to_numeric(pct, errors="coerce")
    else:
        pct = pd.Series(0, index=df.index)

    df["% Complete"] = pct.fillna(0).astype(int)

    return df


# =========================
# FILTER NEXT 7 DAYS
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

    # ✅ TRUE ROSSALL DELIVERABLES
    df = df[
        df["Activity ID"].astype(str).str.contains("ROS-MIL", na=False)
    ]

    return df.sort_values("Finish")


# =========================
# MAIN RENDER
# =========================
def render_next7days_table(df):

    df = _get_next7days(df)

    if df.empty:
        st.success("✅ No Rossall milestones in next 7 days")
        return

    # ✅ RISK FLAGS (REAL LOGIC)
    risk_flag = ((df["% Complete"] < 100) & (df["Float (Days)"] <= 0)).any()

    if risk_flag:
        st.warning("⚠️ Critical Rossall milestones at risk")
    else:
        st.info("✅ Rossall milestones on track")

    # =========================
    # TABLE
    # =========================
    display_df = df[[
        "Activity ID",
        "Activity Name",
        "Finish",
        "Float (Days)",
        "% Complete"
    ]].copy()

    display_df = display_df.rename(columns={
        "Finish": "Milestone Date"
    })

    display_df["Milestone Date"] = pd.to_datetime(
        display_df["Milestone Date"]
    ).dt.strftime("%d-%b-%Y")

    # =========================
    # STATUS
    # =========================
    def status(row):

        if row["% Complete"] == 100:
            return "✅ Completed"

        if row["Float (Days)"] <= 0:
            return "🔴 Critical"

        if row["Float (Days)"] <= 5:
            return "🟠 Low Float"

        return "🟢 Healthy"

    display_df["Status"] = display_df.apply(status, axis=1)

    # =========================
    # COLOURS
    # =========================
    def colour_float(val):
        if val <= 0:
            return "background-color:#b00020;color:white"
        elif val <= 5:
            return "background-color:#ff9800;color:black"
        return ""

    def colour_status(val):
        if "🔴" in val:
            return "background-color:#b00020;color:white"
        elif "🟠" in val:
            return "background-color:#ff9800;color:black"
        return "background-color:#14532d;color:white"

    styled = display_df.style \
        .map(colour_float, subset=["Float (Days)"]) \
        .map(colour_status, subset=["Status"])

    st.markdown(styled.to_html(), unsafe_allow_html=True)