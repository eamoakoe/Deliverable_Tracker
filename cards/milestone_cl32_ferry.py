import streamlit as st
import pandas as pd


# =========================
# PREP DATA
# =========================
def _prepare(df):
    df = df.copy()
    df.columns = df.columns.astype(str).str.strip()

    # ✅ Clean Activity ID
    df["Activity ID"] = df["Activity ID"].astype(str).str.strip()

    # ✅ Clean P6 date issues (A, *)
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
# ✅ FERRY DELIVERABLES (FINAL + FREEZE INCLUDED)
# =========================
FERRY_DELIVERABLES = {

    # 🔥 CRITICAL – DESIGN FREEZE POINTS (TOP OF TRACKER)
    "🔥 DESIGN FREEZE – SCOPE LOCKED": ["FER-PD-1010"],
    "🔥 DESIGN FREEZE – CLIENT APPROVED": ["FER-REV-1030"],

    # 🔴 Stage gates
    "Concept Design Submission": ["FER-PD-1000"],
    "Full Outline Design Submission": ["FER-PD-1020"],
    "Project Completion": ["FER-PD-1030"],

    # 🟠 Client submissions
    "Outline Design Pack Submission": ["FER-REV-1000"],
    "Detailed Design Submission": ["FER-REV-1020"],
    "Final Submission": ["FER-REV-1050"],

    # 🟡 Reports
    "Geotechnical Report (GDR)": ["FER-GEO-1010"],
    "HAZOP Closeout": ["FER-PRO-1040"],

    # 🔵 Concept outputs
    "Concept Drawing Issue": ["FER-CSD-1060"],
    "Pile Design Complete": ["FER-CSD-1070"],

    # 🟣 Civil final outputs
    "Civils Design Complete": [
        "FER-CIV-1070",
        "FER-CIV-1110",
        "FER-CIV-1150"
    ],

    # ⚙️ Mechanical
    "Mechanical Design Complete": [
        "FER-MEC-1030",
        "FER-MEC-1040",
        "FER-MEC-1050"
    ],

    "Mechanical Drawings Issued": [
        "FER-MEC-1060",
        "FER-MEC-1110"
    ],

    # 🧪 Process
    "Process Design Complete": [
        "FER-PRO-1010",
        "FER-PRO-1000",
        "FER-PRO-1020"
    ],

    # ⚡ EICA
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

        # ✅ robust ID matching
        filtered = df[
            df["Activity ID"].str.contains(
                "|".join(activity_ids),
                na=False
            )
        ].copy()

        if filtered.empty:
            continue

        # ✅ Use Finish, fallback to Baseline
        filtered["Sort Date"] = filtered["Finish"].fillna(filtered["BL1 Finish"])

        filtered = filtered.sort_values("Sort Date")

        row = filtered.iloc[-1]

        # ✅ Variance calculation
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

    # ✅ Force numeric Δ
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
        st.warning("⚠️ No deliverables identified - check Activity ID mapping")
        return

    # ✅ Format dates
    ms_df["Baseline Finish (CL32 May)"] = pd.to_datetime(
        ms_df["Baseline Finish (CL32 May)"]
    ).dt.strftime("%d-%b-%Y")

    ms_df["Forecast Finish"] = pd.to_datetime(
        ms_df["Forecast Finish"]
    ).dt.strftime("%d-%b-%Y")

    # ✅ Colour Δ
    def colour_delta(val):
        if val < 0:
            return "background-color:#7f1d1d;color:white;font-weight:bold"  # late
        elif val > 0:
            return "background-color:#14532d;color:white;font-weight:bold"  # early
        return "background-color:#374151;color:white"  # on time

    styled = (
        ms_df.style
        .map(colour_delta, subset=["Δ (Days)"])
        .set_table_styles([
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
    )

    st.write(styled)