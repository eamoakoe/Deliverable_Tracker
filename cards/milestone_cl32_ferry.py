import streamlit as st
import pandas as pd


# =========================
# PREP DATA
# =========================
def _prepare(df):
    df = df.copy()
    df.columns = df.columns.astype(str).str.strip()

    df["Activity ID"] = df["Activity ID"].astype(str).str.strip()

    # Clean dates
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

    # ✅ Identify baseline & forecast
    dates = sorted(df["SnapshotDate"].dropna().unique())
    baseline_date = dates[0]
    forecast_date = dates[-1]

    baseline_df = df[df["SnapshotDate"] == baseline_date]
    forecast_df = df[df["SnapshotDate"] == forecast_date]

    # ✅ Filter deliverables
    baseline_df = baseline_df[baseline_df.apply(is_deliverable, axis=1)]
    forecast_df = forecast_df[forecast_df.apply(is_deliverable, axis=1)]

    # ✅ Merge including progress
    merged = pd.merge(
        baseline_df[["Activity Name", "Finish", "Activity % Complete"]],
        forecast_df[["Activity Name", "Finish", "Activity % Complete"]],
        on="Activity Name",
        how="outer",
        suffixes=("_Baseline", "_Forecast")
    )

    # ✅ Clean fields
    merged["Finish_Baseline"] = pd.to_datetime(merged["Finish_Baseline"], errors="coerce")
    merged["Finish_Forecast"] = pd.to_datetime(merged["Finish_Forecast"], errors="coerce")

    merged["Activity % Complete_Baseline"] = pd.to_numeric(
        merged["Activity % Complete_Baseline"], errors="coerce"
    )
    merged["Activity % Complete_Forecast"] = pd.to_numeric(
        merged["Activity % Complete_Forecast"], errors="coerce"
    )

    # ✅ Calculate deltas
    merged["Δ Change (days)"] = (
        merged["Finish_Forecast"] - merged["Finish_Baseline"]
    ).dt.days

    merged["Δ Progress (%)"] = (
        merged["Activity % Complete_Forecast"]
        - merged["Activity % Complete_Baseline"]
    )

    # ✅ Rename
    merged = merged.rename(columns={
        "Activity Name": "Deliverable",
        "Finish_Baseline": "Baseline Finish",
        "Finish_Forecast": "Forecast Finish",
        "Activity % Complete_Baseline": "Baseline %",
        "Activity % Complete_Forecast": "Forecast %"
    })

    # Remove empty rows
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

    # ✅ Dynamic labels
    baseline_label = f"Baseline ({baseline_date.strftime('%b %Y')})"
    forecast_label = f"Forecast ({forecast_date.strftime('%b %Y')})"

    ms_df = ms_df.rename(columns={
        "Baseline Finish": baseline_label,
        "Forecast Finish": forecast_label
    })

    # ✅ Format dates
    ms_df[baseline_label] = pd.to_datetime(ms_df[baseline_label]).dt.strftime("%d-%b-%Y")
    ms_df[forecast_label] = pd.to_datetime(ms_df[forecast_label]).dt.strftime("%d-%b-%Y")

    # ✅ Format %
    ms_df["Baseline %"] = ms_df["Baseline %"].fillna(0).round(0).astype(int)
    ms_df["Forecast %"] = ms_df["Forecast %"].fillna(0).round(0).astype(int)
    ms_df["Δ Progress (%)"] = ms_df["Δ Progress (%)"].fillna(0).round(0).astype(int)

    # =========================
    # COMBINED STATUS ✅
    # =========================
    def status(row):

        d = row["Δ Change (days)"]
        p = row["Δ Progress (%)"]

        if pd.isna(d) or pd.isna(p):
            return ""

        if d > 7 and p <= 0:
            return "🔴 Critical Delay"

        if d > 7 and p > 0:
            return "🟠 Delayed but Recovering"

        if 0 < d <= 7:
            return "🟠 Slight Delay"

        if p < 0:
            return "🔴 Regressing"

        if p == 0:
            return "🟠 No Progress"

        if d <= 0 and p > 0:
            return "🟢 On Track"

        return "🟢 Stable"

    ms_df["Status"] = ms_df.apply(status, axis=1)

    # =========================
    # KPI ROW
    # =========================
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("🔴 Critical", int((ms_df["Status"] == "🔴 Critical Delay").sum()))
    col2.metric("🟠 Recovering", int((ms_df["Status"] == "🟠 Delayed but Recovering").sum()))
    col3.metric("🟢 On Track", int((ms_df["Status"] == "🟢 On Track").sum()))
    col4.metric("🟠 Stalled", int((ms_df["Status"] == "🟠 No Progress").sum()))

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

    def colour_progress(val):
        if val > 0:
            return "background-color:#14532d;color:white"
        elif val < 0:
            return "background-color:#7f1d1d;color:white"
        return "background-color:#374151;color:white"

    def colour_status(val):
        if "Critical" in val:
            return "background-color:#7f1d1d;color:white"
        elif "Recovering" in val:
            return "background-color:#ff9800;color:black"
        elif "Slight" in val:
            return "background-color:#f59e0b;color:black"
        elif "No Progress" in val:
            return "background-color:#6b7280;color:white"
        elif "On Track" in val:
            return "background-color:#14532d;color:white"
        elif "Regressing" in val:
            return "background-color:#b00020;color:white"
        return ""

    styled = (
        ms_df.style
        .map(colour_delta, subset=["Δ Change (days)"])
        .map(colour_progress, subset=["Δ Progress (%)"])
        .map(colour_status, subset=["Status"])
    )

    st.markdown(styled.to_html(), unsafe_allow_html=True)