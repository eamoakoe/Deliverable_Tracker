import streamlit as st
import pandas as pd


# =========================
# PREP DATA (ROBUST TO YOUR FORMAT)
# =========================
def _prepare(df):
    df = df.copy()

    # ✅ Clean column names
    df.columns = df.columns.astype(str).str.strip()

    # ✅ Clean Activity ID
    df["Activity ID"] = df["Activity ID"].astype(str).str.strip()

    # ✅ Clean Finish column (handles A, *, blanks)
    df["Finish"] = (
        df["Finish"]
        .astype(str)
        .str.replace(r"[A\*]", "", regex=True)
        .str.strip()
    )

    df["Finish"] = pd.to_datetime(df["Finish"], errors="coerce")

    return df


# =========================
# ✅ DELIVERABLE DEFINITIONS
# =========================
ROSSELL_DELIVERABLES = {

    # 🔥 DESIGN FREEZE (CRITICAL CONTROL POINT)
    "🔥 DESIGN FREEZE – APPROVED": [
        "AMP8-DD&B-ROS-OUD-2310"
    ],

    # 🔴 Programme milestones
    "AIO Planned Completion": [
        "AMP8-DD&B-ROS-MIL-1080"
    ],

    "AIO Contract Completion": [
        "AMP8-DD&B-ROS-MIL-1070"
    ],

    # 🟡 Key reports
    "Ground Investigation Reports": [
        "AMP8-DD&B-ROS-ECI-1450",
        "AMP8-DD&B-ROS-ECI-1430",
        "AMP8-DD&B-ROS-ECI-1420",
        "AMP8-DD&B-ROS-ECI-1410",
        "AMP8-DD&B-ROS-ECI-1400",
        "AMP8-DD&B-ROS-ECI-1180"
    ],

    "Ecology Surveys Complete": [
        "AMP8-DD&B-ROS-ECI-2580"
    ],

    # 🔵 Design outputs
    "Outline Design Complete": [
        "AMP8-DD&B-ROS-OUD-1000"
    ],

    "GI Final Factual": [
        "AMP8-DD&B-ROS-OUD-2320"
    ],

    "Detailed Design Complete": [
        "AMP8-DD&B-ROS-DES-1010"
    ],

    "Temp Works Design Complete": [
        "AMP8-DD&B-ROS-TWD-2000"
    ],

    # ⚙️ Supporting deliverables
    "GPR Survey Complete": [
        "AMP8-DD&B-ROS-OUD-2300"
    ],

    "Piling Design Complete": [
        "AMP8-DD&B-ROS-OUD-1010"
    ],
}


# =========================
# EXTRACT DELIVERABLES
# =========================
def extract_milestones(df):

    df = _prepare(df)

    milestones = []

    for name, ids in ROSSELL_DELIVERABLES.items():

        filtered = df[
            df["Activity ID"].str.contains(
                "|".join(ids),
                na=False
            )
        ].copy()

        if filtered.empty:
            continue

        # ✅ Sort by finish (latest = controlling activity)
        filtered = filtered.sort_values("Finish")

        row = filtered.iloc[-1]

        milestones.append({
            "Deliverable": name,
            "Activity": row["Activity Name"],
            "Finish Date": row["Finish"]
        })

    return pd.DataFrame(milestones)


# =========================
# RENDER
# =========================
def render_milestone_table(df):

    ms_df = extract_milestones(df)

    st.markdown("## 📦 ROSSALL – KEY DELIVERABLE TRACKING (CL32)")

    if ms_df.empty:
        st.warning("⚠️ No deliverables identified")
        return

    # ✅ Format date cleanly
    ms_df["Finish Date"] = pd.to_datetime(
        ms_df["Finish Date"]
    ).dt.strftime("%d-%b-%Y")

    # ✅ Highlight DESIGN FREEZE
    def highlight_row(row):
        if "FREEZE" in row["Deliverable"]:
            return ["background-color:#7f1d1d;color:white;font-weight:bold"] * len(row)
        return [""] * len(row)

    styled = (
        ms_df.style
        .apply(highlight_row, axis=1)
        .set_table_styles([
            {
                "selector": "th",
                "props": [
                    ("background-color", "#2b3a55"),
                    ("color", "white"),
                    ("font-weight", "600"),
                    ("padding", "10px"),
                ]
            },
            {
                "selector": "td",
                "props": [
                    ("background-color", "#1c2233"),
                    ("color", "#f1f1f1"),
                    ("padding", "8px"),
                ]
            }
        ])
    )

    st.write(styled)