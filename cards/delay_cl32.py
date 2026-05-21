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

    return df


# =========================
# KEYWORD MAP (EDITABLE)
# =========================
MILESTONE_KEYWORDS = {
    "Design Freeze": ["BIM Execution Plan", "Freeze"],
    "Design Submission": ["Submission", "Outline Design Pack"],
    "Client Review": ["Client Review"],
    "Final Submission": ["Final Submission"]
}


# =========================
# EXTRACT MILESTONES
# =========================
def extract_milestones(df):

    df = _prepare(df)

    milestones = []

    for milestone_name, keywords in MILESTONE_KEYWORDS.items():

        mask = df["Activity Name"].str.contains(
            "|".join(keywords),
            case=False,
            na=False
        )

        filtered = df[mask]

        if filtered.empty:
            continue

        # ✅ take first match (avoids duplicates)
        row = filtered.iloc[0]

        if pd.notna(row["Finish"]) and pd.notna(row["BL1 Finish"]):
            delta = int((row["Finish"] - row["BL1 Finish"]).days)
        else:
            delta = None

        milestones.append({
            "Milestone": milestone_name,
            "Baseline Finish (CL32 May)": row["BL1 Finish"],
            "Forecast Finish": row["Finish"],
            "Δ (Days)": delta
        })

    ms_df = pd.DataFrame(milestones)

    return ms_df


# =========================
# RENDER TABLE
# =========================
def render_milestone_table(df):

    ms_df = extract_milestones(df)

    st.markdown("### 🎯 Key Milestone Tracking – CL32 May")

    if ms_df.empty:
        st.info("No milestones identified")
        return

    # =========================
    # FORMAT DATES
    # =========================
    ms_df["Baseline Finish (CL32 May)"] = pd.to_datetime(
        ms_df["Baseline Finish (CL32 May)"]
    ).dt.strftime("%d-%b-%Y")

    ms_df["Forecast Finish"] = pd.to_datetime(
        ms_df["Forecast Finish"]
    ).dt.strftime("%d-%b-%Y")

    # =========================
    # COLOUR DELTA
    # =========================
    def colour_delta(val):
        if val is None:
            return ""
        if val < 0:
            return "background-color:#7f1d1d;color:white;font-weight:bold"
        elif val > 0:
            return "background-color:#14532d;color:white;font-weight:bold"
        return "background-color:#374151;color:white"

    styled = ms_df.style.map(
        colour_delta,
        subset=["Δ (Days)"]
    ).set_table_styles([
        {
            "selector": "th",
            "props": [
                ("background-color", "#2b3a55"),
                ("color", "white"),
                ("padding", "10px"),
                ("font-weight", "600")
            ]
        },
        {
            "selector": "td",
            "props": [
                ("background-color", "#1c2233"),
                ("color", "#f1f1f1"),
                ("padding", "8px")
            ]
        }
    ])

    st.write(styled)