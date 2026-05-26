import streamlit as st
import pandas as pd


# =========================
# PREP (ROSSALL CL32)
# =========================
def _prepare(df):

    df = df.copy()
    df.columns = df.columns.astype(str).str.strip()

    # ✅ Clean Finish (remove Primavera flags like A, *)
    df["Finish"] = (
        df["Finish"]
        .astype(str)
        .str.replace("A", "", regex=False)
        .str.replace("*", "", regex=False)
        .str.strip()
    )

    df["Finish"] = pd.to_datetime(df["Finish"], errors="coerce", dayfirst=True)

    # ✅ FLOAT (already days in your data)
    df["Float (Days)"] = (
        pd.to_numeric(df.get("Total Float"), errors="coerce")
        .fillna(0)
        .round(0)
        .astype(int)
    )

    return df


# =========================
# FILTER NEXT 7 DAYS
# =========================
def _get_next7days(df):

    df = _prepare(df)

    today = pd.Timestamp.today().normalize()
    lookahead = today + pd.Timedelta(days=7)

    # ✅ Date filter
    df = df[
        (df["Finish"] >= today) &
        (df["Finish"] <= lookahead)
    ].copy()

    # ✅ TRUE ROSSALL MILESTONES ONLY
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
        st.success("✅ No Rossall milestones due in next 7 days")
        return

    # =========================
    # RISK FLAG
    # =========================
    critical_flag = (df["Float (Days)"] <= 0).any()

    if critical_flag:
        st.warning("⚠️ Critical Rossall milestones at risk (zero or negative float)")
    else:
        st.info("✅ Rossall milestones are healthy")

    # =========================
    # TABLE
    # =========================
    display_df = df[[
        "Activity ID",
        "Activity Name",
        "Finish",
        "Float (Days)"
    ]].copy()

    display_df = display_df.rename(columns={
        "Finish": "Milestone Date"
    })

    # ✅ Format date
    display_df["Milestone Date"] = (
        pd.to_datetime(display_df["Milestone Date"])
        .dt.strftime("%d-%b-%Y")
    )

    # =========================
    # STATUS (CL32 LOGIC)
    # =========================
    def status(row):

        if row["Float (Days)"] <= 0:
            return "🔴 Critical"

        if row["Float (Days)"] <= 3:
            return "🟠 Tight"

        if row["Float (Days)"] <= 7:
            return "🟡 Watch"

        return "🟢 Healthy"

    display_df["Status (CL32)"] = display_df.apply(status, axis=1)

    # =========================
    # COLOURING
    # =========================
    def colour_float(val):
        if val <= 0:
            return "background-color:#b00020;color:white"
        elif val <= 3:
            return "background-color:#ff9800;color:black"
        elif val <= 7:
            return "background-color:#facc15;color:black"
        return ""

    def colour_status(val):
        if "🔴" in val:
            return "background-color:#b00020;color:white"
        elif "🟠" in val:
            return "background-color:#ff9800;color:black"
        elif "🟡" in val:
            return "background-color:#facc15;color:black"
        return "background-color:#14532d;color:white"

    styled = display_df.style \
        .map(colour_float, subset=["Float (Days)"]) \
        .map(colour_status, subset=["Status (CL32)"])

    st.markdown(styled.to_html(), unsafe_allow_html=True)
