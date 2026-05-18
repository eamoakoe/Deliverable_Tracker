import streamlit as st
import pandas as pd


def _prepare(df):
    df = df.copy()

    df.columns = df.columns.astype(str).str.strip()

    df["Start"] = pd.to_datetime(df["Start"], errors="coerce")
    df["Finish"] = pd.to_datetime(df["Finish"], errors="coerce")

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
# LOOKAHEAD LOGIC (NEXT 4 WEEKS)
# =========================
def _get_next4weeks(df):
    df = _prepare(df)

    today = pd.Timestamp.today()
    lookahead = today + pd.Timedelta(days=28)

    # Activities that overlap next 4-week window
    next4weeks = df[
        (df["Start"] <= lookahead) &
        (df["Finish"] >= today)
    ].copy()

    return next4weeks.sort_values("Start", ascending=True)


# =========================
# RENDER TABLE
# =========================
def render_next4weeks_table(df):

    upcoming = _get_next4weeks(df)

    if upcoming.empty:
        st.success("No activities in the next 4 weeks 🎯")
        return

    display_df = upcoming[[
        "Activity ID",
        "Activity Name",
        "Start",
        "Finish",
        "Comments"
    ]].copy()

    # =========================
    # DISPLAY FORMATTING ONLY
    # =========================
    display_df["Start"] = display_df["Start"].dt.strftime("%d-%b-%Y")
    display_df["Finish"] = display_df["Finish"].dt.strftime("%d-%b-%Y")

    # =========================
    # CONSTRAINT COLUMN (SIMPLE FORECAST LABEL)
    # =========================
    display_df["Constraints"] = "Within 4-week window"


    # =========================
    # COLOUR FUNCTION (CONSTRAINT ONLY)
    # =========================
    def colour_constraints(val):
        if "Within" in str(val):
            return "background-color:#1e4d2b; color:white; font-weight:bold"
        return ""


    # =========================
    # TABLE STYLING (SAME STYLE AS delay_cl32.py)
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
                ("letter-spacing", "1px"),
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
    # APPLY COLOUR ONLY TO CONSTRAINTS COLUMN
    # =========================
    styled = styled.map(colour_constraints, subset=["Constraints"])

    # =========================
    # RENDER
    # =========================
    st.write(styled)