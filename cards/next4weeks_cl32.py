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

    df["Total Float"] = pd.to_numeric(
        df.get("Total Float"),
        errors="coerce"
    )

    return df


# =========================
# ✅ ISSUE FORECAST (NEXT 7 DAYS)
# =========================
def _get_next4weeks(df):  # name unchanged
    df = _prepare(df)

    today = pd.Timestamp.today().normalize()
    lookahead = today + pd.Timedelta(days=7)

    # ✅ Deliverables being issued in next 7 days
    upcoming = df[
        (df["Finish"].notna()) &
        (df["Finish"] >= today) &
        (df["Finish"] <= lookahead)
    ].copy()

    # ✅ Delta: Forecast vs Baseline
    upcoming["Change (Days)"] = (
        upcoming["Finish"] - upcoming["BL1 Finish"]
    ).dt.days

    return upcoming.sort_values("Finish")


# =========================
# RENDER TABLE
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
        "Total Float"
    ]].copy()

    # =========================
    # CLEAN HEADERS
    # =========================
    display_df.rename(columns={
        "Activity ID": "ID",
        "Activity Name": "Activity",
        "BL1 Finish": "Baseline Finish",
        "Finish": "Forecast Finish",
        "Total Float": "Float"
    }, inplace=True)

    # =========================
    # FORMAT DATES
    # =========================
    display_df["Baseline Finish"] = display_df["Baseline Finish"].dt.strftime("%d-%b-%Y")
    display_df["Forecast Finish"] = display_df["Forecast Finish"].dt.strftime("%d-%b-%Y")

    # =========================
    # COLOUR LOGIC
    # =========================
    def colour_delta(val):
        try:
            if val > 0:
                return "background-color:#fdecea; color:#b71c1c; font-weight:600"
            elif val < 0:
                return "background-color:#e8f5e9; color:#1b5e20; font-weight:600"
            else:
                return "background-color:#e3f2fd; color:#0d47a1"
        except:
            return ""

    def colour_float(val):
        try:
            if val < 0:
                return "background-color:#ffcdd2; color:#b71c1c; font-weight:600"
            elif val <= 5:
                return "background-color:#fff3e0; color:#ef6c00"
            else:
                return "background-color:#e8f5e9; color:#1b5e20"
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

        .apply(stripe_rows, axis=1)
        .map(colour_delta, subset=["Change (Days)"])
        .map(colour_float, subset=["Float"])
    )

    # =========================
    # KPI (CORE VALUE)
    # =========================
    total = len(display_df)
    behind = (display_df["Change (Days)"] > 0).sum()
    critical = (display_df["Float"] < 0).sum()

    st.markdown(
        f"""
        <span style='font-weight:600'>
            📦 {total} Deliverables This Week &nbsp;&nbsp;|&nbsp;&nbsp;
            🔴 {behind} Behind Plan &nbsp;&nbsp;|&nbsp;&nbsp;
            ⚠ {critical} Critical (Neg Float)
        </span>
        """,
        unsafe_allow_html=True
    )

    # =========================
    # RENDER
    # =========================
    st.dataframe(styled, use_container_width=True)
``