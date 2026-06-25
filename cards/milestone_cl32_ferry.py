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

    # ✅ Deliverables only
    df_deliv = df_latest[df_latest["Activity Name"].apply(is_deliverable)].copy()

    if df_deliv.empty:
        st.warning("⚠️ No deliverables found")
        return

    # ✅ Clean fields
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
    # ✅ DISCIPLINE FROM CODE
    # =========================
    def get_disc(code):
        code = str(code)
        if "CIV" in code: return "CIV"
        if "MEC" in code: return "MEC"
        if "PRO" in code: return "PRO"
        if "EICA" in code: return "EICA"
        if "GEO" in code: return "GEO"
        if "3D" in code: return "BIM"
        if "CSD" in code: return "CSD"
        if "REV" in code: return "REV"
        return ""

    merged["Discipline"] = merged["Activity ID"].apply(get_disc)

    merged["Deliverable"] = merged.apply(
        lambda r: f"<span style='color:#94a3b8'>[{r['Discipline']}]</span> {r['Deliverable']}"
        if r["Discipline"] else r["Deliverable"],
        axis=1
    )

    # =========================
    # ✅ WORKING DAYS Δ
    # =========================
    start_dt = pd.to_datetime(merged["Baseline Finish"], errors="coerce")
    end_dt = pd.to_datetime(merged["Forecast Finish"], errors="coerce")

    valid = start_dt.notna() & end_dt.notna()
    merged["Δ Change (days)"] = 0

    merged.loc[valid, "Δ Change (days)"] = np.busday_count(
        start_dt[valid].values.astype("datetime64[D]"),
        end_dt[valid].values.astype("datetime64[D]")
    )

    merged["Progress %"] = merged["Progress %"].fillna(0).astype(int)
    merged["Δ Change (days)"] = merged["Δ Change (days)"].astype(int)

    # =========================
    # ✅ STATUS
    # =========================
    def status(r):
        if r["Progress %"] >= 100:
            return "🟢 Completed"
        elif r["Δ Change (days)"] > 0:
            return "🔴 Slipped"
        return "🟡 On Track"

    merged["Status"] = merged.apply(status, axis=1)

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

    # ✅ ✅ ✅ SAFE COLUMN SELECTION (FIXES DISAPPEARING TABLE)
    final_cols = [
        "Deliverable",
        baseline_label,
        forecast_label,
        "Progress %",
        "Δ Change (days)",
        "Status"
    ]

    final_cols = [c for c in final_cols if c in merged.columns]
    merged = merged[final_cols]

    # =========================
    # ✅ TABLE DISPLAY
    # =========================
    styled = (
        merged.style
        .set_table_styles([
            {"selector": "thead th", "props": [
                ("background-color", "#082f49"),
                ("color", "white"),
                ("border", "1px solid #334155")
            ]},
            {"selector": "tbody td", "props": [
                ("background-color", "#0f172a"),
                ("color", "white"),
                ("border", "1px solid #334155")
            ]}
        ])
    )

    st.markdown("### 📊 Deliverables Performance CL32")
    st.markdown(styled.to_html(escape=False), unsafe_allow_html=True)