import streamlit as stimport streamlit as st =========================
# PREP DATA
# =========================
def _prepare(df):
    df = df.copy()
    df.columns = df.columns.astype(str).str.strip()

    df["Activity ID"] = df["Activity ID"].astype(str).str.strip()

    for col in ["Finish"]:
        df[col] = (
            df[col]
            .astype(str)
            .str.replace(r"[A\*]", "", regex=True)
            .str.strip()
        )
        df[col] = pd.to_datetime(df[col], errors="coerce")

    return df


# =========================
# CONTROLLED DELIVERABLE DETECTION ✅
# =========================
def is_deliverable(row):

    name = str(row.get("Activity Name", "")).lower()

    # ✅ Include real deliverables
    include = [
        "submission",
        "completion",
        "report",
        "hazop",
        "freeze",
        "review"   # ✅ added safely
    ]

    # ✅ Remove engineering / noise tasks
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

    # ✅ Must be milestone-like
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
        st.error("❌ SnapshotDate column missing (check loader)")
        return pd.DataFrame(), None, None

    # ✅ Baseline & Forecast selection
    baseline_date = df["SnapshotDate"].min()
    forecast_date = df["SnapshotDate"].max()

    baseline_df = df[df["SnapshotDate"] == baseline_date]
    forecast_df = df[df["SnapshotDate"] == forecast_date]

    # ✅ Filter real deliverables only
    baseline_df = baseline_df[baseline_df.apply(is_deliverable, axis=1)]
    forecast_df = forecast_df[forecast_df.apply(is_deliverable, axis=1)]

    # ✅ Merge baseline vs forecast
    merged = pd.merge(
        baseline_df[["Activity Name", "Finish"]],
        forecast_df[["Activity Name", "Finish"]],
        on="Activity Name",
        how="outer",
        suffixes=("_Baseline", "_Forecast")
    )

    merged["Finish_Baseline"] = pd.to_datetime(
        merged["Finish_Baseline"], errors="coerce"
    )
    merged["Finish_Forecast"] = pd.to_datetime(
        merged["Finish_Forecast"], errors="coerce"
    )

    # ✅ Delta calculation
    merged["Δ Change (days)"] = (
        merged["Finish_Forecast"] - merged["Finish_Baseline"]
    ).dt.days

    merged = merged.rename(columns={
        "Activity Name": "Deliverable",
        "Finish_Baseline": "Baseline Finish",
        "Finish_Forecast": "Forecast Finish"
    })

    # ✅ Remove rows with no usable comparison
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
        st.warning("⚠️ No deliverables identified")
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

    # =========================
    # STATUS
    # =========================
    def status(row):
        delta = row["Δ Change (days)"]

        if pd.isna(delta):
            return ""
        elif delta > 7:
            return "🔴 Delayed"
        elif delta > 0:
            return "🟠 Slight Delay"
        else:
            return "🟢 On / Ahead"

    ms_df["Status"] = ms_df.apply(status, axis=1)

    # =========================
    # KPI ROW
    # =========================
    col1, col2, col3 = st.columns(3)

    late = (ms_df["Δ Change (days)"] > 7).sum()
    slight = ((ms_df["Δ Change (days)"] > 0) & (ms_df["Δ Change (days)"] <= 7)).sum()
    on_track = (ms_df["Δ Change (days)"] <= 0).sum()

    col1.metric("🔴 Delayed", int(late))
    col2.metric("🟠 Slight Delay", int(slight))
    col3.metric("🟢 On / Ahead", int(on_track))

    # =========================
    # SORT (worst first)
    # =========================
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
            return "background-color:#ff9800;color:black;font-weight:bold"
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
        .set_table_styles([
            {
                "selector": "th",
                "props": [
                    ("background-color", "#2b3a55"),
                    ("color", "white"),
                    ("font-weight", "600"),
                    ("padding", "10px"),
                    ("text-transform", "uppercase")
                ]
            },
            {
                "selector": "td",
                "props": [
                    ("background-color", "#1c2233"),
                    ("color", "#f1f1f1"),
                    ("padding", "8px")
                ]
            }
        ])
        .map(colour_delta, subset=["Δ Change (days)"])
        .map(colour_status, subset=["Status"])
    )

    st.markdown(styled.to_html(), unsafe_allow_html=True)
import pandas as pd


