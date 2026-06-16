import pandas as pd
import plotly.graph_objects as go


# =========================
# ✅ DELIVERABLE LIST (MATCHES MILESTONE)
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


def is_deliverable(name):
    name = str(name).lower()
    return any(d.lower() in name for d in DELIVERABLE_NAMES)


# =========================
# ✅ MAIN FUNCTION
# =========================
def render_pie_ferry(df, container):

    df = df.copy()
    df.columns = df.columns.str.strip()

    # ✅ Deliverables only
    df = df[df["Activity Name"].apply(is_deliverable)]

    # ✅ Clean fields
    df["Activity ID"] = df["Activity ID"].astype(str).str.strip()
    df["Finish"] = pd.to_datetime(df["Finish"], errors="coerce")

    df["Activity % Complete"] = (
        df["Activity % Complete"]
        .astype(str)
        .str.replace("%", "", regex=False)
        .str.strip()
    )

    df["Activity % Complete"] = pd.to_numeric(
        df["Activity % Complete"], errors="coerce"
    ).fillna(0)

    # =========================
    # ✅ Δ CHANGE (MATCH MILESTONE)
    # =========================
    dates = sorted(df["SnapshotDate"].dropna().unique())

    if len(dates) >= 2:

        base_date = dates[0]
        latest_date = dates[-1]

        base_df = df[df["SnapshotDate"] == base_date][
            ["Activity ID", "Finish"]
        ].rename(columns={"Finish": "Base Finish"})

        latest_df = df[df["SnapshotDate"] == latest_date][
            ["Activity ID", "Finish", "Activity % Complete"]
        ].rename(columns={"Finish": "Latest Finish"})

        merged = pd.merge(base_df, latest_df, on="Activity ID", how="inner")

        merged["Δ Change (days)"] = (
            merged["Latest Finish"] - merged["Base Finish"]
        ).dt.days

        df = merged

    else:
        df["Δ Change (days)"] = 0

    # =========================
    # ✅ STATUS (SAME AS TABLE)
    # =========================
    def classify(row):

        if row["Activity % Complete"] >= 100:
            return "Completed"

        if row["Δ Change (days)"] > 0:
            return "Delayed"

        return "On Track"

    df["Status"] = df.apply(classify, axis=1)

    # =========================
    # ✅ SUMMARY
    # =========================
    summary = df["Status"].value_counts()
    summary = summary.reindex(
        ["On Track", "Delayed", "Completed"]
    ).fillna(0)

    summary = summary[summary > 0]

    # ✅ Colours
    colors = {
        "On Track": "#FFD700",   # 🟡 Gold
        "Delayed": "#FF3B30",    # 🔴 Red
        "Completed": "#00C853"   # 🟢 Green
    }

    # =========================
