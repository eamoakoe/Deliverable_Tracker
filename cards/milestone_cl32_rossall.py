import streamlit as st
import pandas as pd


# =========================
# PREP DATA (ROBUST)
# =========================
def _prepare(df):
    df = df.copy()

    # Clean column names
    df.columns = df.columns.astype(str).str.strip()

    # ✅ Clean Activity ID (CRITICAL FIX)
    df["Activity ID"] = (
        df["Activity ID"]
        .astype(str)
        .str.replace("&amp;", "&", regex=False)  # FIX HTML encoding
        .str.strip()
    )

    # ✅ Clean Finish column
    df["Finish"] = (
        df["Finish"]
        .astype(str)
        .str.replace(r"[A\*]", "", regex=True)
        .str.strip()
    )

    df["Finish"] = pd.to_datetime(df["Finish"], errors="coerce")

    return df


# =========================
# ✅ DESIGN DELIVERABLES (CLEAN IDs - NO HTML)
# =========================
ROSSELL_DELIVERABLES = {

    "🔥 DESIGN FREEZE – VERIFIED": [
        "AMP8-DD&B-ROS-OUD-2310",
        "AMP8-DD&B-ROS-OUD-2320",
        "AMP8-DD&B-ROS-DES-1010"
    ],

    "National Highways Approval": [
        "AMP8-DD&B-ROS-OUD-2310"
    ],

    "GI Reports Complete (All Shafts)": [
        "AMP8-DD&B-ROS-ECI-1450",
        "AMP8-DD&B-ROS-ECI-1430",
        "AMP8-DD&B-ROS-ECI-1420",
        "AMP8-DD&B-ROS-ECI-1410",
        "AMP8-DD&B-ROS-ECI-1400",
        "AMP8-DD&B-ROS-ECI-1180"
    ],

    "GI Final Factual Complete": [
        "AMP8-DD&B-ROS-OUD-2320"
    ],

    "Outline Design Complete": [
        "AMP8-DD&B-ROS-OUD-1000"
    ],

    "Detailed Design Complete": [
        "AMP8-DD&B-ROS-DES-1010"
    ],

    "Temporary Works Design Complete": [
        "AMP8-DD&B-ROS-TWD-2000"
    ],

    "GPR Survey Complete": [
        "AMP8-DD&B-ROS-OUD-2300"
    ],

    "Piling Design Complete": [
        "AMP8-DD&B-ROS-OUD-1010"
    ],

    "Tunnel / Alignment Decisions Complete": [
        "AMP8-DD&B-ROS-OUD-2180"
    ],

    "Ecology Surveys Complete": [
        "AMP8-DD&B-ROS-ECI-2580"
    ],
}


# =========================
# EXTRACT DELIVERABLES
# =========================
def extract_milestones(df):

    df = _prepare(df)

    milestones = []

    for name, ids in ROSSELL_DELIVERABLES.items():

        # ✅ EXACT MATCH (no regex issues)
        filtered = df[df["Activity ID"].isin(ids)].copy()

        if filtered.empty:
            continue

        filtered = filtered.sort_values("Finish")

        row = filtered.iloc[-1]

        milestones.append({
            "Deliverable": name,
            "Activity": row["Activity Name"],
            "Finish Date": row["Finish"]
        })

    result = pd.DataFrame(milestones)

    # ✅ FALLBACK: if still empty, show debug info
    if result.empty:
        st.warning("⚠️ No matches found — showing sample Activity IDs below for debugging")
        st.write(df[["Activity ID", "Activity Name"]].head(20))

    return result


# =========================
# RENDER
# =========================
def render_milestone_table(df):

    ms_df = extract_milestones(df)

    if ms_df.empty:
        return

    ms_df = ms_df.sort_values("Finish Date")

    ms_df["Finish Date"] = pd.to_datetime(
        ms_df["Finish Date"]
    ).dt.strftime("%d-%b-%Y")

    # ✅ Highlight key rows
    def highlight_row(row):
        if "FREEZE" in row["Deliverable"]:
            return ["background-color:#7f1d1d;color:white;font-weight:bold"] * len(row)
        if "Approval" in row["Deliverable"]:
            return ["background-color:#b45309;color:white"] * len(row)
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