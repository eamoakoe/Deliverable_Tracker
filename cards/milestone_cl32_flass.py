import streamlit as st
import pandas as pd

# =========================
# PREP DATA
# =========================
def _prepare(df):
    df = df.copy()
    df.columns = df.columns.astype(str).str.strip()

    df["Activity ID"] = df["Activity ID"].astype(str).str.strip()

    # ✅ Clean date fields
    for col in ["Finish", "BL Project Finish"]:
        if col in df.columns:
            df[col] = (
                df[col]
                .astype(str)
                .str.replace(r"[A\*]", "", regex=True)
                .str.strip()
            )
            df[col] = pd.to_datetime(df[col], errors="coerce")

    # ✅ Ensure numeric fields
    for col in ["Activity % Complete", "Total Float(h)", "Variance - BL Project Finish Date(h)"]:
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

    # No forecast
    if pd.isna(row["Forecast Finish"]):
        return "⚠️ No Forecast"

    # Late + not started
    if row["Progress (%)"] == 0 and today > row["Baseline Finish"]:
        return "🔴 Late / Not Started"

    # Variance
    if row["Δ (Days)"] > 0:
        return "🔴 Delayed"
    elif row["Float (Days)"] <= 0:
        return "🟠 Critical"
    else:
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

        # ✅ Use Primavera variance if available
        if "Variance - BL Project Finish Date(h)" in df.columns:
            variance_hours = row.get("Variance - BL Project Finish Date(h)", 0)
            delta = round(variance_hours / 24, 1)
        else:
            if pd.notna(row[finish_col]) and pd.notna(row[base_col]):
                delta = (row[finish_col] - row[base_col]).days
            else:
                delta = None

        float_days = row.get("Total Float(h)", 0)
        float_days = float_days / 24 if pd.notna(float_days) else 0

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

    # ✅ Format dates
    for col in ["Baseline Finish", "Forecast Finish"]:
        if col in ms_df.columns:
            ms_df[col] = pd.to_datetime(ms_df[col]).dt.strftime("%d-%b-%Y")

    # ✅ Colour delta
    def colour_delta(val):
        if pd.isna(val):
            return "background-color:#374151;color:white"
        if val > 0:
            return "background-color:#7f1d1d;color:white;font-weight:bold"
        elif val < 0:
            return "background-color:#14532d;color:white;font-weight:bold"
        return "background-color:#374151;color:white"

    # ✅ Colour status
    def colour_status(val):
        if "Delayed" in val or "Late" in val:
            return "background-color:#7f1d1d;color:white"
        elif "Critical" in val:
            return "background-color:#78350f;color:white"
        elif "Track" in val:
            return "background-color:#14532d;color:white"
        return "background-color:#374151;color:white"

    styled = (
        ms_df.style
        .map(colour_delta, subset=["Δ (Days)"])
        .map(colour_status, subset=["Status"])
        .set_table_styles([
            {
                "selector": "th",
                "props": [
                    ("background-color", "#2b3a55"),
                    ("color", "white"),
                    ("font-weight", "600"),
                    ("padding", "10px"),
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
    )

    st.write(styled)
