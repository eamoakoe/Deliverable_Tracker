import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np


# =========================
# DELIVERABLES
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
# MAIN
# =========================
def render_milestone_table(df):

    df = df.copy()
    df.columns = df.columns.str.strip()
    df["Activity Name"] = df["Activity Name"].astype(str).str.strip()

    # ✅ Latest snapshot
    latest_date = pd.to_datetime(df["SnapshotDate"]).max()
    df_latest = df[df["SnapshotDate"] == latest_date]

    # ✅ Deliverables
    df_deliv = df_latest[df_latest["Activity Name"].apply(is_deliverable)].copy()

    df_deliv["Finish"] = pd.to_datetime(df_deliv["Finish"], errors="coerce")

    df_deliv["Activity % Complete"] = (
        df_deliv["Activity % Complete"]
        .astype(str)
        .str.replace("%", "", regex=False)
        .str.strip()
    )
    df_deliv["Activity % Complete"] = pd.to_numeric(
        df_deliv["Activity % Complete"], errors="coerce"
    ).fillna(0)

    today = pd.Timestamp.today().normalize()

    # =========================
    # ✅ PIE
    # =========================
    def classify(row):
        if row["Activity % Complete"] >= 100:
            return "Completed"
        elif pd.notna(row["Finish"]) and today > row["Finish"]:
            return "Delayed"
        else:
            return "On Track"

    df_deliv["Status"] = df_deliv.apply(classify, axis=1)

    summary = df_deliv["Status"].value_counts().reindex(
        ["On Track", "Delayed", "Completed"]
    ).fillna(0)

    colors = {
        "On Track": "#FFD700",
        "Delayed": "#FF3B30",
        "Completed": "#00C853"
    }

    st.markdown("### 📊 Delivery Status (Current)")

    fig = go.Figure(
        data=[go.Pie(
            labels=summary.index,
            values=summary.values,
            textinfo="label+value+percent",
            textposition="inside",
            marker=dict(colors=[colors[k] for k in summary.index]),
            sort=False
        )]
    )

    fig.update_layout(height=250, margin=dict(l=5, r=5, t=5, b=5), showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    # =========================
    # ✅ PROGRAMME TABLE
    # =========================
