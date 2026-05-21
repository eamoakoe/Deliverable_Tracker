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

    df["Total Float"] = pd.to_numeric(df["Total Float"], errors="coerce")

    # Clean % complete
    df["Activity % Complete"] = (
        df["Activity % Complete"]
        .astype(str)
        .str.replace("%", "", regex=False)
    )

    df["Activity % Complete"] = pd.to_numeric(
        df["Activity % Complete"],
        errors="coerce"
    ).fillna(0)

    # ✅ Change (force integer)
    df["Change (days)"] = (
        (df["Finish"] - df["BL1 Finish"])
        .dt.days
        .fillna(0)
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

    return df.sort_values("Finish")


# =========================
# RENDER TABLE
# =========================
def render_next7days_table(df):

    st.markdown("### 📅 CL32 May Lookahead – Next 7 Days")
    st.caption("Baseline vs Forecast Finish (Clause 32 – May Programme)")

    df = _get_next7days(df)

    if df.empty:
        st.success("No activities issuing in the next 7 days 🎯")
        return

    # =========================
    # RENAME FOR CLARITY
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
        "Change (days)": "Change vs CL32 Baseline (days)"
    })

    # =========================
    # FORMAT DATES
    # =========================
    display_df["Baseline Finish (CL32 May)"] = \
        pd.to_datetime(display_df["Baseline Finish (CL32 May)"]).dt.strftime("%d-%b-%Y")

    display_df["Forecast Finish (CL32 May)"] = \
        pd.to_datetime(display_df["Forecast Finish (CL32 May)"]).dt.strftime("%d-%b-%Y")

    # =========================
    # STATUS
    # =========================
    def get_status(row):
        if row["Activity % Complete"] < 100 and row["Total Float"] <= 0:
            return "🔴 At Risk"
        elif row["Change vs CL32 Baseline (days)"] < 0:
            return "🟠 Late"
        else:
            return "🟢 OK"

    display_df["Status"] = display_df.apply(get_status, axis=1)

    # =========================
    # ML-LITE RISK INDICATOR
    # =========================
    def get_risk(row):
        if row["Activity % Complete"] < 100 and row["Total Float"] <= 0:
            return "🔴 High Risk"
        elif row["Activity % Complete"] < 75 and row["Change vs CL32 Baseline (days)"] < 0:
            return "🟠 Behind Progress"
        elif row["Activity % Complete"] >= 90 and row["Change vs CL32 Baseline (days)"] < 0:
            return "⚠️ Near Complete but Late"
        else:
            return "🟢 Low Risk"

    display_df["Risk"] = display_df.apply(get_risk, axis=1)

    # =========================
    # KPI SUMMARY
    # =========================
    total = len(display_df)
    late = (display_df["Change vs CL32 Baseline (days)"] < 0).sum()
    at_risk = (display_df["Status"] == "🔴 At Risk").sum()

    st.markdown(f"""
    **Next 7 Days Summary**
    - Total Activities: {total}
    - Late: {late}
    - At Risk: {at_risk}
    """)

    # =========================
    # COLOUR FUNCTIONS
    # =========================
    def colour_change(val):
        if val < 0:
            return "background-color:#7f1d1d; color:white; font-weight:bold"
        elif val > 0:
            return "background-color:#14532d; color:white; font-weight:bold"
        else:
            return "background-color:#374151; color:white"

    def colour_float(val):
        if pd.isna(val):
            return ""
        if val <= 0:
            return "background-color:#b00020; color:white"
        return ""

    def colour_status(val):
        if "🔴" in val:
            return "background-color:#b00020; color:white; font-weight:bold"
        elif "🟠" in val:
            return "background-color:#ff9800; color:black; font-weight:bold"
        elif "🟢" in val:
            return "background-color:#1e7e34; color:white; font-weight:bold"
        return ""

    def colour_risk(val):
        if "🔴" in val:
            return "background-color:#7f1d1d; color:white"
        elif "🟠" in val:
            return "background-color:#ff9800; color:black"
        elif "⚠️" in val:
            return "background-color:#facc15; color:black"
        elif "🟢" in val:
            return "background-color:#14532d; color:white"
        return ""

    # =========================
    # STYLE TABLE
    # =========================
    styled = display_df.style.set_table_styles([
        {
            "selector": "th",
            "props": [
                ("background-color", "#2b3a55"),
                ("color", "white"),
                ("font-size", "13px"),
                ("font-weight", "600"),
                ("text-transform", "uppercase"),
                ("padding", "10px"),
                ("border-bottom", "2px solid #4da3ff"),
                ("text-align", "left")
            ]
        },
        {
            "selector": "td",
            "props": [
                ("padding", "8px"),
                ("background-color", "#1c2233"),
                ("color", "#f1f1f1"),
                ("border-bottom", "1px solid #2a3347"),
                ("border-right", "1px solid #2a3347")
            ]
        }
    ])

    # Apply colours
    styled = styled.map(colour_change, subset=["Change vs CL32 Baseline (days)"])
    styled = styled.map(colour_float, subset=["Total Float"])
    styled = styled.map(colour_status, subset=["Status"])
    styled = styled.map(colour_risk, subset=["Risk"])

    st.write(styled)