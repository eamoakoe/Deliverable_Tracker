import streamlit as st
import pandas as pd
from your_pie_file import render_pie_ferry  # ✅ import your existing pie


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


def is_deliverable(row):
    name = str(row.get("Activity Name", "")).lower()
    return any(d.lower() in name for d in DELIVERABLE_NAMES)


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
    ).dt.days.round(0)

    merged = merged.rename(columns={"Activity Name": "Deliverable"})

    return merged, baseline_date, forecast_date


# =========================
# ✅ MAIN RENDER
# =========================
def render_milestone_table(df):

    ms_df, baseline_date, forecast_date = extract_milestones(df)

    if ms_df.empty:
        st.warning("⚠️ No deliverables found")
        return

    # ✅ ✅ ✅ SHOW PIE ABOVE TABLE
    st.markdown("### 📊 Delivery Status (Current)")
