import streamlit as st
import pandas as pd


# =========================
# DATA PREPARATION
# =========================
def _prepare(df):
    df = df.copy()

    # Clean column names
    df.columns = df.columns.astype(str).str.strip()

    # Convert dates
    df["Start"] = pd.to_datetime(df["Start"], errors="coerce")
    df["Finish"] = pd.to_datetime(df["Finish"], errors="coerce")

    # Clean percentage
    df["Activity % Complete"] = (
        df["Activity % Complete"]
        .astype(str)
        .str.replace("%", "", regex=False)
    )

    df["Activity % Complete"] = pd.to_numeric(
        df["Activity % Complete"], errors="coerce"
    ).fillna(0)

    return df


# =========================
# DELAY LOGIC (ALIGNED WITH PIE)
# =========================
def _get_delayed(df):
    df = _prepare(df)

    # Remove time component (IMPORTANT)
    today = pd.Timestamp.today().normalize()

    delayed = df[
        (df["Finish"].notna()) &
        (df["Finish"] < today) &
        (df["Activity % Complete"] < 100)
    ].copy()

    delayed["Delay (Days)"] = (today - delayed["Finish"]).dt.days

    return delayed.sort_values("Delay (Days)", ascending=False)


# =========================
# RENDER TABLE
# =========================
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
    # FORMAT DATA
    # =========================
    display_df["Start"] = display_df["Start"].dt.strftime("%d-%b-%Y")
    display_df["Finish"] = display_df["Finish"].dt.strftime("%d-%b-%Y")

    # =========================
    # COLOUR FUNCTION
    # =========================
    def colour_delay(val):
        try:
            v = float(val)

            if v >= 50:
                return "background-color:#7f0000; color:white; font-weight:600"
            elif v >= 30:
                return "background-color:#b30000; color:white; font-weight:600"
            elif v >= 15:
                return "background-color:#e68a00; color:black; font-weight:600"
            else:
                return "background-color:#999900; color:black; font-weight:600"
        except:
            return ""

    # =========================
    # ROW STRIPES
    # =========================
    def stripe_rows(row):
        return [
            "background-color:#20283a" if row.name % 2 == 0 else "background-color:#1c2233"
        ] * len(row)

    # =========================
    # TABLE STYLE
    # =========================
    styled = (
        display_df.style

        # Header styling
        .set_table_styles([
            {
                "selector": "th",
                "props": [
                    ("background-color", "#2f3e5a"),
                    ("color", "white"),
                    ("font-size", "12px"),
                    ("font-weight", "700"),
                    ("text-transform", "uppercase"),
                    ("letter-spacing", "0.5px"),
                    ("padding", "10px"),
                    ("border-bottom", "2px solid #4da3ff"),
                    ("text-align", "left")
                ]
            },
            {
                "selector": "td",
                "props": [
                    ("padding", "8px"),
                    ("color", "#f5f7fb"),
                    ("border-bottom", "1px solid #2a3347")
                ]
            },
            {
                "selector": "table",
                "props": [
                    ("border-collapse", "collapse"),
                    ("width", "100%"),
                    ("border-radius", "10px"),
                    ("overflow", "hidden")
                ]
            }
        ])

        # Alternate row shading
        .apply(stripe_rows, axis=1)

        # Colour delay column
        .map(colour_delay, subset=["Delay (Days)"])

        # Align delay values
        .set_properties(subset=["Delay (Days)"], **{
            "text-align": "center",
            "font-size": "13px"
        })

        # Emphasise activity name
        .set_properties(subset=["Activity Name"], **{
            "font-weight": "500"
        })
    )

    # =========================
    # OPTIONAL SUMMARY KPI
    # =========================
    st.markdown(f"**🔴 {len(display_df)} Delayed Activities**")

    # =========================
    # RENDER TABLE
    # =========================
    st.write(styled)
