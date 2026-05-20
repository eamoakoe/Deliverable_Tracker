import streamlit as stimport stream_datetime(df.get("BL1 Finish"), errors="coerce")

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
# ✅ 7-DAY ISSUE FORECAST
# =========================
def _get_next4weeks(df):   # name unchanged
    df = _prepare(df)

    today = pd.Timestamp.today().normalize()
    lookahead = today + pd.Timedelta(days=7)

    upcoming = df[
        (df["Finish"].notna()) &
        (df["Finish"] >= today) &
        (df["Finish"] <= lookahead)
    ].copy()

    # Change vs baseline
    upcoming["Change (Days)"] = (
        upcoming["Finish"] - upcoming["BL1 Finish"]
    ).dt.days

    return upcoming.sort_values("Finish")


# =========================
# RENDER TABLE + KPI
# =========================
def render_next4weeks_table(df):

    forecast = _get_next4weeks(df)

    if forecast.empty:
        st.success("No deliverables due in next 7 days 🎯")
        return

    display_df = forecast[[
        "Activity ID",
        "Activity Name",
        "BL1 Finish",
        "Finish",
        "Change (Days)",
        "Total Float",
        "Activity % Complete"
    ]].copy()

    # =========================
    # CLEAN HEADERS
    # =========================
    display_df.rename(columns={
        "Activity ID": "ID",
        "Activity Name": "Activity",
        "BL1 Finish": "Baseline Finish",
        "Finish": "Forecast Finish",
        "Total Float": "Float",
        "Activity % Complete": "% Complete"
    }, inplace=True)

    # =========================
    # FORMAT VALUES
    # =========================
    display_df["Baseline Finish"] = display_df["Baseline Finish"].dt.strftime("%d-%b-%Y")
    display_df["Forecast Finish"] = display_df["Forecast Finish"].dt.strftime("%d-%b-%Y")
    display_df["% Complete"] = display_df["% Complete"].round(0).astype(int).astype(str) + "%"

    # =========================
    # KPI CALCULATIONS
    # =========================
    total = len(display_df)
    behind = (display_df["Change (Days)"] > 0).sum()
    on_plan = (display_df["Change (Days)"] == 0).sum()
    ahead = (display_df["Change (Days)"] < 0).sum()
    critical = (display_df["Float"] < 0).sum()

    # =========================
    # ✅ KPI CARDS (FIXED)
    # =========================
    st.markdown(f"""
<div style="display:flex; gap:12px; margin-bottom:12px;">

    <div style="flex:1; background:white; padding:10px; border-radius:10px; text-align:center;">
        <div style="font-size:12px; color:#6b7280;">Deliverables (7 Days)</div>
        <div style="font-size:20px; font-weight:700;">{total}</div>
    </div>

    <div style="flex:1; background:white; padding:10px; border-radius:10px; text-align:center; border-left:4px solid #b71c1c;">
        <div style="font-size:12px; color:#6b7280;">Behind Plan</div>
        <div style="font-size:20px; font-weight:700; color:#b71c1c;">{behind}</div>
    </div>

    <div style="flex:1; background:white; padding:10px; border-radius:10px; text-align:center; border-left:4px solid #0d47a1;">
        <div style="font-size:12px; color:#6b7280;">On Plan</div>
        <div style="font-size:20px; font-weight:700; color:#0d47a1;">{on_plan}</div>
    </div>

    <div style="flex:1; background:white; padding:10px; border-radius:10px; text-align:center; border-left:4px solid #1b5e20;">
        <div style="font-size:12px; color:#6b7280;">Ahead</div>
        <div style="font-size:20px; font-weight:700; color:#1b5e20;">{ahead}</div>
    </div>

    <div style="flex:1; background:white; padding:10px; border-radius:10px; text-align:center; border-left:4px solid #ef6c00;">
        <div style="font-size:12px; color:#6b7280;">Critical (Float &lt; 0)</div>
        <div style="font-size:20px; font-weight:700; color:#ef6c00;">{critical}</div>
    </div>

</div>
""", unsafe_allow_html=True)

    # =========================
    # COLOUR FUNCTIONS
    # =========================
    def colour_delta(val):
        if val > 0:
            return "background-color:#fdecea; color:#b71c1c; font-weight:600"
        elif val < 0:
            return "background-color:#e8f5e9; color:#1b5e20"
        return ""

    def colour_float(val):
        if pd.notna(val):
            if val < 0:
                return "background-color:#ffcdd2; color:#b71c1c"
            elif val <= 5:
                return "background-color:#fff3e0; color:#ef6c00"
            else:
                return "background-color:#e8f5e9; color:#1b5e20"
        return ""

    def colour_progress(val):
        try:
            v = float(val.replace("%", ""))
            if v >= 80:
                return "background-color:#e8f5e9; color:#1b5e20"
            elif v >= 40:
                return "background-color:#fff3e0; color:#ef6c00"
            else:
                return "background-color:#fdecea; color:#b71c1c"
        except:
            return ""

    def stripe_rows(row):
        return [
            "background-color:#ffffff" if row.name % 2 == 0 else "background-color:#f7f9fc"
        ] * len(row)

    # =========================
    # STYLE TABLE
    # =========================
    styled = (
        display_df.style
        .apply(stripe_rows, axis=1)
        .map(colour_delta, subset=["Change (Days)"])
        .map(colour_float, subset=["Float"])
        .map(colour_progress, subset=["% Complete"])
    )

    # =========================
    # RENDER TABLE
    # =========================
    st.dataframe(styled, width="stretch")
``
import pandas as pd


# =========================
# DATA PREPARATION
# =========================
def _prepare(df):
    df = df.copy()
    df.columns = df.columns.astype(str).str.strip()

    df["Finish"] = pd.to_datetime(df["Finish"], errors="coerce")
