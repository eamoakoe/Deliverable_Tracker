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
        st.success("No delayed deliverables 🎯")
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
    # CLEAN COLUMN NAMES (PRO LOOK)
    # =========================
    display_df.rename(columns={
        "Activity ID": "ID",
        "Activity Name": "Activity",
        "Start": "Start Date",
        "Finish": "Finish Date",
        "Delay (Days)": "Delay (Days)",
        "Comments": "Remarks"
    }, inplace=True)

    # =========================
    # FORMAT DATES
    # =========================
    display_df["Start Date"] = display_df["Start Date"].dt.strftime("%d-%b-%Y")
    display_df["Finish Date"] = display_df["Finish Date"].dt.strftime("%d-%b-%Y")

    # =========================
    # DELAY COLOUR SCALE
    # =========================
    def colour_delay(val):
        try:
            v = float(val)

            if v >= 50:
                return "background-color:#d32f2f; color:white; font-weight:600"
            elif v >= 30:
                return "background-color:#f57c00; color:white; font-weight:600"
            elif v >= 15:
                return "background-color:#fbc02d; color:black; font-weight:600"
            else:
                return "background-color:#c8e6c9; color:black; font-weight:600"
        except:
            return ""

    # =========================
    # ROW STRIPING
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

        # Stripe rows
        .apply(stripe_rows, axis=1)

        # Colour delay column
        .map(colour_delay, subset=["Delay (Days)"])

        # Align columns
        .set_properties(subset=["ID", "Activity", "Remarks"], **{
            "text-align": "left"
        })
        .set_properties(subset=["Start Date", "Finish Date"], **{
            "text-align": "center"
        })
        .set_properties(subset=["Delay (Days)"], **{
            "text-align": "center",
            "font-weight": "600"
        })
    )

    # =========================
    # KPI SUMMARY
    # =========================
    st.markdown(
        f"<span style='color:#d32f2f;font-weight:600;font-size:15px'>🔴 {len(display_df)} Delayed Activities</span>",
        unsafe_allow_html=True
    )

    # =========================
    # RENDER
    # =========================
    st.write(styled)