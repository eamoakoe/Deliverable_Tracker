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

    # ✅ FLOAT → whole number
    df["Total Float"] = (
        pd.to_numeric(df["Total Float"], errors="coerce")
        .fillna(0)
        .round(0)
        .astype(int)
    )

    # ✅ % COMPLETE → whole number
    df["Activity % Complete"] = (
        df["Activity % Complete"]
        .astype(str)
        .str.replace("%", "", regex=False)
    )

    df["Activity % Complete"] = (
        pd.to_numeric(df["Activity % Complete"], errors="coerce")
        .fillna(0)
        .round(0)
        .astype(int)
    )

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
        (df["Finish"] <= lookahead) &
        (df["Activity % Complete"] < 100)   # ✅ remove completed
    ].copy()

    return df.sort_values("Finish")


# =========================
# MAIN RENDER
# =========================
def render_next7days_table(df):

    df = _get_next7days(df)

    if df.empty:
        st.success("✅ No activities issuing in the next 7 days")
        return

    # =========================
    # TABLE
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

    # ✅ KEEP YOUR FULL LABELS (they will wrap now)
    display_df = display_df.rename(columns={
        "BL1 Finish": "Baseline Finish (CL32 May)",
        "Finish": "Forecast Finish (CL32 May)",
        "Change (days)": "Δ Change vs CL32 May (days)",
        "Total Float": "Float (Days)",
        "Activity % Complete": "% Complete"
    })

    # =========================
    # FORMAT DATES
    # =========================
    display_df["Baseline Finish (CL32 May)"] = \
        pd.to_datetime(display_df["Baseline Finish (CL32 May)"]).dt.strftime("%d-%b-%Y")

    display_df["Forecast Finish (CL32 May)"] = \
        pd.to_datetime(display_df["Forecast Finish (CL32 May)"]).dt.strftime("%d-%b-%Y")

    # ✅ optional: show % sign (clean)
    display_df["% Complete"] = display_df["% Complete"].astype(str) + "%"

    # =========================
    # STYLING (NO SCROLL ✅)
    # =========================
    styled = display_df.style.set_table_styles([

        # ✅ HEADERS WRAP
        {
            "selector": "th",
            "props": [
                ("background-color", "#2b3a55"),
                ("color", "white"),
                ("font-weight", "600"),
                ("padding", "8px"),
                ("font-size", "12px"),
                ("white-space", "normal"),   # ✅ enables multi-line
                ("line-height", "1.2"),
                ("text-align", "center")
            ]
        },

        # ✅ CELLS WRAP
        {
            "selector": "td",
            "props": [
                ("background-color", "#1c2233"),
                ("color", "#f1f1f1"),
                ("padding", "6px"),
                ("font-size", "12px"),
                ("white-space", "normal"),
                ("word-wrap", "break-word"),
                ("max-width", "160px")   # ✅ prevents expansion
            ]
        },

        # ✅ FORCE TABLE FIT WIDTH
        {
            "selector": "table",
            "props": [
                ("width", "100%"),
                ("table-layout", "fixed")   # ✅ CRITICAL (removes scrollbar)
            ]
        }
    ])

    # ✅ Render properly (keeps layout)
    st.markdown(styled.to_html(), unsafe_allow_html=True)
