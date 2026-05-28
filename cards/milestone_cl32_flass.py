import streamlit as st
import pandas as pd


# =========================
# PREP DATA
# =========================
def _prepare(df):
    df = df.copy()
    df.columns = df.columns.astype(str).str.strip()

    df["Activity ID"] = df["Activity ID"].astype(str).str.strip()

    # ✅ Clean dates
    for col in ["Finish", "BL Project Finish"]:
        if col in df.columns:
            df[col] = (
                df[col]
                .astype(str)
                .str.replace(r"[A\*]", "", regex=True)
                .str.strip()
            )
            df[col] = pd.to_datetime(df[col], errors="coerce")

    # ✅ Numeric conversions
    for col in [
        "Activity % Complete",
        "Total Float(h)",
        "Variance - BL Project Finish Date(h)"
    ]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


# =========================
# DELIVERABLE MAP
# =========================
FLASS_DELIVERABLES = {
    "🔥 DESIGN FREEZE – APPROVED": ["AR-FL-DRIA-1040"],
    "Planned Completion": ["AR-FL-KD-1020"],
    "Project Completion": ["AR-FL-KD-1040"],
    "GI Report & Constructability Review": ["AR-FL-DRIA-1060"],
    "Design Review Complete": ["AR-FL-DDST-1030"],
    "General Ground Model": ["AR-FL-DDGD-1000"],
    "Pile Design Complete": ["AR-FL-DDGD-1020"],
    "Ground Movement Assessment": ["AR-FL-DDGD-1030"],
    "Specification Issued": ["AR-FL-DDGD-1040"],
    "Pile GA Drawing": ["AR-FL-DDGD-1060"],
    "Pile GA + Specification Issued": ["AR-FL-DDGD-1070"],
}


# =========================
# STATUS LOGIC
# =========================
def get_status(row):
    today = pd.Timestamp.today()

    if row["Progress (%)"] == 100:
        if row["Δ (Days)"] and row["Δ (Days)"] > 0:
            return "🔴 Completed Late"
        return "✅ Completed"

    if pd.isna(row["Forecast Finish"]):
        return "⚠️ No Forecast"

    if row["Progress (%)"] == 0 and pd.notna(row["Baseline Finish"]) and today > row["Baseline Finish"]:
        return "🔴 Late / Not Started"

    if row["Δ (Days)"] and row["Δ (Days)"] > 0:
        return "🔴 Delayed"
    elif row["Float (Days)"] <= 0:
        return "🟠 Critical"
    return "🟢 On Track"


# =========================
# EXTRACT DELIVERABLES
# =========================
def extract_milestones(df):

    df = _prepare(df)
    milestones = []

    for name, ids in FLASS_DELIVERABLES.items():

        filtered = df[
            df["Activity ID"].str.contains("|".join(ids), na=False)
        ].copy()

        if filtered.empty:
            continue

        finish_col = "Finish"
        base_col = "BL Project Finish"

        filtered["Sort Date"] = filtered[finish_col].fillna(filtered[base_col])
        filtered = filtered.sort_values("Sort Date")

        row = filtered.iloc[-1]

        # ✅ Delta
        delta = None
        if "Variance - BL Project Finish Date(h)" in df.columns:
            variance_hours = row.get("Variance - BL Project Finish Date(h)")
            if pd.notna(variance_hours):
                delta = int(round(variance_hours / 24))
        elif pd.notna(row[finish_col]) and pd.notna(row[base_col]):
            delta = int((row[finish_col] - row[base_col]).days)

        # ✅ Float
        float_days = row.get("Total Float(h)")
        float_days = int(round(float_days / 24)) if pd.notna(float_days) else 0

        milestones.append({
            "Deliverable": name,
            "Activity": row["Activity Name"],
            "Baseline Finish": row.get(base_col),
            "Forecast Finish": row.get(finish_col),
            "Δ (Days)": delta,
            "Progress (%)": row.get("Activity % Complete", 0),
            "Float (Days)": float_days,
        })

    ms_df = pd.DataFrame(milestones)

    if not ms_df.empty:
        ms_df["Status"] = ms_df.apply(get_status, axis=1)

    return ms_df


# =========================
# RENDER TABLE
# =========================
def render_milestone_table(df):

    ms_df = extract_milestones(df)

    if ms_df.empty:
        st.warning("⚠️ No deliverables identified")
        return

    # =========================
    # FORMAT DATES
    # =========================
    for col in ["Baseline Finish", "Forecast Finish"]:
        ms_df[col] = pd.to_datetime(ms_df[col]).dt.strftime("%d-%b-%Y")

    # =========================
    # KPI SUMMARY
    # =========================
    late = ms_df["Status"].str.contains("Late|Delayed", na=False).sum()
    critical = ms_df["Status"].str.contains("Critical", na=False).sum()
    on_track = ms_df["Status"].str.contains("Track", na=False).sum()
    completed = ms_df["Status"].str.contains("Completed", na=False).sum()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🔴 Late/Delayed", late)
    col2.metric("🟠 Critical", critical)
    col3.metric("🟢 On Track", on_track)
    col4.metric("✅ Completed", completed)

    # =========================
    # SORT (worst first)
    # =========================
    ms_df = ms_df.sort_values(
        by=["Δ (Days)", "Float (Days)"],
        ascending=[False, True]
    )

    # =========================
    # CLEAN STATUS
    # =========================
    def simplify_status(val):
        if "Late" in val or "Delayed" in val:
            return "🔴 Issue"
        elif "Critical" in val:
            return "🟠 Critical"
        elif "Completed" in val:
            return "✅ Completed"
        return "🟢 On Track"

    ms_df["Status"] = ms_df["Status"].apply(simplify_status)

    # =========================
    # STYLING (DARK THEME)
    # =========================
    def colour_delta(val):
        if pd.isna(val):
            return "background-color:#374151;color:white"
        if val > 0:
            return "background-color:#7f1d1d;color:white;font-weight:bold"
        elif val < 0:
            return "background-color:#14532d;color:white;font-weight:bold"
        return "background-color:#374151;color:white"

    def colour_status(val):
        if "🔴" in val:
            return "background-color:#b00020;color:white"
        elif "🟠" in val:
            return "background-color:#ff9800;color:black"
        elif "✅" in val:
            return "background-color:#1e7e34;color:white"
        elif "🟢" in val:
            return "background-color:#14532d;color:white"
        return ""

    def colour_float(val):
        if val <= 0:
            return "background-color:#b00020;color:white"
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
        .map(colour_delta, subset=["Δ (Days)"])
        .map(colour_status, subset=["Status"])
        .map(colour_float, subset=["Float (Days)"])
    )

    st.markdown(styled.to_html(), unsafe_allow_html=True)
