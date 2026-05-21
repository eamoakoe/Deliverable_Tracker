import streamlit as st
import pandas as pd


# =========================
# ✅ GLOBAL THEME OVERRIDE =========================# ✅ GLOBAL THEME OVERRIDE
st.markdown("""
<style>

/* App background */
.stApp {
    background-color: #0b1f17;
}

/* Headers */
h1, h2, h3 {
    color: #22c55e !important;
}

/* Text */
p, div {
    color: #d1fae5;
}

/* Metric / alerts */
[data-testid="stMetric"] {
    background-color: #0f2a1d;
    border-radius: 10px;
    padding: 10px;
}

/* Table header */
thead tr th {
    background-color: #14532d !important;
    color: white !important;
}

/* Table cells */
tbody tr td {
    background-color: #0f2a1d !important;
    color: #ecfdf5 !important;
}

/* Custom Header Card */
.green-header {
    background-color: #0f2a1d;
    padding: 20px;
    border-radius: 12px;
    border-left: 6px solid #16a34a;
    margin-bottom: 15px;
}

.green-header h2 {
    color: #22c55e !important;
    margin-bottom: 5px;
}

.green-header p {
    color: #bbf7d0 !important;
    font-size: 14px;
    margin: 0;
}

</style>
""", unsafe_allow_html=True)


# =========================
# PREP DATA
# =========================
def _prepare(df):
    df = df.copy()

    df.columns = df.columns.astype(str).str.strip()

    df["Start"] = pd.to_datetime(df["Start"], errors="coerce")
    df["Finish"] = pd.to_datetime(df["Finish"], errors="coerce")
    df["BL1 Finish"] = pd.to_datetime(df["BL1 Finish"], errors="coerce")

    df["Total Float"] = pd.to_numeric(df["Total Float"], errors="coerce")

    df["Activity % Complete"] = (
        df["Activity % Complete"]
        .astype(str)
        .str.replace("%", "", regex=False)
    )

    df["Activity % Complete"] = pd.to_numeric(
        df["Activity % Complete"], errors="coerce"
    ).fillna(0)

    df["Change (days)"] = (
        (df["Finish"] - df["BL1 Finish"])
        .dt.days
        .fillna(0)
        .astype(int)
    )

    return df


# =========================
# FILTER NEXT 7 DAYS
# =========================
def _get_next7days(df):
    df = _prepare(df)

    today = pd.Timestamp.today().normalize()
    lookahead = today + pd.Timedelta(days=7)

    df = df[
        (df["Finish"] >= today) &
        (df["Finish"] <= lookahead)
    ].copy()

    return df.sort_values("Finish")


# =========================
# MAIN RENDER
# =========================
def render_next7days_table(df):

    df = _get_next7days(df)

    # =========================
    # ✅ HEADER (FIXED)
    # =========================
    st.markdown("""
    <div class="green-header">
        <h2>📊 CLAUSE 32 (CL32) – MAY PROGRAMME</h2>
        <p>
            Lookahead: Activities Issuing in Next 7 Days<br>
            Comparison of <b>CL32 May Baseline</b> vs <b>Current Forecast Finish</b>
        </p>
    </div>
    """, unsafe_allow_html=True)

    # =========================
    # STATUS MESSAGE
    # =========================
    if df.empty:
        st.success("✅ No activities issuing in the next 7 days")
        return

    late_flag = (df["Change (days)"] < 0).any()
    risk_flag = ((df["Activity % Complete"] < 100) & (df["Total Float"] <= 0)).any()

    if late_flag or risk_flag:
        st.warning("⚠️ Some activities issuing in the next 7 days are behind or at risk")
    else:
        st.info("✅ Activities are aligned with programme")

    # =========================
    # TABLE
    # =========================
    display_df = df[[
        "Activity ID", "Activity Name", "BL1 Finish", "Finish",
        "Change (days)", "Total Float", "Activity % Complete", "Comments"
    ]].copy()

    display_df = display_df.rename(columns={
        "BL1 Finish": "Baseline Finish",
        "Finish": "Forecast Finish",
        "Change (days)": "Δ Change (days)",
        "Total Float": "Float",
        "Activity % Complete": "% Complete"
    })

    display_df["Baseline Finish"] = pd.to_datetime(
        display_df["Baseline Finish"]
    ).dt.strftime("%d-%b-%Y")

    display_df["Forecast Finish"] = pd.to_datetime(
        display_df["Forecast Finish"]
    ).dt.strftime("%d-%b-%Y")

    def status(row):
        if row["% Complete"] < 100 and row["Float"] <= 0:
            return "🔴 At Risk"
        elif row["Δ Change (days)"] < 0:
            return "🟠 Late"
        return "🟢 OK"

    display_df["Status"] = display_df.apply(status, axis=1)

    # =========================
    # TABLE STYLING
    # =========================
    def colour_change(val):
        if val < 0:
            return "background-color:#7f1d1d;color:white"
        elif val > 0:
            return "background-color:#14532d;color:white"
        return ""

    def colour_status(val):
        if "🔴" in val:
            return "background-color:#b00020;color:white"
        elif "🟠" in val:
            return "background-color:#f59e0b;color:black"
        return "background-color:#14532d;color:white"

    styled = display_df.style
    styled = styled.map(colour_change, subset=["Δ Change (days)"])
    styled = styled.map(colour_status, subset=["Status"])

    st.write(styled)
