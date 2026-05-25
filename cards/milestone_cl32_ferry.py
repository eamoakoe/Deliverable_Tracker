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
# FERRY DELIVERABLE MAP
# =========================
FERRY_DELIVERABLES = {
    # 🔴 Programme level
    "Concept Design Submission": ["FER-PD-1000"],
    "Outline Design Scope Freeze": ["FER-PD-1010"],
    "Full Outline Design Submission": ["FER-PD-1020"],
    "Project Completion": ["FER-PD-1030"],

    # 🟠 Client submission / approvals
    "Outline Design Pack Submission": ["FER-REV-1000"],
    "Client Review Complete (Outline)": ["FER-REV-1010"],
    "Detailed Design Submission": ["FER-REV-1020"],
    "Client Review Complete (Detailed)": ["FER-REV-1030"],
    "Final Submission": ["FER-REV-1050"],

    # 🟡 Key reports / governance
    "Geotechnical Report (GDR)": ["FER-GEO-1010"],
    "HAZOP Complete": ["FER-PRO-1030"],
    "HAZOP Closeout": ["FER-PRO-1040"],

    # 🟡 Concept design outputs
    "Concept Drawing Issue": ["FER-CSD-1060"],
    "Pile Design Complete": ["FER-CSD-1070"],
    "CAT2 Check Complete": ["FER-CSD-1080"],

    # 🔵 Civils deliverables
    "Civils Key Drawings": [
        "FER-CIV-1020",
        "FER-CIV-1050"
    ],
    "Civils Detailed Design": [
        "FER-CIV-1070",
        "FER-CIV-1110",
        "FER-CIV-1150"
    ],

    # 🟣 Mechanical deliverables
    "Mechanical Design Pack": [
        "FER-MEC-1020",
        "FER-MEC-1030",
        "FER-MEC-1040",
        "FER-MEC-1050"
    ],
    "Mechanical Drawings Issue": [
        "FER-MEC-1060",
        "FER-MEC-1070",
        "FER-MEC-1080",
        "FER-MEC-1090",
        "FER-MEC-1100",
        "FER-MEC-1110"
    ],

    # 🟤 Process deliverables
    "Process Design Pack": [
        "FER-PRO-1010",
        "FER-PRO-1000",
        "FER-PRO-1020"
    ],

    # 🟢 EICA deliverables
    "EICA Design Documents": [
        "FER-EICA-1000",
        "FER-EICA-1020",
        "FER-EICA-1040"
    ],
    "EICA Drawings Issue": [
        "FER-EICA-1070",
        "FER-EICA-1080",
        "FER-EICA-1090"
    ],
}


# =========================
# EXTRACT DELIVERABLES
# =========================
def extract_milestones(df):

    df = _prepare(df)

    milestones = []

    for name, activity_ids in FERRY_DELIVERABLES.items():

        filtered = df[df["Activity ID"].isin(activity_ids)]

        if filtered.empty:
            continue

        # ✅ Take latest finish (represents final issued deliverable)
        row = filtered.sort_values("Finish").iloc[-1]

        # ✅ Calculate variance
        if pd.notna(row["Finish"]) and pd.notna(row["BL1 Finish"]):
            delta = int((row["Finish"] - row["BL1 Finish"]).days)
        else:
            delta = 0

        milestones.append({
            "Deliverable": name,
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

    st.markdown("## 📦 FERRY – KEY DELIVERABLE TRACKING (CL32)")

    if ms_df.empty:
        st.info("No deliverables identified")
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
        }
    ])

    st.write(styled)