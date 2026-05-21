import streamlit as st
import pandas as pd


def _prepare(df):
    df = df.copy()

    df.columns = df.columns.astype(str).str.strip()

    df["Start"] = pd.to_datetime(df["Start"], errors="coerce")
    df["Finish"] = pd.to_datetime(df["Finish"], errors="coerce")
    df["BL1 Finish"] = pd.to_datetime(df["BL1 Finish"], errors="coerce")

    df["Total Float"] = pd.to_numeric(df["Total Float"], errors="coerce")

    df["Activity % Complete"] = (
        df["Activity % Complete"]
        .astype(str)
        .str.replace("%", "", regex=False)
    )

    df["Activity % Complete"] = pd.to_numeric(
        df["Activity % Complete"],
        errors="coerce"
    ).fillna(0)

    # 🔹 Calculate change (Forecast vs Baseline)
    df["Change (days)"] = (df["Finish"] - df["BL1 Finish"]).dt.days

    return df


# =========================
# LOOKAHEAD (NEXT 7 DAYS)
# =========================
def _get_next7days(df):
    df = _prepare(df)

    today = pd.Timestamp.today().normalize()
    lookahead = today + pd.Timedelta(days=7)

    next7 = df[
        (df["Finish"] >= today) &
        (df["Finish"] <= lookahead)
    ].copy()

    return next7.sort_values("Finish", ascending=True)


# =========================
# RENDER TABLE
# =========================
def render_next7days_table(df):

    upcoming = _get_next7days(df)

    if upcoming.empty:
        st.success("No activities issuing in the next 7 days 🎯")
        return

    display_df = upcoming[[
        "Activity ID",
        "Activity Name",
        "BL1 Finish",
        "Finish",
        "Change (days)",
        "Total Float",
        "Activity % Complete",
        "Comments"
    ]].copy()

    # =========================
    # FORMAT DATES
    # =========================
    display_df["BL1 Finish"] = display_df["BL1 Finish"].dt.strftime("%d-%b-%Y")
    display_df["Finish"] = display_df["Finish"].dt.strftime("%d-%b-%Y")

    # =========================
    # STATUS COLUMN (SMART ADD)
    # =========================
    def get_status(row):
        if row["Activity % Complete"] < 100 and row["Total Float"] <= 0:
            return "🔴 At Risk"
        elif row["Change (days)"] < 0:
            return "🟠 Late"
        else:
            return "🟢 OK"

    display_df["Status"] = display_df.apply(get_status, axis=1)

    # =========================
    # COLOUR FUNCTIONS
    # =========================
    def colour_status(val):
        if "🔴" in str(val):
            return "background-color:#b00020; color:white; font-weight:bold"
        elif "🟠" in str(val):
            return "background-color:#ff9800; color:black; font-weight:bold"
        elif "🟢" in str(val):
            return "background-color:#1e7e34; color:white; font-weight:bold"
        return ""

    def colour_change(val):
        if pd.isna(val):
            return ""
        if val < 0:
            return "background-color:#5c1f1f; color:white"
        elif val > 0:
            return "background-color:#1f5c2e; color:white"
        return ""

    def colour_float(val):
        if pd.isna(val):
            return ""
        if val <= 0:
            return "background-color:#b00020; color:white"
        return ""

    # =========================
    # TABLE STYLING
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
        },
        {
            "selector": "table",
            "props": [
                ("border-collapse", "collapse"),
                ("width", "100%"),
                ("background-color", "#1c2233")
            ]
        }
    ])

    # =========================
    # APPLY COLOURS
    # =========================
    styled = styled.map(colour_status, subset=["Status"])
    styled = styled.map(colour_change, subset=["Change (days)"])
    styled = styled.map(colour_float, subset=["Total Float"])

    # =========================
    # RENDER
    # =========================
    st.write(styled)