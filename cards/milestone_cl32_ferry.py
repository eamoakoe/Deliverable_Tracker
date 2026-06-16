import streamlit as st
import pandas as pd
import plotly.graph_objects as go


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

    # ✅ Latest CL32 only
    latest_date = df["SnapshotDate"].max()
    df_latest = df[df["SnapshotDate"] == latest_date]

    # ✅ Deliverables only
    df_latest = df_latest[df_latest["Activity Name"].apply(is_deliverable)]

    # ✅ Clean fields
    df_latest["Finish"] = pd.to_datetime(df_latest["Finish"], errors="coerce")

    df_latest["Activity % Complete"] = (
        df_latest["Activity % Complete"]
        .astype(str)
        .str.replace("%", "", regex=False)
        .str.strip()
    )
    df_latest["Activity % Complete"] = pd.to_numeric(
        df_latest["Activity % Complete"], errors="coerce"
    ).fillna(0)

    today = pd.Timestamp.today().normalize()

    # =========================
    # ✅ DELIVERY PIE LOGIC
    # =========================
    def classify(row):

        progress = row["Activity % Complete"]
        finish = row["Finish"]

        if progress >= 100:
            return "Completed"
        elif pd.notna(finish) and today > finish:
            return "Delayed"
        else:
            return "On Track"

    df_latest["Status"] = df_latest.apply(classify, axis=1)

    summary = df_latest["Status"].value_counts().reindex(
        ["On Track", "Delayed", "Completed"]
    ).fillna(0)

    colors = {
        "On Track": "#FFD700",
        "Delayed": "#FF3B30",
        "Completed": "#00C853"
    }

    # =========================
    # ✅ SHOW PIE
    # =========================
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

    fig.update_layout(
        height=250,
        margin=dict(l=5, r=5, t=5, b=5),
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)

    # =========================
    # ✅ PROGRAMME TABLE (EXISTING LOGIC)
    # =========================

    # prepare baseline vs latest
    dates = sorted(df["SnapshotDate"].dropna().unique())
    baseline_date = dates[0]

    baseline_df = df[df["SnapshotDate"] == baseline_date]
    baseline_df = baseline_df[baseline_df["Activity Name"].apply(is_deliverable)]

    baseline_df = baseline_df.rename(columns={"Finish": "Baseline Finish"})

    merged = pd.merge(
        baseline_df[["Activity ID", "Activity Name", "Baseline Finish"]],
        df_latest[["Activity ID", "Finish", "Activity % Complete"]],
        on="Activity ID",
        how="left"
    )

    merged = merged.rename(columns={
        "Activity Name": "Deliverable",
        "Finish": "Forecast Finish",
        "Activity % Complete": "Progress %"
    })

    merged["Δ Change (days)"] = (
        pd.to_datetime(merged["Forecast Finish"]) -
        pd.to_datetime(merged["Baseline Finish"])
    ).dt.days

    # ✅ FIX NA
    merged["Δ Change (days)"] = merged["Δ Change (days)"].fillna(0).astype(int)
    merged["Progress %"] = merged["Progress %"].fillna(0).astype(int)

    # ✅ STATUS (programme)
    def programme_status(row):
        if row["Progress %"] >= 100:
            return "🟢 Completed"
        elif row["Δ Change (days)"] > 0:
            return "🔴 Slipped"
        else:
            return "🟡 On Track"

    merged["Status"] = merged.apply(programme_status, axis=1)

    merged = merged.sort_values("Δ Change (days)", ascending=False)

    # =========================
    # ✅ TABLE STYLE
    # =========================
    styled = (
        merged.style
        .set_table_styles([
            {
                "selector": "thead th",
                "props": [
                    ("background-color", "#082f49"),
                    ("color", "white"),
                    ("font-weight", "bold"),
                    ("border", "1px solid #334155"),
                ]
            },
            {
                "selector": "tbody td",
                "props": [
                    ("background-color", "#0f172a"),
                    ("color", "white"),
                    ("border", "1px solid #334155"),
                ]
            }
        ])
    )

    st.markdown("### 📊 Deliverables Performance CL32")
    st.markdown(styled.to_html(), unsafe_allow_html=True)