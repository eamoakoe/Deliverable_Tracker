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
# LOOKAHEAD LOGIC (NEXT 4 WEEKS)
# =========================
def _get_next4weeks(df):
    df = _prepare(df)

    today = pd.Timestamp.today().normalize()
    lookahead = today + pd.Timedelta(days=28)

    next4weeks = df[
        (df["Start"].notna()) &
        (df["Finish"].notna()) &
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
    # CLEAN COLUMN NAMES
    # =========================
    display_df.rename(columns={
        "Activity ID": "ID",
        "Activity Name": "Activity",
        "Start": "Start Date",
        "Finish": "Finish Date",
        "Comments": "Remarks"
    }, inplace=True)

    # =========================
    # FORMAT DATES
    # =========================
    display_df["Start Date"] = display_df["Start Date"].dt.strftime("%d-%b-%Y")
    display_df["Finish Date"] = display_df["Finish Date"].dt.strftime("%d-%b-%Y")

    # =========================
    # FORECAST TAG
    # =========================
    display_df["Window"] = "4-Week Lookahead"

    # =========================
    # COLOUR FUNCTION
    # =========================
    def colour_window(val):
        return "background-color:#e3f2fd; color:#0d47a1; font-weight:600"

    # =========================
    # ROW STRIPES (LIGHT)
    # =========================
    def stripe_rows(row):
        return [
            "background-color:#ffffff" if row.name % 2 == 0 else "background-color:#f7f9fc"
        ] * len(row)

    # =========================
    # PROFESSIONAL TABLE STYLE
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
                    ("letter-spacing", "0.6px"),
                    ("padding", "10px 8px"),
                    ("border-bottom", "3px solid #3b82f6"),
                ]
            },
            {
                "selector": "td",
                "props": [
                    ("padding", "8px"),
                    ("color", "#1f2a44"),
                    ("border-bottom", "1px solid #e5e7eb")
                ]
            },
            {
                "selector": "table",
                "props": [
                    ("border-collapse", "collapse"),
                    ("width", "100%"),
                    ("background-color", "white"),
                    ("border-radius", "8px"),
                    ("overflow", "hidden"),
                    ("box-shadow", "0 1px 3px rgba(0,0,0,0.08)")
                ]
            }
        ])

        # Striping
        .apply(stripe_rows, axis=1)

        # Highlight window column
        .map(colour_window, subset=["Window"])

        # Alignment
        .set_properties(subset=["ID", "Activity", "Remarks"], **{"text-align": "left"})
        .set_properties(subset=["Start Date", "Finish Date"], **{"text-align": "center"})
    )

    # =========================
    # KPI
    # =========================
    st.markdown(
        f"<span style='color:#1e88e5;font-weight:600;font-size:15px'>🟢 {len(display_df)} Activities in Lookahead</span>",
        unsafe_allow_html=True
    )

    # =========================
    # RENDER
    # =========================
    st.write(styled)
