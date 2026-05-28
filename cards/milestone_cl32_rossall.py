import streamlit as st
import pandas as pd


# =========================
# PREP DATA (ROBUST PARSING)
# =========================
def _prepare(df):
    df = df.copy()
    df.columns = df.columns.astype(str).str.strip()

    # ✅ Fix Activity ID encoding
    df["Activity ID"] = (
        df["Activity ID"]
        .astype(str)
        .str.replace("&amp;amp;", "&amp;", regex=False)
        .str.strip()
    )

    # ✅ Robust date parser
    def parse_dates(series):
        cleaned = (
            series.astype(str)
            .str.replace(r"[A\*]", "", regex=True)
            .str.strip()
            .replace("", pd.NA)
        )

        dt_strict = pd.to_datetime(
            cleaned,
            format="%d-%b-%y",
            errors="coerce"
        )

        dt_fallback = pd.to_datetime(
            cleaned,
            errors="coerce",
            dayfirst=True
        )

        return dt_strict.combine_first(dt_fallback)

    df["Start"] = parse_dates(df["Start"])
    df["Finish"] = parse_dates(df["Finish"])

    # ✅ Use finish first, fallback to start
    df["Date"] = df["Finish"].combine_first(df["Start"])

    return df


# =========================
# DESIGN DELIVERABLES
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
# EXTRACT DESIGN DATA
# =========================
def extract_design(df):

    df = _prepare(df)

    results = []

    for name, ids in ROSSELL_DESIGN.items():

        filtered = df[df["Activity ID"].isin(ids)].copy()

        if filtered.empty:
            continue

        filtered = filtered.dropna(subset=["Date"])

        if filtered.empty:
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

    return pd.DataFrame(results)


# =========================
# RENDER TABLE
# =========================
def render_design_table(df):

    design_df = extract_design(df)

    if design_df.empty:
        st.warning("⚠️ No design deliverables found")
        return

    # =========================
    # SORT
    # =========================
    design_df = design_df.sort_values("Date")

    # =========================
    # KPI SUMMARY ✅
    # =========================
    total = len(design_df)
    missing = design_df["Date"].isna().sum()
    freeze = design_df["Deliverable"].str.contains("FREEZE", na=False).sum()

    col1, col2, col3 = st.columns(3)
    col1.metric("📦 Total Deliverables", total)
    col2.metric("🔥 Design Freeze", freeze)
    col3.metric("⚠ Missing Dates", missing)

    # =========================
    # FORMAT DATE
    # =========================
    design_df["Date"] = pd.to_datetime(design_df["Date"]).dt.strftime("%d-%b-%Y")
    design_df["Date"] = design_df["Date"].fillna("⚠ Missing")

    # =========================
    # STATUS COLUMN ✅
    # =========================
    def status(row):
        if "⚠" in str(row["Date"]):
            return "⚠ Missing"
        if "FREEZE" in row["Deliverable"]:
            return "🔥 Critical"
        if "Approval" in row["Deliverable"]:
            return "🟠 Key Approval"
        return "🟢 Standard"

    design_df["Status"] = design_df.apply(status, axis=1)

    # =========================
    # STYLING (CLEAN DARK)
    # =========================
    def colour_status(val):
        if "🔥" in val:
            return "background-color:#7f1d1d;color:white;font-weight:bold"
        elif "🟠" in val:
            return "background-color:#b45309;color:white"
        elif "⚠" in val:
            return "background-color:#7c2d12;color:white"
        elif "🟢" in val:
            return "background-color:#14532d;color:white"
        return ""

    def highlight_freeze(val):
        if "FREEZE" in val:
            return "font-weight:bold;color:#f87171"
        return ""

    styled = (
        design_df.style
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
        .map(colour_status, subset=["Status"])
        .map(highlight_freeze, subset=["Deliverable"])
    )

    st.markdown(styled.to_html(), unsafe_allow_html=True)


# =========================
# BACKWARD COMPATIBILITY
# =========================
render_milestone_table = render_design_table