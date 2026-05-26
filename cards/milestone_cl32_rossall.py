import streamlit as st
import pandas as pd


# =========================
# PREP DATA (DESIGN SAFE)
# =========================
def _prepare(df):
    df = df.copy()

    df.columns = df.columns.astype(str).str.strip()

    # ✅ Fix IDs
    df["Activity ID"] = (
        df["Activity ID"]
        .astype(str)
        .str.replace("&amp;", "&", regex=False)
        .str.strip()
    )

    # ✅ Clean Start
    df["Start"] = (
        df["Start"]
        .astype(str)
        .str.replace(r"[A\*]", "", regex=True)
        .str.strip()
    )

    df["Start"] = pd.to_datetime(
        df["Start"],
        format="%d-%b-%y",
        errors="coerce"
    )

    # ✅ Clean Finish
    df["Finish"] = (
        df["Finish"]
        .astype(str)
        .str.replace(r"[A\*]", "", regex=True)
        .str.strip()
    )

    df["Finish"] = pd.to_datetime(
        df["Finish"],
        format="%d-%b-%y",
        errors="coerce"
    )

    # ✅ KEY: Design management date logic
    # ALWAYS take the latest available date (most reliable for design outputs)
    df["Date"] = df[["Start", "Finish"]].max(axis=1)

    return df


# =========================
# DESIGN DELIVERABLES ONLY
# =========================
ROSSELL_DESIGN = {

    # 🔥 TRUE DESIGN FREEZE (what YOU care about)
    "🔥 DESIGN FREEZE (Ready for Construction)": [
        "AMP8-DD&B-ROS-OUD-2310",  # NH Approval
        "AMP8-DD&B-ROS-OUD-2320",  # GI Final Factual
        "AMP8-DD&B-ROS-DES-1010"   # Detailed Design
    ],

    # 🔴 EXTERNAL CONTROL
    "National Highways Approval": [
        "AMP8-DD&B-ROS-OUD-2310"
    ],

    # 🟡 GROUND INVESTIGATION (DESIGN DRIVER)
    "GI Reports Complete": [
        "AMP8-DD&B-ROS-ECI-1450",
        "AMP8-DD&B-ROS-ECI-1430",
        "AMP8-DD&B-ROS-ECI-1420",
        "AMP8-DD&B-ROS-ECI-1410",
        "AMP8-DD&B-ROS-ECI-1400",
        "AMP8-DD&B-ROS-ECI-1180"
    ],

    "GI Final Factual": [
        "AMP8-DD&B-ROS-OUD-2320"
    ],

    # 🔵 DESIGN PROGRESSION
    "Outline Design Complete": [
        "AMP8-DD&B-ROS-OUD-1000"
    ],

    "Detailed Design Complete": [
        "AMP8-DD&B-ROS-DES-1010"
    ],

    "Temp Works Design Complete": [
        "AMP8-DD&B-ROS-TWD-2000"
    ],

    # ⚙️ DESIGN INPUTS
    "GPR Survey Complete": [
        "AMP8-DD&B-ROS-OUD-2300"
    ],

    "Piling Design Complete": [
        "AMP8-DD&B-ROS-OUD-1010"
    ],

    "Tunnel Alignment Fixed": [
        "AMP8-DD&B-ROS-OUD-2180"
    ],

    "Ecology Constraints Complete": [
        "AMP8-DD&B-ROS-ECI-2580"
    ],
}


# =========================
# EXTRACT DESIGN DELIVERABLES
# =========================
def extract_design(df):

    df = _prepare(df)

    results = []

    for name, ids in ROSSELL_DESIGN.items():

        filtered = df[df["Activity ID"].isin(ids)].copy()

        if filtered.empty:
            continue

        # ✅ Take latest = controlling design output
        row = filtered.sort_values("Date").iloc[-1]

        results.append({
            "Deliverable": name,
            "Activity": row["Activity Name"],
            "Date": row["Date"]
        })

    result_df = pd.DataFrame(results)

    if result_df.empty:
        st.warning("⚠️ No design deliverables found")
        st.write(df[["Activity ID", "Activity Name"]].head(20))

    return result_df


# =========================
# RENDER TABLE
# =========================
def render_design_table(df):

    design_df = extract_design(df)

    if design_df.empty:
        return

    # ✅ Sort by actual design sequence
    design_df = design_df.sort_values("Date")

    # Format dates
    design_df["Date"] = design_df["Date"].dt.strftime("%d-%b-%Y")

    # ✅ Highlight design risk zones
    def highlight(row):
        if "FREEZE" in row["Deliverable"]:
            return ["background-color:#7f1d1d;color:white;font-weight:bold"] * len(row)
        if "Approval" in row["Deliverable"]:
            return ["background-color:#b45309;color:white"] * len(row)
        if "GI" in row["Deliverable"]:
            return ["background-color:#1d4ed8;color:white"] * len(row)
        return [""] * len(row)

    styled = (
        design_df.style
        .apply(highlight, axis=1)
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