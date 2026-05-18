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
