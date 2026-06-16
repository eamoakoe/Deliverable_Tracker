import pandas as pd
import plotly.graph_objects as go


# =========================
# ✅ SAME DELIVERABLE LIST (MATCHES MILESTONE)
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
# MAIN FUNCTION
# =========================
def render_pie_ferry(df, container):

    # ---------- CLEAN ----------
    df = df.copy()
    df.columns = df.columns.str.strip()

    # ✅ Latest CL32 only
    if "SnapshotDate" in df.columns:
        latest_date = df["SnapshotDate"].max()
        df = df[df["SnapshotDate"] == latest_date]

    # ✅ Deliverables only (aligned with milestone)
    df = df[df["Activity Name"].apply(is_deliverable)]

    # ✅ Clean Activity ID
    df["Activity ID"] = df["Activity ID"].astype(str).str.strip()

    # ✅ Clean % Complete
    df["Activity % Complete"] = (
        df["Activity % Complete"]
        .astype(str)
        .str.replace("%", "", regex=False)
        .str.strip()
    )

    df["Activity % Complete"] = pd.to_numeric(
        df["Activity % Complete"], errors="coerce"
    ).fillna(0)

    # ✅ Clean Finish
    df["Finish"] = pd.to_datetime(
        df["Finish"], dayfirst=True, errors="coerce"
    ).dt.normalize()

    today = pd.Timestamp.today().normalize()

    # =========================
    # ✅ STATUS LOGIC (SAME AS BEFORE)
    # =========================
    def classify(row):

        progress = row["Activity % Complete"]
        finish = row["Finish"]

        if progress >= 100:
            return "Completed"

        if pd.isna(finish):
            return "On Track"

        if finish < today:
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

    # ✅ Colours (your spec)
    colors = {
        "On Track": "#FFD700",   # 🟡 Gold
        "Delayed": "#FF3B30",    # 🔴 Red
        "Completed": "#00C853"   # 🟢 Green
    }

    # =========================
    # ✅ SINGLE PIE
    # =========================
    fig = go.Figure(
        data=[go.Pie(
            labels=summary.index,
            values=summary.values,

            # ✅ SHOW LABEL + NUMBER + %
            textinfo="label+value+percent",

            marker=dict(
                colors=[colors[k] for k in summary.index]
            ),

            sort=False,
            hole=0  # ✅ solid pie
        )]
    )

    fig.update_layout(
        height=260,
        margin=dict(l=5, r=5, t=5, b=5),
        showlegend=False
    )

    container.plotly_chart(fig, width="stretch")