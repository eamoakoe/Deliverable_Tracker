import streamlit as st
import pandas as pd


# =========================
# SHARED FERRIES STYLE ✅
# =========================
def format_like_ferries(display_df):

    def colour_change(val):
        if val < 0:
            return "background-color:#7f1d1d;color:white;font-weight:bold"
        elif val > 0:
            return "background-color:#14532d;color:white;font-weight:bold"
        return "background-color:#374151;color:white"

    def colour_float(val):
        if pd.isna(val):
            return ""
        if val <= 0:
            return "background-color:#b00020;color:white"
        return ""

    def colour_status(val):
        if "🔴" in val:
            return "background-color:#b00020;color:white"
        elif "🟠" in val:
            return "background-color:#ff9800;color:black"
        elif "🟡" in val:
            return "background-color:#facc15;color:black"
        elif "🟢" in val:
            return "background-color:#1e7e34;color:white"
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

    styled = display_df.style.set_table_styles([
        {
            "selector": "th",
            "props": [
                ("background-color", "#2b3a55"),
                ("color", "white"),
                ("font-weight", "600"),
                ("padding", "10px")
            ]
        },
        {
            "selector": "td",
            "props": [
                ("background-color", "#1c2233"),
                ("color", "#f1f1f1"),
                ("padding", "8px")
            ]
        }
    ])

    if "Δ Change vs CL32 May (days)" in display_df.columns:
        styled = styled.map(colour_change, subset=["Δ Change vs CL32 May (days)"])

    if "Float (Days)" in display_df.columns:
        styled = styled.map(colour_float, subset=["Float (Days)"])

    if "Status (CL32 May)" in display_df.columns:
        styled = styled.map(colour_status, subset=["Status (CL32 May)"])

    if "Risk (Forward Look)" in display_df.columns:
        styled = styled.map(colour_risk, subset=["Risk (Forward Look)"])

    return styled


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

    # ✅ FLOAT → whole number
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

    df = df[
        (df["Finish"] >= today) &
        (df["Finish"] <= lookahead)
    ].copy()

    # ✅ Rossall milestones only
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
    # HEADER MESSAGE
    # =========================
    critical_flag = (df["Float (Days)"] <= 0).any()

    if critical_flag:
        st.warning("⚠️ Critical Rossall milestones at risk (zero or negative float)")
    else:
        st.info("✅ Rossall milestones are healthy")

    # =========================
    # BUILD TABLE
    # =========================
    display_df = df[[
        "Activity ID",
        "Activity Name",
        "Finish",
        "Float (Days)"
    ]].copy()

    display_df = display_df.rename(columns={
        "Finish": "Forecast Finish (CL32 May)"
    })

    # ✅ Format date
    display_df["Forecast Finish (CL32 May)"] = (
        pd.to_datetime(display_df["Forecast Finish (CL32 May)"])
        .dt.strftime("%d-%b-%Y")
    )

    # =========================
    # STATUS
    # =========================
    def status(row):
        if row["Float (Days)"] <= 0:
            return "🔴 Critical"
        elif row["Float (Days)"] <= 3:
            return "🟠 Tight"
        elif row["Float (Days)"] <= 7:
            return "🟡 Watch"
        return "🟢 Healthy"

    display_df["Status (CL32 May)"] = display_df.apply(status, axis=1)

    # =========================
    # RISK (MATCH FERRIES STYLE)
    # =========================
    def risk(row):
        if row["Float (Days)"] <= 0:
            return "🔴 High Risk"
        elif row["Float (Days)"] <= 3:
            return "🟠 Tight Window"
        elif row["Float (Days)"] <= 7:
            return "⚠️ Watch"
        return "🟢 Low Risk"

    display_df["Risk (Forward Look)"] = display_df.apply(risk, axis=1)

    # =========================
    # APPLY SHARED STYLE ✅
    # =========================
    styled = format_like_ferries(display_df)

    st.markdown(styled.to_html(), unsafe_allow_html=True)
