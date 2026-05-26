import streamlit as st
import pandas as pd


# =========================
# PREP DATA
# =========================
def _prepare(df):
    df = df.copy()
    df.columns = df.columns.astype(str).str.strip()

    df["Activity ID"] = df["Activity ID"].astype(str).str.strip()

    for col in ["Finish", "BL1 Finish"]:
        df[col] = (
            df[col]
            .astype(str)
            .str.replace(r"[A\*]", "", regex=True)
            .str.strip()
        )
        df[col] = pd.to_datetime(df[col], errors="coerce")

    return df


# =========================
# ✅ FERRY DELIVERABLES
# =========================
FERRY_DELIVERABLES = {

    "🔥 DESIGN FREEZE – SCOPE LOCKED": ["FER-PD-1010"],
    "🔥 DESIGN FREEZE – CLIENT APPROVED": ["FER-REV-1030"],

    "Concept Design Submission": ["FER-PD-1000"],
    "Full Outline Design Submission": ["FER-PD-1020"],
    "Project Completion": ["FER-PD-1030"],

    "Outline Design Pack Submission": ["FER-REV-1000"],
    "Detailed Design Submission": ["FER-REV-1020"],
    "Final Submission": ["FER-REV-1050"],

    "Geotechnical Report (GDR)": ["FER-GEO-1010"],
    "HAZOP Closeout": ["FER-PRO-1040"],

    "Concept Drawing Issue": ["FER-CSD-1060"],
    "Pile Design Complete": ["FER-CSD-1070"],

    "Civils Design Complete": [
        "FER-CIV-1070",
        "FER-CIV-1110",
        "FER-CIV-1150"
    ],

    "Mechanical Design Complete": [
        "FER-MEC-1030",
        "FER-MEC-1040",
        "FER-MEC-1050"
    ],

    "Mechanical Drawings Issued": [
        "FER-MEC-1060",
        "FER-MEC-1110"
    ],

    "Process Design Complete": [
        "FER-PRO-1010",
        "FER-PRO-1000",
        "FER-PRO-1020"
    ],

    "EICA Design Complete": [
        "FER-EICA-1000",
        "FER-EICA-1040",
        "FER-EICA-1070"
    ],
}


# =========================
# EXTRACT DELIVERABLES
# =========================
def extract_milestones(df):

    df = _prepare(df)
    milestones = []

    for name, activity_ids in FERRY_DELIVERABLES.items():

        filtered = df[
            df["Activity ID"].str.contains("|".join(activity_ids), na=False)
        ].copy()

        if filtered.empty:
            continue

        filtered["Sort Date"] = filtered["Finish"].fillna(filtered["BL1 Finish"])
        filtered = filtered.sort_values("Sort Date")

        row = filtered.iloc[-1]

        if pd.notna(row["Finish"]) and pd.notna(row["BL1 Finish"]):
            delta = int((row["Finish"] - row["BL1 Finish"]).days)
        else:
            delta = 0

        milestones.append({
            "Deliverable": name,
            "Source Activity": row["Activity Name"],
            "Baseline Finish (CL32 May)": row["BL1 Finish"],
            "Forecast Finish": row["Finish"],
            "Δ (Days)": delta
        })

    ms_df = pd.DataFrame(milestones)

    if not ms_df.empty:
        ms_df["Δ (Days)"] = ms_df["Δ (Days)"].fillna(0).astype(int)

    return ms_df


# =========================
# ✅ RENDER TABLE (FINAL)
# =========================
def render_milestone_table(df):

    ms_df = extract_milestones(df)

    if ms_df.empty:
        st.warning("⚠️ No deliverables identified")
        return

    # ✅ Format dates
    ms_df["Baseline Finish (CL32 May)"] = pd.to_datetime(
        ms_df["Baseline Finish (CL32 May)"]
    ).dt.strftime("%d-%b-%Y")

    ms_df["Forecast Finish"] = pd.to_datetime(
        ms_df["Forecast Finish"]
    ).dt.strftime("%d-%b-%Y")

    # =========================
    # ✅ STYLING
    # =========================

    # Δ column highlight only
    def colour_delta(val):
        if val < 0:
            return "background-color:#fdecea;color:#b91c1c;font-weight:600"
        elif val > 0:
