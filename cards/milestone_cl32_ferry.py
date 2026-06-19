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
    "GA &amp; Long sections",
    "Valve chamber standard detail",
    "Kiosk slab proposal",
    "Shaft penetrations",
    "Line sizing",
    "Mechanical calculations",
    "Pump system curve",
    "Basis of Design",
    "Outline P&amp;IDs",
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
    "MH01 &amp; MH02 Design",
    "Pipework from MHs to Shaft",
    "Valve Chamber",
    "Flowmeter Chamber",
    "Civils Pipe Design",
    "Tank kiosk enclosure foundation",
    "Assessment of exit details",
    "Routing &amp; Design",
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

    # ✅ Deliverables only (for metrics)
    df_deliv = df_latest[df_latest["Activity Name"].apply(is_deliverable)].copy()

    # ✅ Clean finish
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
    dates = sorted(df["SnapshotDate"].dropna().unique())
    baseline_date = dates[0]
    forecast_date = dates[-1]

    baseline_df = df[df["SnapshotDate"] == baseline_date]
    baseline_df = baseline_df[baseline_df["Activity Name"].apply(is_deliverable)]
    baseline_df = baseline_df.rename(columns={"Finish": "Baseline Finish"})

    merged = pd.merge(
        baseline_df[["Activity ID", "Activity Name", "Baseline Finish"]],
        df_deliv[["Activity ID", "Finish", "Activity % Complete"]],
        on="Activity ID",
        how="left"
    )

    merged = merged.rename(columns={
        "Activity Name": "Deliverable",
        "Finish": "Forecast Finish",
        "Activity % Complete": "Progress %"
    })

    # =========================
    # ✅ ADD HIERARCHY + COLOUR
    # =========================
    SECTION_COLORS = {
        "Optioneering Assessment": "#7C3AED",
        "3D Modelling": "#2563EB",
        "Concept Shaft Design": "#1D4ED8",
        "Outline Design Scope Freeze (Minimum Requirements)": "#F59E0B",
        "Civils Design": "#16A34A",
        "Mechanical Design": "#DC2626",
        "Process Design": "#0D9488",
        "Geotechnical": "#4B5563",
        "EICA Design": "#DB2777"
    }

    df_full = df[df["SnapshotDate"] == latest_date].copy()
    df_full["Activity ID"] = df_full["Activity ID"].fillna("").astype(str).str.strip()
    df_full["Is Summary"] = df_full["Activity ID"] == ""

    # Hierarchy level
    levels = []
    level = 0
    for _, row in df_full.iterrows():
        if row["Is Summary"]:
            level += 1
        levels.append(level)

    df_full["Level"] = levels

    # Discipline tracking
    df_full["Discipline"] = None
    current = None

    for i, row in df_full.iterrows():
        name = row["Activity Name"]
        if name in SECTION_COLORS:
            current = name
        df_full.at[i, "Discipline"] = current

    df_lookup = df_full[["Activity ID", "Level", "Discipline"]]
    merged = merged.merge(df_lookup, on="Activity ID", how="left")

    def format_deliverable(row):
        indent = "&nbsp;" * 6 * int(row["Level"]) if pd.notna(row["Level"]) else ""
        color = SECTION_COLORS.get(row["Discipline"], "#FFFFFF")
        return f"{indent}<span style='color:{color}'>{row['Deliverable']}</span>"

    merged["Deliverable"] = merged.apply(format_deliverable, axis=1)

    # =========================
    # ✅ DELTA
    # =========================
    start_dt = pd.to_datetime(merged["Baseline Finish"], errors="coerce")
    end_dt = pd.to_datetime(merged["Forecast Finish"], errors="coerce")

    valid_mask = start_dt.notna() & end_dt.notna()

    merged["Δ Change (days)"] = 0
    merged.loc[valid_mask, "Δ Change (days)"] = np.busday_count(
        start_dt[valid_mask].values.astype("datetime64[D]"),
        end_dt[valid_mask].values.astype("datetime64[D]")
    )

    merged["Δ Change (days)"] = merged["Δ Change (days)"].astype(int)
    merged["Progress %"] = merged["Progress %"].fillna(0).astype(int)

    # =========================
    # ✅ STATUS
    # =========================
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
    # ✅ FORMAT DATES
    # =========================
    merged["Baseline Finish"] = pd.to_datetime(
        merged["Baseline Finish"]
    ).dt.strftime("%d %B %Y")

    merged["Forecast Finish"] = pd.to_datetime(
        merged["Forecast Finish"]
    ).dt.strftime("%d %B %Y")

    baseline_label = f"Finish Date (CL32 {baseline_date.strftime('%B %Y')})"
    forecast_label = f"Finish Date (CL32 {forecast_date.strftime('%B %Y')})"

    merged = merged.rename(columns={
        "Baseline Finish": baseline_label,
        "Forecast Finish": forecast_label
    })

    # =========================
    # ✅ STYLE (UNCHANGED)
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
    st.markdown(styled.to_html(escape=False), unsafe_allow_html=True)