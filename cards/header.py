import streamlit as st
from datetime import datetime
import pandas as pd


# =========================
# ✅ HELPERS
# =========================

def get_next_deliverable(df):

    df = df.copy()
    df["Finish"] = pd.to_datetime(df["Finish"], dayfirst=True, errors="coerce")

    if "Activity % Complete" in df.columns:
        df = df[df["Activity % Complete"] < 100]

    df = df[df["Finish"].notna()].sort_values("Finish")

    if not df.empty:
        row = df.iloc[0]
        finish = row["Finish"]
        today = pd.Timestamp.today().normalize()

        status = " 🔴" if finish < today else ""

        return f"{row['Activity Name']} – {finish.strftime('%d %b')}{status}"

    return "—"


def get_next_deliverable_rossall(df):

    df = df.copy()

    df["Finish"] = pd.to_datetime(
        df["Finish"].astype(str).str.replace("A", "").str.replace("*", ""),
        dayfirst=True,
        errors="coerce"
    )

    df["Remaining Duration"] = (
        df["Remaining Duration"]
        .astype(str)
        .str.replace("d", "")
    )

    df["Remaining Duration"] = pd.to_numeric(
        df["Remaining Duration"], errors="coerce"
    ).fillna(0)

    df = df[df["Remaining Duration"] > 0]
    df = df[df["Finish"].notna()].sort_values("Finish")

    if not df.empty:
        row = df.iloc[0]
        finish = row["Finish"]
        today = pd.Timestamp.today().normalize()

        status = " 🔴" if finish < today else ""

        return f"{row['Activity Name']} – {finish.strftime('%d %b')}{status}"

    return "—"


# =========================
# ✅ HEADER (NO HTML)
# =========================

def render_header(ferry_df=None, flass_df=None, rossall_df=None):

    st.markdown("## 📊 UU Design Programme Dashboard")
    st.caption("CL31 & CL32 • Delivery Tracking • Forecasting")

    col1, col2, col3, col4 = st.columns(4)

    # ✅ DATE
    with col1:
        st.metric("📅 Today", datetime.today().strftime('%d %b %Y'))

    # ✅ STATUS
    with col2:
        st.markdown("**Status**")
        st.success("● Programme Live")

    # ✅ PLACEHOLDER / FUTURE KPI
    with col3:
        st.metric("Overview", "—")

    # ✅ ✅ KEY DELIVERABLES
    with col4:
        st.markdown("**🎯 Key Upcoming Deliverables**")

        if ferry_df is not None:
            st.write(f"**Ferry** → {get_next_deliverable(ferry_df)}")

        if flass_df is not None:
            st.write(f"**Flass** → {get_next_deliverable(flass_df)}")

        if rossall_df is not None:
            st.write(f"**Rossall** → {get_next_deliverable_rossall(rossall_df)}")