import streamlit as st
import pandas as pd


# =========================
# DATA PREPARATION
# =========================
def _prepare(df):
    df = df.copy()

    df.columns = df.columns.astype(str).str.strip()

    df["Start"] = pd.to_datetime(df["Start"], errors="coerce")
    df["Finish"] = pd.to_datetime(df["Finish"], errors="coerce")
    df["BL1 Finish"] = pd.to_datetime(df.get("BL1 Finish"), errors="coerce")

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
# ✅ FORECAST LOGIC (NEXT 7 DAYS)
# =========================
def _get_next7days(df):
    df = _prepare(df)

    today = pd.Timestamp.today().normalize()
    lookahead = today + pd.Timedelta(days=7)

    upcoming = df[
        (df["Start"].notna()) &
        (df["Finish"].notna()) &
        (df["Start"] <= lookahead) &
        (df["Finish"] >= today)
    ].copy()

    # ✅ Add Delta vs BL1 Finish
    if "BL1 Finish" in upcoming.columns:
        upcoming["Delta (Days)"] = (
            upcoming["Finish"] - upcoming["BL1 Finish"]
        ).dt.days

    return upcoming.sort_values("Start", ascending=True)


# =========================
# RENDER TABLE
# =========================
def render_next7days_table(df):

    upcoming = _get_next7days(df)

    if upcoming.empty:
        st.success("No activities in the next 7 days 🎯")
        return

    display_df = upcoming[[
        "Activity ID",
        "Activity Name",
        "Start",
        "Finish",
        "BL1 Finish",
        "Delta (Days)",
        "Comments"
    ]].copy()

    # =========================
    # CLEAN COLUMN NAMES
    # =========================
    display_df.rename(columns={
        "Activity ID": "ID",
        "Activity Name": "Activity",
        "Start": "Start Date",
        "Finish": "Forecast Finish",
        "BL1 Finish": "Baseline Finish",
        "Comments": "Remarks"
    }, inplace=True)

    # =========================
    # FORMAT DATES
    # =========================
    display_df["Start Date"] = display_df["Start Date"].dt.strftime("%d-%b-%Y")
    display_df["Forecast Finish"] = display_df["Forecast Finish"].dt.strftime("%d-%b-%Y")
    display_df["Baseline Finish"] = display_df["Baseline Finish"].dt.strftime("%d-%b-%Y")

    # =========================
    # DELTA COLOUR
    # =========================
    def colour_delta(val):
        try:
            v = float(val)

            if v > 0:
                return "background-color:#fdecea; color:#b71c1c; font-weight:600"
            elif v < 0:
                return "background-color:#e8f5e9; color:#1b5e20; font-weight:600"
            else:
                return "background-color:#e3f2fd; color:#0d47a1; font-weight:600"
        except:
            return ""

    # =========================
    # ROW STRIPES
    # =========================
    def stripe_rows(row):
        return [
            "background-color:#ffffff" if row.name % 2 == 0 else "background-color:#f7f9fc"
        ] * len(row)

    # =========================
    # STYLE
    # =========================
    styled = (
        display_df.style

        .set_table_styles([
            {
                "selector": "th",
                "props": [
                    ("background-color", "#1e3a8a"),
                    ("color", "white"),
                    ("font-size", "12.5px"),
                    ("font-weight", "700"),
                    ("text-transform", "uppercase"),
                    ("padding", "10px 8px"),
                    ("border-bottom", "3px solid #3b82f6")
                ]
            },
            {
                "selector": "td",
                "props": [
                    ("padding", "8px"),
                    ("color", "#1f2a44"),
                    ("border-bottom", "1px solid #e5e7eb")
                ]
            }
        ])

        .apply(stripe_rows, axis=1)
        .map(colour_delta, subset=["Delta (Days)"])
    )

    # =========================
    # KPI
    # =========================
    delay_count = (display_df["Delta (Days)"] > 0).sum()
    total = len(display_df)

    st.markdown(
        f"""
        <span style='font-weight:600'>
            🔴 {delay_count} Behind Plan &nbsp;|&nbsp; 🟢 {total - delay_count} On/ Ahead
        </span>
        """,
        unsafe_allow_html=True
    )

    # =========================
    # RENDER
    # =========================
    st.dataframe(styled, use_container_width=True)
