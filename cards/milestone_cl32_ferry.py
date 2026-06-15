import streamlit as st
import pandas as pd


# =========================
# CORE DELIVERABLE IDS ✅
# =========================
CORE_DELIVERABLE_IDS = [
    "FER-CD-1010",

    "FER-PD-1000",
    "FER-PD-1010",
    "FER-PD-1020",
    "FER-PD-1030",

    "FER-REV-1000",
    "FER-REV-1010",
    "FER-REV-1020",
    "FER-REV-1030",
    "FER-REV-1040",
    "FER-REV-1050",

    "FER-GEO-1010",
    "FER-GEO-1020",
]


# =========================
# PREP DATA
# =========================
def _prepare(df):
    df = df.copy()
    df.columns = df.columns.astype(str).str.strip()

    df["Activity ID"] = df["Activity ID"].astype(str).str.strip()

    # Clean Finish
    df["Finish"] = (
        df["Finish"]
        .astype(str)
        .str.replace(r"[A\*]", "", regex=True)
        .str.strip()
    )
    df["Finish"] = pd.to_datetime(df["Finish"], errors="coerce")

    # Clean progress
    if "Activity % Complete" in df.columns:
        df["Activity % Complete"] = pd.to_numeric(
            df["Activity % Complete"], errors="coerce"
        )

    return df


# =========================
# DYNAMIC NEW DELIVERABLES ✅
# =========================
def is_new_deliverable(row):

    activity_id = str(row.get("Activity ID", "")).strip()
    name = str(row.get("Activity Name", "")).lower()

    valid_prefixes = ["FER-PD", "FER-REV", "FER-GEO", "FER-CD"]

    prefix_match = any(activity_id.startswith(p) for p in valid_prefixes)

    keyword_match = any(k in name for k in [
        "submission",
        "review",
        "completion"
    ])

    is_milestone = (
        row.get("Remaining Duration", None) == 0
        and pd.notna(row.get("Finish", None))
    )

    return prefix_match and keyword_match and is_milestone


# =========================
# FINAL DELIVERABLE FILTER ✅
# =========================
def is_deliverable(row):

    activity_id = str(row.get("Activity ID", "")).strip()

    # ✅ Always include core items
    if activity_id in CORE_DELIVERABLE_IDS:
        return True

    # ✅ Allow new valid deliverables
    return is_new_deliverable(row)


# =========================
# EXTRACT
# =========================
def extract_milestones(df):

    df = _prepare(df)

    if "SnapshotDate" not in df.columns:
        st.error("❌ SnapshotDate missing")
        return pd.DataFrame(), None, None

    # ✅ Baseline & Forecast
    dates = sorted(df["SnapshotDate"].dropna().unique())
    baseline_date = dates[0]
    forecast_date = dates[-1]

    baseline_df = df[df["SnapshotDate"] == baseline_date]
    forecast_df = df[df["SnapshotDate"] == forecast_date]

    # ✅ Filter
    baseline_df = baseline_df[baseline_df.apply(is_deliverable, axis=1)]
    forecast_df = forecast_df[forecast_df.apply(is_deliverable, axis=1)]

    # ✅ Merge (progress = latest only)
    merged = pd.merge(
        baseline_df[["Activity ID", "Activity Name", "Finish"]],
        forecast_df[["Activity ID", "Finish", "Activity % Complete"]],
        on="Activity ID",
        how="outer",
        suffixes=("_Baseline", "_Forecast")
    )

    # ✅ Clean
    merged["Finish_Baseline"] = pd.to_datetime(merged["Finish_Baseline"], errors="coerce")
    merged["Finish_Forecast"] = pd.to_datetime(merged["Finish_Forecast"], errors="coerce")

    merged["Activity % Complete"] = pd.to_numeric(
        merged["Activity % Complete"], errors="coerce"
    )

    # ✅ Delta
    merged["Δ Change (days)"] = (
        merged["Finish_Forecast"] - merged["Finish_Baseline"]
    ).dt.days

    # ✅ Rename
    merged = merged.rename(columns={
        "Activity Name": "Deliverable",
        "Finish_Baseline": "Baseline Finish",
        "Finish_Forecast": "Forecast Finish",
        "Activity % Complete": "Progress %"
    })

    # ✅ Remove empty rows
    merged = merged[
        merged["Baseline Finish"].notna() | merged["Forecast Finish"].notna()
    ]

    return merged, baseline_date, forecast_date


# =========================
# RENDER
# =========================
def render_milestone_table(df):

    ms_df, baseline_date, forecast_date = extract_milestones(df)

    if ms_df.empty:
        st.warning("⚠️ No deliverables found")
        return

    # ✅ Labels
    baseline_label = f"Baseline ({baseline_date.strftime('%b %Y')})"
    forecast_label = f"Forecast ({forecast_date.strftime('%b %Y')})"

    ms_df = ms_df.rename(columns={
        "Baseline Finish": baseline_label,
        "Forecast Finish": forecast_label
    })

    # ✅ Format dates
    ms_df[baseline_label] = pd.to_datetime(ms_df[baseline_label]).dt.strftime("%d-%b-%Y")
    ms_df[forecast_label] = pd.to_datetime(ms_df[forecast_label]).dt.strftime("%d-%b-%Y")

    # ✅ Progress (latest only)
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

    # ✅ Sort
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