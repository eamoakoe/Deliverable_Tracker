import streamlit as st
import pandas as pd


# =========================
# DELIVERABLE NAMES
# =========================
DELIVERABLE_NAMES = [
    "Outfall pipework optioneering",
    "Model Existing Tank",
    "Build Terrain Model",
    "BIM Set Up",
    "Civil Modelling - Tank",
    "Civil Modelling - Other Assets",
    "Mechanical Modelling",
    "Network modelling",
    "BIM Execution Plan",

    "Determine entry/exit levels",
    "Review GI",
    "Estimate conservative thickness",
    "Assessment to determine",
    "Check on shaft sizing",
    "Produce 2D conept drawing",
    "MGE Detailed Pile Design",
    "CAT2 check on MGE pile design",

    "Manhole Schedule",
    "Outline drawing",
    "GA & Long sections",
    "Valve chamber standard detail",
    "Kiosk slab proposal",
    "Shaft penetrations",

    "Line sizing",
    "Mechanical calculations",
    "Pump system curve",

    "Basis of Design",
    "Outline P&IDs",
    "Control Philosophy",

    "Submission of Outline Design Pack",
    "Client Review of Design Pack",

    "Review available GI",
    "GDR",
    "Client Review of GDR",

    "Benching design",
    "Cover slab design",
    "Pipe entry/exit",
    "Pipe exit details",

    "MH01 & MH02 Design",
    "Pipework from MHs to Shaft",

    "Valve Chamber",
    "Flowmeter Chamber",
    "Civils Pipe Design",

    "Tank kiosk enclosure foundation",

    "Assessment of exit details",
    "Routing & Design",

    "HAZOP",
    "DSEAR Assessment",
    "Material Take Off",

    "User Requirement Specification",
    "Load Schedule",
    "Power Supply Assessment",
    "Network Architecture Drawing",
    "Telemetry Schedules",

    "Single Line Diagrams",
    "Block Cable Diagrams",

    "Final Submission"
]


# =========================
# PREP DATA
# =========================
def _prepare(df):
    df = df.copy()
    df.columns = df.columns.astype(str).str.strip()

    df["Activity ID"] = df["Activity ID"].astype(str).str.strip()

    df["Finish"] = (
        df["Finish"]
        .astype(str)
        .str.replace(r"[A\*]", "", regex=True)
        .str.strip()
    )
    df["Finish"] = pd.to_datetime(df["Finish"], errors="coerce")

    df["Activity % Complete"] = (
        df["Activity % Complete"]
        .astype(str)
        .str.replace("%", "", regex=False)
        .str.strip()
    )
    df["Activity % Complete"] = pd.to_numeric(
        df["Activity % Complete"], errors="coerce"
    )

    return df


# =========================
# FILTER
# =========================
def is_deliverable(row):
    name = str(row.get("Activity Name", "")).lower()
    return any(d.lower() in name for d in DELIVERABLE_NAMES)


# =========================
# EXTRACT
# =========================
def extract_milestones(df):

    df = _prepare(df)

    df = df.sort_values("SnapshotDate")
    df = df.drop_duplicates(subset=["Activity ID", "SnapshotDate"], keep="last")

    dates = sorted(df["SnapshotDate"].dropna().unique())
    baseline_date = dates[0]
    forecast_date = dates[-1]

    baseline_df = df[df["SnapshotDate"] == baseline_date]
    forecast_df = df[df["SnapshotDate"] == forecast_date]

    baseline_df = baseline_df[baseline_df.apply(is_deliverable, axis=1)]
    forecast_df = forecast_df[forecast_df.apply(is_deliverable, axis=1)]

    forecast_df = forecast_df.copy()
    forecast_df["Progress %"] = forecast_df["Activity % Complete"]

    baseline_df = baseline_df.rename(columns={"Finish": "Baseline Finish"})
    forecast_df = forecast_df.rename(columns={"Finish": "Forecast Finish"})

    merged = pd.merge(
        baseline_df[["Activity ID", "Activity Name", "Baseline Finish"]],
        forecast_df[["Activity ID", "Forecast Finish", "Progress %"]],
        on="Activity ID",
        how="left"
    )

    merged["Δ Change (days)"] = (
        merged["Forecast Finish"] - merged["Baseline Finish"]
    ).dt.days.round(0).astype("Int64")

    merged = merged.rename(columns={"Activity Name": "Deliverable"})

    return merged, baseline_date, forecast_date


# =========================
# RENDER (DARK CARD)
# =========================
def render_milestone_table(df):

    ms_df, baseline_date, forecast_date = extract_milestones(df)

    if ms_df.empty:
        st.warning("⚠️ No deliverables found")
        return

    # ✅ Clear labels
    baseline_label = f"Forecast Finish ({baseline_date.strftime('%b %Y')})"
    forecast_label = f"Forecast Finish ({forecast_date.strftime('%b %Y')})"

    ms_df = ms_df.rename(columns={
        "Baseline Finish": baseline_label,
        "Forecast Finish": forecast_label
    })

    # ✅ Format
    ms_df[baseline_label] = pd.to_datetime(ms_df[baseline_label]).dt.strftime("%d-%b-%Y")
    ms_df[forecast_label] = pd.to_datetime(ms_df[forecast_label]).dt.strftime("%d-%b-%Y")

    ms_df["Progress %"] = ms_df["Progress %"].fillna(0).round(0).astype(int)

    # ✅ STATUS
    def status(row):
        d = row["Δ Change (days)"]
        if pd.isna(d):
            return ""
        elif d > 7:
            return "🔴 Delayed"
        elif d > 0:
            return "🟠 Slight Delay"
        else:
            return "🟢 On / Ahead"

    ms_df["Status"] = ms_df.apply(status, axis=1)

    # ✅ Sort
    ms_df = ms_df.sort_values("Δ Change (days)", ascending=False)

    # =========================
    # STYLING (DARK TABLE)
    # =========================
    styled = (
        ms_df.style
        .set_table_styles([
            {
                "selector": "thead",
                "props": [
                    ("background-color", "#082f49"),
                    ("color", "white"),
                    ("font-weight", "bold"),
                ]
            },
            {
                "selector": "tbody tr",
                "props": [
                    ("background-color", "#0f172a"),
                    ("color", "white"),
                ]
            },
            {
                "selector": "tbody tr:nth-child(even)",
                "props": [
                    ("background-color", "#1e293b"),
                ]
            },
        ])
    )

    # =========================
    # CARD WRAPPER ✅
    # =========================
    card = """
    <div style="
        background-color:#0b3d5c;
        padding:20px;
        border-radius:15px;
        box-shadow:0px 4px 12px rgba(0,0,0,0.3);
        margin-top:15px;
    ">
    <h3 style="color:white;">📊 Deliverables Performance</h3>
    """

    st.markdown(card, unsafe_allow_html=True)
    st.markdown(styled.to_html(), unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)