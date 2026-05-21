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
# FILTER NEXT 7 DAYS
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

    # Format
    display_df["Baseline"] = display_df["Baseline"].dt.strftime("%d-%b-%Y")
    display_df["Forecast"] = display_df["Forecast"].dt.strftime("%d-%b-%Y")
    display_df["% Complete"] = display_df["% Complete"].round(0).astype(int).astype(str) + "%"

    # =========================
    # KPI CALCULATIONS
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
    # ✅ KPI CARDS (NO HTML BUGS)
    # =========================
    st.markdown(
        f"""
        <div style="display:flex; gap:12px; margin-bottom:16px;">

            <div style="flex:1; background:white; padding:12px; border-radius:12px; text-align:center;">
                <div style="font-size:12px; color:#6b7280;">Deliverables (7 Days)</div>
                <div style="font-size:22px; font-weight:700;">{total}</div>
            </div>

            <div style="flex:1; background:white; padding:12px; border-radius:12px; text-align:center; border-left:4px solid #b71c1c;">
                <div style="font-size:12px; color:#6b7280;">Behind Plan</div>
                <div style="font-size:22px; font-weight:700; color:#b71c1c;">{behind}</div>
            </div>

            <div style="flex:1; background:white; padding:12px; border-radius:12px; text-align:center; border-left:4px solid #0d47a1;">
                <div style="font-size:12px; color:#6b7280;">On Plan</div>
                <div style="font-size:22px; font-weight:700; color:#0d47a1;">{on_plan}</div>
            </div>

            <div style="flex:1; background:white; padding:12px; border-radius:12px; text-align:center; border-left:4px solid #1b5e20;">
                <div style="font-size:12px; color:#6b7280;">Ahead</div>
                <div style="font-size:22px; font-weight:700; color:#1b5e20;">{ahead}</div>
            </div>

            <div style="flex:1; background:white; padding:12px; border-radius:12px; text-align:center; border-left:4px solid #ef6c00;">
                <div style="font-size:12px; color:#6b7280;">Critical (Float &lt; 0)</div>
                <div style="font-size:22px; font-weight:700; color:#ef6c00;">{critical}</div>
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    # =========================
    # TABLE OUTPUT
    # =========================
    st.dataframe(display_df, use_container_width=True)