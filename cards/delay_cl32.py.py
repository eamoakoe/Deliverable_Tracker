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


def _get_delayed(df):
    df = _prepare(df)
    today = pd.Timestamp.today()

    delayed = df[
        (df["Finish"] < today) &
        (df["Activity % Complete"] < 100)
    ].copy()

    delayed["Delay (Days)"] = (today - delayed["Finish"]).dt.days

    return delayed.sort_values("Delay (Days)", ascending=False)


def render_delayed_table(df):

    delayed = _get_delayed(df)

    if delayed.empty:
        st.success("No delayed activities 🎯")
        return

    display_df = delayed[[
        "Activity ID",
        "Activity Name",
        "Start",
        "Finish",
        "Delay (Days)",
        "Comments"
    ]].copy()

    # =========================
    # DISPLAY FORMATTING ONLY
    # =========================
    display_df["Start"] = display_df["Start"].dt.strftime("%d-%b-%Y")
    display_df["Finish"] = display_df["Finish"].dt.strftime("%d-%b-%Y")


    # =========================
    # COLOUR FUNCTION (DELAY ONLY)
    # =========================
    def colour_delay(val):
        try:
            v = float(val)

            if v >= 50:
                return "background-color:#5a0000; color:white; font-weight:bold"
            elif v >= 30:
                return "background-color:#8b1e1e; color:white; font-weight:bold"
            elif v >= 15:
                return "background-color:#a66a00; color:white; font-weight:bold"
            else:
                return "background-color:#4a4a00; color:white; font-weight:bold"
        except:
            return ""


    # =========================
    # APPLY STYLING (SAFE FOR NEW PANDAS)
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
    # APPLY COLOUR ONLY TO "Delay (Days)"
    # (FIXED: uses map, not applymap)
    # =========================
    styled = styled.map(colour_delay, subset=["Delay (Days)"])

    # =========================
    # RENDER THIS TABLE ONLY
    # =========================
    st.write(styled)