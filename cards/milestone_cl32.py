import streamlit as st
import pandas as pd


# =========================
# PREP DATA
# =========================
def _prepare(df):
    df = df.copy()
    df.columns = df.columns.astype(str).str.strip()

    df["Finish"] = pd.to_datetime(df["Finish"], errors="coerce")
    df["BL1 Finish"] = pd.to_datetime(df["BL1 Finish"], errors="coerce")

    return df


# =========================
# MILESTONE KEYWORDS
# =========================
MILESTONE_KEYWORDS = {
    "Design Freeze": ["BIM Execution Plan"],
    "GDR": ["GDR"],
    "Client Review (GDR)": ["Client Review of GDR"],
    "Client Review (Design Pack)": ["Client Review of Design Pack"],
    "Outline Design Submission": ["Submission of Outline Design Pack"],
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

        # ✅ take first match only
        row = filtered.iloc[0]

        # ✅ Calculate Δ (whole number only)
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

    if not ms_df.empty:
        ms_df["Δ (Days)"] = ms_df["Δ (Days)"].fillna(0).astype(int)

    return ms_df


# =========================
# RENDER TABLE
# =========================
def render_milestone_table(df):

    ms_df = extract_milestones(df)

    st.markdown("## 🎯 KEY MILESTONE TRACKING – CL32 MAY")

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
    # COLOUR Δ COLUMN
    # =========================
    def colour_delta(val):
        if val < 0:
            return "background-color:#7f1d1d;color:white;font-weight:bold"   # delayed
        elif val > 0:
            return "background-color:#14532d;color:white;font-weight:bold"   # early
        return "background-color:#374151;color:white"  # on baseline

    styled = ms_df.style.map(
        colour_delta,
        subset=["Δ (Days)"]
    ).set_table_styles([
        {
            "selector": "th",
            "props": [
                ("background-color", "#2b3a55"),
                ("color", "white"),
                ("font-weight", "600"),
                ("padding", "10px"),
                ("text-transform", "uppercase")
            ]
        },
        {
            "selector": "td",
            "props": [
                ("background-color", "#1c2233"),
                ("color", "#f1f1f1"),
                ("padding", "8px")
            ]
        },
        {
            "selector": "table",
            "props": [
                ("width", "100%"),
                ("border-collapse", "collapse")
            ]
        }
    ])

    st.write(styled)
