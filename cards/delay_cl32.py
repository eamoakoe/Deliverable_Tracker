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
# DELAY LOGIC
# =========================
def _get_delayed(df):
    df = _prepare(df)

    # Normalize date to match pie logic
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
    # FORMAT DATES
    # =========================
    display_df["Start"] = display_df["Start"].dt.strftime("%d-%b-%Y")
    display_df["Finish"] = display_df["Finish"].dt.strftime("%d-%b-%Y")

    # =========================
    # DELAY COLOUR (CLEAR & BRIGHT)
    # =========================
    def colour_delay(val):
        try:
            v = float(val)

            if v >= 50:
                return "background-color:#d32f2f; color:white; font-weight:600"
            elif v >= 30:
                return "background-color:#f57c00; color:black; font-weight:600"
            elif v >= 15:
                return "background-color:#fbc02d; color:black; font-weight:600"
            else:
                return "background-color:#cddc39; color:black; font-weight:600"
        except:
            return ""

    # =========================
    # ROW STRIPING (READABLE)
    # =========================
    def stripe_rows(row):
        return [
            "background-color:#2a2f3a" if row.name % 2 == 0 else "background-color:#343a46"
        ] * len(row)

    # =========================
    # PROFESSIONAL TABLE STYLE
    # =========================
    styled = (
        display_df.style

        # Header
        .set_table_styles([
            {
                "selector": "th",
                "props": [
                    ("background-color", "#4a6fa5"),
                    ("color", "white"),
                    ("font-size", "13px"),
                    ("font-weight", "700"),
                    ("padding", "10px"),
                    ("border-bottom", "2px solid #90caf9"),
                    ("text-align", "left")
                ]
            },
            {
                "selector": "td",
                "props": [
                    ("padding", "8px"),
                    ("color", "#f1f3f6"),
                    ("border-bottom", "1px solid #555a66")
                ]
            },
            {
                "selector": "table",
                "props": [
                    ("border-collapse", "collapse"),
                    ("width", "100%"),
                    ("background-color", "#2f3542"),
                    ("border-radius", "8px"),
                    ("overflow", "hidden")
                ]
            }
        ])

        # Stripe rows
        .apply(stripe_rows, axis=1)

        # Highlight delay column
        .map(colour_delay, subset=["Delay (Days)"])

        # Align delay column
        .set_properties(subset=["Delay (Days)"], **{
            "text-align": "center",
            "font-weight": "600"
        })

        # Emphasise activity names
        .set_properties(subset=["Activity Name"], **{
            "font-weight": "500"
        })
    )

    # =========================
    # KPI ABOVE TABLE
    # =========================
    st.markdown(
        f"<span style='color:#ff6b6b;font-weight:600'>🔴 {len(display_df)} Delayed Activities</span>",
        unsafe_allow_html=True
    )

    # =========================
    # RENDER
    # =========================
    st.write(styled)