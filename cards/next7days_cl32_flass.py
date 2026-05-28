import streamlit as st
import pandas as pd


# =========================
# SHARED FERRIES STYLE ✅
# =========================
def format_like_ferries(display_df):

    def colour_change(val):
        if val < 0:
            return "background-color:#7f1d1d;color:white;font-weight:bold"
        elif val > 0:
            return "background-color:#14532d;color:white;font-weight:bold"
        return "background-color:#374151;color:white"

    def colour_float(val):
        if pd.isna(val):
            return ""
        if val <= 0:
            return "background-color:#b00020;color:white"
        return ""

    def colour_status(val):
        if "🔴" in val:
            return "background-color:#b00020;color:white"
        elif "🟠" in val:
            return "background-color:#ff9800;color:black"
        elif "🟢" in val:
            return "background-color:#1e7e34;color:white"
        return ""

    def colour_risk(val):
        if "🔴" in val:
            return "background-color:#7f1d1d;color:white"
        elif "🟠" in val:
            return "background-color:#ff9800;color:black"
        elif "⚠️" in val:
            return "background-color:#facc15;color:black"
        elif "🟢" in val:
            return "background-color:#14532d;color:white"
        return ""

    styled = display_df.style.set_table_styles([
        {
            "selector": "th",
            "props": [
                ("background-color", "#2b3a55"),
                ("color", "white"),
                ("font-weight", "600"),
                ("padding", "10px")
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

    if "Δ Change vs CL32 May (days)" in display_df.columns:
        styled = styled.map(colour_change, subset=["Δ Change vs CL32 May (days)"])

    if "Float (Days)" in display_df.columns:
        styled = styled.map(colour_float, subset=["Float (Days)"])

    if "Status (CL32 May)" in display_df.columns:
        styled = styled.map(colour_status, subset=["Status (CL32 May)"])

    if "Risk (Forward Look)" in display_df.columns:
        styled = styled.map(colour_risk, subset=["Risk (Forward Look)"])

    return styled


# =========================
# PREP DATA (FLASS)
# =========================
def _prepare(df):
    df = df.copy()
    df.columns = df.columns.astype(str).str.strip()

    # ✅ Dates
    df["Start"] = pd.to_datetime(df.get("Start"), errors="coerce")
    df["Finish"] = pd.to_datetime(df.get("Finish"), errors="coerce")
    df["BL Project Finish"] = pd.to_datetime(df.get("BL Project Finish"), errors="coerce")

    # ✅ FLOAT (hours → days)
    if "Total Float(h)" in df.columns:
        float_series = pd.to_numeric(df["Total Float(h)"], errors="coerce")
    else:
        float_series = pd.Series(0, index=df.index)

    df["Float (Days)"] = float_series.fillna(0).apply(lambda x: int(round(x / 24)))

    # ✅ % COMPLETE
    if "Activity % Complete" in df.columns:
        pct_series = pd.to_numeric(df["Activity % Complete"], errors="coerce")
    else:
        pct_series = pd.Series(0, index=df.index)

    df["% Complete"] = pct_series.fillna(0).astype(int)

    # ✅ DELTA
    if "Variance - BL Project Finish Date(h)" in df.columns:
        var_series = pd.to_numeric(df["Variance - BL Project Finish Date(h)"], errors="coerce")

        df["Δ Change vs CL32 May (days)"] = (
            var_series.fillna(0).apply(lambda x: int(round(x / 24)))
        )
    else:
        df["Δ Change vs CL32 May (days)"] = (
            (df["Finish"] - df["BL Project Finish"]).dt.days.fillna(0).astype(int)
        )

    return df


# =========================
# NEXT 7 DAYS FILTER
# =========================
def _get_next7days(df):

    df = _prepare(df)

    today = pd.Timestamp.today().normalize()
    lookahead = today + pd.Timedelta(days=7)

    df = df[
        (df["Finish"] >= today) &
        (df["Finish"] <= lookahead)
    ].copy()

    # ✅ Deliverables filter
    deliverable_ids = ["-KD-", "-DRIA-", "-DDST-", "-DDGD-"]
    df = df[df["Activity ID"].str.contains("|".join(deliverable_ids), na=False)]

    # ✅ Remove long tasks
    if "Remaining Duration" in df.columns:
        df["Remaining Duration"] = pd.to_numeric(df["Remaining Duration"], errors="coerce")
        df = df[df["Remaining Duration"] <= 10]

    # ✅ Keywords
    keywords = ["Completion", "Review", "Design", "Specification", "Assessment", "Report", "Drawing"]
    df = df[df["Activity Name"].str.contains("|".join(keywords), case=False, na=False)]

    return df.sort_values("Finish")


# =========================
# MAIN RENDER
# =========================
def render_next7days_table(df):

    df = _get_next7days(df)

    if df.empty:
        st.success("✅ No deliverables due in the next 7 days")
        return

    # ✅ FLAGS
    late_flag = (df["Δ Change vs CL32 May (days)"] > 0).any()
    risk_flag = ((df["% Complete"] < 100) & (df["Float (Days)"] <= 0)).any()

    if late_flag or risk_flag:
        st.warning("⚠️ Key deliverables in the next 7 days are delayed or at risk")
    else:
        st.info("✅ Deliverables in the next 7 days are on track")

    # =========================
    # TABLE
    # =========================
    display_df = df[[
        "Activity ID",
        "Activity Name",
        "BL Project Finish",
        "Finish",
        "Δ Change vs CL32 May (days)",
        "Float (Days)",
        "% Complete"
    ]].copy()

    display_df = display_df.rename(columns={
        "BL Project Finish": "Baseline Finish (CL32 May)",
        "Finish": "Forecast Finish (CL32 May)"
    })

    # ✅ Format dates
    display_df["Baseline Finish (CL32 May)"] = pd.to_datetime(
        display_df["Baseline Finish (CL32 May)"]
    ).dt.strftime("%d-%b-%Y")

    display_df["Forecast Finish (CL32 May)"] = pd.to_datetime(
        display_df["Forecast Finish (CL32 May)"]
    ).dt.strftime("%d-%b-%Y")

    # =========================
    # STATUS (MATCH FERRIES)
    # =========================
    def status(row):
        if row["% Complete"] < 100 and row["Float (Days)"] <= 0:
            return "🔴 At Risk"
        elif row["Δ Change vs CL32 May (days)"] > 0:
            return "🟠 Late"
        return "🟢 OK"

    display_df["Status (CL32 May)"] = display_df.apply(status, axis=1)

    # =========================
    # RISK (MATCH FERRIES)
    # =========================
    def risk(row):
        if row["% Complete"] < 100 and row["Float (Days)"] <= 0:
            return "🔴 High Risk"
        elif row["% Complete"] < 75 and row["Δ Change vs CL32 May (days)"] > 0:
            return "🟠 Behind Progress"
        elif row["% Complete"] >= 90 and row["Δ Change vs CL32 May (days)"] > 0:
            return "⚠️ Near Complete but Late"
        return "🟢 Low Risk"

    display_df["Risk (Forward Look)"] = display_df.apply(risk, axis=1)

    # =========================
    # APPLY SHARED STYLE ✅
    # =========================
    styled = format_like_ferries(display_df)

    st.markdown(styled.to_html(), unsafe_allow_html=True)
