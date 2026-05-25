import streamlit as st
import pandas as pd


# =========================
# PREP DATA (FLASS VERSION)
# =========================
def _prepare(df):
    df = df.copy()
    df.columns = df.columns.astype(str).str.strip()

    # ✅ Clean Activity ID
    df["Activity ID"] = df["Activity ID"].astype(str).str.strip()

    # ✅ Handle Flass date fields
    for col in ["Finish", "BL Project Finish"]:
        if col in df.columns:
            df[col] = (
                df[col]
                .astype(str)
                .str.replace(r"[A\*]", "", regex=True)
                .str.strip()
            )
            df[col] = pd.to_datetime(df[col], errors="coerce")

    return df


# =========================
# ✅ FLASS DELIVERABLES
# =========================
FLASS_DELIVERABLES = {

    # 🔥 DESIGN FREEZE (CRITICAL)
    "🔥 DESIGN FREEZE – APPROVED": ["AR-FL-DRIA-1040"],

    # 🔴 Programme
    "Planned Completion": ["AR-FL-KD-1020"],
    "Project Completion": ["AR-FL-KD-1040"],

    # 🟡 Reports
    "GI Report & Constructability Review": ["AR-FL-DRIA-1060"],

    # 🔵 Design validation
    "Design Review Complete": ["AR-FL-DDST-1030"],

    # 🟣 Geotechnical / Piling outputs
    "General Ground Model": ["AR-FL-DDGD-1000"],
    "Pile Design Complete": ["AR-FL-DDGD-1020"],
    "Ground Movement Assessment": ["AR-FL-DDGD-1030"],

    # 🟠 Specifications + drawings
    "Specification Issued": ["AR-FL-DDGD-1040"],
    "Pile GA Drawing": ["AR-FL-DDGD-1060"],
    "Pile GA + Specification Issued": ["AR-FL-DDGD-1070"],
}


# =========================
# EXTRACT DELIVERABLES
# =========================
def extract_milestones(df):

    df = _prepare(df)

    milestones = []

    for name, ids in FLASS_DELIVERABLES.items():

        filtered = df[
            df["Activity ID"].str.contains(
                "|".join(ids),
                na=False
            )
        ].copy()

        if filtered.empty:
            continue

        # ✅ Use Finish or BL finish
        finish_col = "Finish" if "Finish" in df.columns else "BL Project Finish"
        base_col = "BL Project Finish"

        filtered["Sort Date"] = filtered[finish_col].fillna(filtered[base_col])

        filtered = filtered.sort_values("Sort Date")

        row = filtered.iloc[-1]

        # ✅ Variance (handle column mismatch)
        try:
            delta = int((row[finish_col] - row[base_col]).days)
        except:
            delta = 0

        milestones.append({
            "Deliverable": name,
            "Activity": row["Activity Name"],
            "Baseline Finish": row.get(base_col, None),
            "Forecast Finish": row.get(finish_col, None),
            "Δ (Days)": delta
        })

    ms_df = pd.DataFrame(milestones)

    if not ms_df.empty:
        ms_df["Δ (Days)"] = ms_df["Δ (Days)"].fillna(0).astype(int)

    return ms_df


# =========================
# RENDER TABLE
# =========================
def render_milestone_table(df):

    ms_df = extract_milestones(df)

    st.markdown("## 📦 FLASS – KEY DELIVERABLE TRACKING (CL32)")

    if ms_df.empty:
        st.warning("⚠️ No deliverables identified")
        return

    # ✅ Format dates safely
    for col in ["Baseline Finish", "Forecast Finish"]:
        if col in ms_df.columns:
            ms_df[col] = pd.to_datetime(ms_df[col]).dt.strftime("%d-%b-%Y")

    # ✅ Colour variance
    def colour_delta(val):
        if val < 0:
            return "background-color:#7f1d1d;color:white;font-weight:bold"
        elif val > 0:
            return "background-color:#14532d;color:white;font-weight:bold"
        return "background-color:#374151;color:white"

    styled = (
        ms_df.style
        .map(colour_delta, subset=["Δ (Days)"])
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