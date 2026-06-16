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

    # ✅ Clean Finish
    df["Finish"] = (
        df["Finish"]
        .astype(str)
        .str.replace(r"[A\*]", "", regex=True)
        .str.strip()
    )
    df["Finish"] = pd.to_datetime(df["Finish"], errors="coerce")

    # ✅ Clean Progress
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
# DELIVERABLE FILTER
# =========================
def is_deliverable(row):
    name = str(row.get("Activity Name", "")).lower()
    return any(d.lower() in name for d in DELIVERABLE_NAMES)


# =========================
# EXTRACT
# =========================
def extract_milestones(df):

    df = _prepare(df)

    # ✅ Ensure unique rows
    df = df.sort_values("SnapshotDate")
    df = df.drop_duplicates(subset=["Activity ID", "SnapshotDate"], keep="last")

    # ✅ Identify snapshots
    dates = sorted(df["SnapshotDate"].dropna().unique())
    baseline_date = dates[0]
    forecast_date = dates[-1]

    baseline_df = df[df["SnapshotDate"] == baseline_date]
    forecast_df = df[df["SnapshotDate"] == forecast_date]

    # ✅ Filter deliverables
    baseline_df = baseline_df[baseline_df.apply(is_deliverable, axis=1)]
    forecast_df = forecast_df[forecast_df.apply(is_deliverable, axis=1)]

    # ✅ Extract latest progress ONLY ✅
    forecast_df = forecast_df.copy()
    forecast_df["Progress %"] = forecast_df["Activity % Complete"]

    # ✅ Rename
    baseline_df = baseline_df.rename(columns={"Finish": "Baseline Finish"})
    forecast_df = forecast_df.rename(columns={"Finish": "Forecast Finish"})

    # ✅ Merge
    merged = pd.merge(
        baseline_df[["Activity ID", "Activity Name", "Baseline Finish"]],
        forecast_df[["Activity ID", "Forecast Finish", "Progress %"]],
        on="Activity ID",
        how="left"
    )

    # ✅ Δ Change (clean int)
    merged["Δ Change (days)"] = (
        merged["Forecast Finish"] - merged["Baseline Finish"]
    ).dt.days.round(0).astype("Int64")

    merged = merged.rename(columns={
        "Activity Name": "Deliverable"
    })

    return merged, baseline_date, forecast_date


# =========================
# RENDER
# =========================
def render_milestone_table(df):

    ms_df, baseline_date, forecast_date = extract_milestones(df)

    if ms_df.empty:
        st.warning("⚠️ No deliverables found")
        return

    # ✅ NEW CLEAR LABELS ✅
    baseline_label = f"Forecast Finish ({baseline_date.strftime('%b %Y')})"
    forecast_label = f"Forecast Finish ({forecast_date.strftime('%b %Y')})"

    ms_df = ms_df.rename(columns={
        "Baseline Finish": baseline_label,
        "Forecast Finish": forecast_label
    })

    # ✅ Format dates
    ms_df[baseline_label] = pd.to_datetime(ms_df[baseline_label]).dt.strftime("%d-%b-%Y")
    ms_df[forecast_label] = pd.to_datetime(ms_df[forecast_label]).dt.strftime("%d-%b-%Y")

    # ✅ Clean progress
    ms_df["Progress %"] = ms_df["Progress %"].fillna(0).round(0).astype(int)

    # =========================
    # STATUS
    # =========================
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

    # =========================
    # KPI
    # =========================
    col1, col2, col3 = st.columns(3)

    col1.metric("🔴 Delayed", int((ms_df["Δ Change (days)"] > 7).sum()))
    col2.metric("🟠 Slight Delay", int(((ms_df["Δ Change (days)"] > 0) & (ms_df["Δ Change (days)"] <= 7)).sum()))
    col3.metric("🟢 On / Ahead", int((ms_df["Δ Change (days)"] <= 0).sum()))

    # ✅ Sort worst first
    ms_df = ms_df.sort_values("Δ Change (days)", ascending=False)

    # =========================
    # STYLING
    # =========================
    def colour_delta(val):
        if pd.isna(val):
            return ""
        if val > 7:
            return "background-color:#7f1d1d;color:white;font-weight:bold"
        elif val > 0:
            return "background-color:#ff9800;color:black"
        return "background-color:#14532d;color:white"

    def colour_status(val):
        if "🔴" in val:
            return "background-color:#b00020;color:white"
        elif "🟠" in val:
            return "background-color:#ff9800;color:black"
        elif "🟢" in val:
            return "background-color:#1e7e34;color:white"
        return ""

    styled = (
        ms_df.style
        .map(colour_delta, subset=["Δ Change (days)"])
        .map(colour_status, subset=["Status"])
    )

    st.markdown(styled.to_html(), unsafe_allow_html=True)
