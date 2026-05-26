import streamlit as st
import pandas as pd


# =========================
# PREP DATA (ROBUST + FLEXIBLE)
# =========================
def _prepare(df):
    df = df.copy()

    # Clean column names
    df.columns = df.columns.astype(str).str.strip()

    # ✅ Fix Activity ID encoding
    df["Activity ID"] = (
        df["Activity ID"]
        .astype(str)
        .str.replace("&amp;", "&", regex=False)
        .str.strip()
    )

    # ✅ Clean date text (handles A, *, blanks, weird spaces)
    def clean_date(col):
        return (
            df[col]
            .astype(str)
            .str.replace(r"[A\*]", "", regex=True)
            .str.replace(r"\s+", " ", regex=True)
            .str.strip()
            .replace("", pd.NA)
        )

    df["Start"] = clean_date("Start")
    df["Finish"] = clean_date("Finish")

    # ✅ Flexible parsing (handles Jan, Feb etc automatically)
    df["Start"] = pd.to_datetime(df["Start"], errors="coerce", dayfirst=True)
    df["Finish"] = pd.to_datetime(df["Finish"], errors="coerce", dayfirst=True)

    # ✅ DESIGN LOGIC (CRITICAL)
    # → Always use Finish if available, else Start
    df["Date"] = df["Finish"].combine_first(df["Start"])

    return df


# =========================
# DESIGN DELIVERABLES (ROSSALL)
# =========================
ROSSELL_DESIGN = {

    "🔥 DESIGN FREEZE (Ready for Construction)": [
        "AMP8-DD&B-ROS-OUD-2310",
        "AMP8-DD&B-ROS-OUD-2320",
        "AMP8-DD&B-ROS-DES-1010"
    ],

    "National Highways Approval": [
        "AMP8-DD&B-ROS-OUD-2310"
    ],

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

    "Outline Design Complete": [
        "AMP8-DD&B-ROS-OUD-1000"
    ],

    "Detailed Design Complete": [
        "AMP8-DD&B-ROS-DES-1010"
    ],

    "Temp Works Design Complete": [
        "AMP8-DD&B-ROS-TWD-2000"
    ],

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

        # ✅ Use latest valid date (controls multi-activity deliverables)
        filtered = filtered.dropna(subset=["Date"])

        if filtered.empty:
            # still append empty row so you SEE gaps
            results.append({
                "Deliverable": name,
                "Activity": "⚠ No valid date",
                "Date": pd.NaT
            })
            continue

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

    # Sort chronologically
    design_df = design_df.sort_values("Date")

    # Format date safely
    design_df["Date"] = design_df["Date"].dt.strftime("%d-%b-%Y")

    design_df["Date"] = design_df["Date"].fillna("⚠ Missing")

    # ✅ Highlight key design controls
    def highlight(row):
        if "FREEZE" in row["Deliverable"]:
            return ["background-color:#7f1d1d;color:white;font-weight:bold"] * len(row)
        if "Approval" in row["Deliverable"]:
            return ["background-color:#b45309;color:white"] * len(row)
        if "GI" in row["Deliverable"]:
            return ["background-color:#1d4ed8;color:white"] * len(row)
        if "⚠" in row["Date"]:
            return ["background-color:#7c2d12;color:white"] * len(row)
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


# ✅ ✅ CRITICAL IMPORT FIX (KEEP LAST)
render_milestone_table = render_design_table