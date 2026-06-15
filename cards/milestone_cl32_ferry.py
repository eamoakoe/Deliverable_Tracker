import streamlit as st
import pandas as pd


# =========================
# PREP DATA
# =========================
def _prepare(df):
    df = df.copy()
    df.columns = df.columns.astype(str).str.strip()

    df["Activity ID"] = df["Activity ID"].astype(str).str.strip()

    # Clean Finish dates
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
# DELIVERABLE FILTER
# =========================
def is_deliverable(row):

    name = str(row.get("Activity Name", "")).lower()

    include = [
        "submission",
        "completion",
        "report",
        "hazop",
        "freeze",
        "review"
    ]

    exclude = [
        "design complete",
        "modelling",
        "model",
        "drawing",
        "build",
        "setup",
        "optioneering",
        "calculation"
    ]

    is_milestone = (
        row.get("Remaining Duration", None) == 0
        and pd.notna(row.get("Finish", None))
    )

    include_match = any(k in name for k in include)
    exclude_match = any(k in name for k in exclude)

    return is_milestone and include_match and not exclude_match


# =========================
# EXTRACT MILESTONES
# =========================
def extract_milestones(df):

    df = _prepare(df)

    if "SnapshotDate" not in df.columns:
        st.error("❌ SnapshotDate missing")
        return pd.DataFrame(), None, None

    # ✅ Baseline + Forecast selection
    dates = sorted(df["SnapshotDate"].dropna().unique())
    baseline_date = dates[0]
    forecast_date = dates[-1]

    baseline_df = df[df["SnapshotDate"] == baseline_date]
    forecast_df = df[df["SnapshotDate"] == forecast_date]

    # ✅ Filter deliverables
    baseline_df = baseline_df[baseline_df.apply(is_deliverable, axis=1)]
    forecast_df = forecast_df[forecast_df.apply(is_deliverable, axis=1)]

    # ✅ Merge (progress ONLY from latest CL32)
    merged = pd.merge(
        baseline_df[["Activity Name", "Finish"]],
        forecast_df[["Activity Name", "Finish", "Activity % Complete"]],
        on="Activity Name",
        how="outer"
    )

    # ✅ Clean fields
    merged["Finish_x"] = pd.to_datetime(merged["Finish_x"], errors="coerce")
    merged["Finish_y"] = pd.to_datetime(merged["Finish_y"], errors="coerce")

    merged["Activity % Complete"] = pd.to_numeric(
        merged["Activity % Complete"], errors="coerce"
    )

    # ✅ Delta
    merged["Δ Change (days)"] = (
        merged["Finish_y"] - merged["Finish_x"]
    ).dt.days

    # ✅ Rename columns
    merged = merged.rename(columns={
        "Activity Name": "Deliverable",
        "Finish_x": "Baseline Finish",
        "Finish_y": "Forecast Finish",
        "Activity % Complete": "Progress %"
    })

    # ✅ Remove empty rows
    merged = merged[
        merged["Baseline Finish"].notna() | merged["Forecast Finish"].notna()
    ]

    return merged, baseline_date, forecast_date


# =========================
# RENDER TABLE
# =========================
def render_milestone_table(df):

    ms_df, baseline_date, forecast_date = extract_milestones(df)

    if ms_df.empty:
        st.warning("⚠️ No deliverables found")
        return

    # ✅ Dynamic headers
    baseline_label = f"Baseline ({baseline_date.strftime('%b %Y')})"
    forecast_label = f"Forecast ({forecast_date.strftime('%b %Y')})"

    ms_df = ms_df.rename(columns={
        "Baseline Finish": baseline_label,
        "Forecast Finish": forecast_label
    })

    # ✅ Format dates
    ms_df[baseline_label] = pd.to_datetime(
        ms_df[baseline_label]
    ).dt.strftime("%d-%b-%Y")

    ms_df[forecast_label] = pd.to_datetime(
        ms_df[forecast_label]
    ).dt.strftime("%d-%b-%Y")

    # ✅ Format Progress (latest only)
    ms_df["Progress %"] = ms_df["Progress %"].fillna(0).round(0).astype(int)

    # =========================
    # STATUS (based on delay only)
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
