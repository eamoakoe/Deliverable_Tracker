import streamlit as st
import pandas as pd


# =========================
# DATA PREPARATION
# =========================
def _prepare(df):
    df = df.copy()
    df.columns = df.columns.astype(str).str.strip()

    df["Finish"] = pd.to_datetime(df["Finish"], errors="coerce")
    df["BL1 Finish"] = pd.to_datetime(df.get("BL1 Finish"), errors="coerce")

    df["Total Float"] = pd.to_numeric(df.get("Total Float"), errors="coerce")

    df["Activity % Complete"] = (
        df["Activity % Complete"]
        .astype(str)
        .str.replace("%", "", regex=False)
    )

    df["Activity % Complete"] = pd.to_numeric(
        df["Activity % Complete"],
        errors="coerce"
    ).fillna(0)

    return df


# =========================
# 7 DAY FILTER
# =========================
def _get_next7days(df):
    df = _prepare(df)

    today = pd.Timestamp.today().normalize()
    lookahead = today + pd.Timedelta(days=7)

    upcoming = df[
        (df["Finish"].notna()) &
        (df["Finish"] >= today) &
        (df["Finish"] <= lookahead)
    ].copy()

    upcoming["Change (Days)"] = (
        upcoming["Finish"] - upcoming["BL1 Finish"]
    ).dt.days

    return upcoming.sort_values("Finish")


# =========================
# KPI CARD FUNCTION
# =========================
def kpi_card(title, value, color=None):
    border = f"border-left:4px solid {color};" if color else ""

    return f"""
    <div style="
        flex:1;
        background:white;
        padding:12px;
        border-radius:12px;
        text-align:center;
        {border}
        box-shadow:0 1px 3px rgba(0,0,0,0.1);
    ">
        <div style="font-size:12px; color:#6b7280;">{title}</div>
        <div style="font-size:22px; font-weight:700; color:{color or '#111'};">
            {value}
        </div>
    </div>
    """


# =========================
# RENDER FUNCTION
# =========================
def render_next7days_table(df):

    forecast = _get_next7days(df)

    if forecast.empty:
        st.success("No deliverables due in next 7 days 🎯")
        return

    display_df = forecast[[
        "Activity ID",
        "Activity Name",
        "BL1 Finish",
        "Finish",
        "Total Float",
        "Activity % Complete"
    ]].copy()

    display_df.rename(columns={
        "Activity ID": "ID",
        "Activity Name": "Activity",
        "BL1 Finish": "Baseline",
        "Finish": "Forecast",
        "Total Float": "Float",
        "Activity % Complete": "% Complete"
    }, inplace=True)

    display_df["Baseline"] = display_df["Baseline"].dt.strftime("%d-%b-%Y")
    display_df["Forecast"] = display_df["Forecast"].dt.strftime("%d-%b-%Y")
    display_df["% Complete"] = display_df["% Complete"].round(0).astype(int).astype(str) + "%"

    # =========================
    # KPI CALCS
    # =========================
    total = len(display_df)

    change = (
        forecast["Finish"] - forecast["BL1 Finish"]
    ).dt.days

    behind = (change > 0).sum()
    on_plan = (change == 0).sum()
    ahead = (change < 0).sum()
    critical = (forecast["Total Float"] < 0).sum()

    # =========================
    # ✅ KPI UI (FIXED)
    # =========================
    st.markdown(
        f"""
        <div style="display:flex; gap:12px; margin-bottom:16px">

            {kpi_card("Deliverables (7 Days)", total)}
            {kpi_card("Behind Plan", behind, "#b71c1c")}
            {kpi_card("On Plan", on_plan, "#0d47a1")}
            {kpi_card("Ahead", ahead, "#1b5e20")}
            {kpi_card("Critical (Float < 0)", critical, "#ef6c00")}

        </div>
        """,
        unsafe_allow_html=True
    )

    # =========================
    # TABLE
    # =========================
    st.dataframe(display_df, use_container_width=True)