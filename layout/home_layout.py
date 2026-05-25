import streamlit as st

from cards.header import render_header
from cards.next7days_cl32 import render_next7days_table
from cards.table_card import render_table

# ✅ Milestones (deliverable tracking)
from cards.milestone_cl32_ferry import render_milestone_table as ferry_ms
from cards.milestone_cl32_flass import render_milestone_table as flass_ms
from cards.milestone_cl32_rossall import render_milestone_table as rossall_ms


# =========================
# ✅ DETECT ASSET
# =========================
def detect_asset(df):

    if "Activity ID" not in df.columns:
        return "Unknown"

    ids = df["Activity ID"].astype(str)

    if ids.str.contains("FER-").any():
        return "Ferry"
    elif ids.str.contains("FLA").any() or ids.str.contains("FLASS").any():
        return "Flass"
    elif ids.str.contains("ROS").any():
        return "Rossall"
    else:
        return "Unknown"


# =========================
# ✅ DASHBOARD (MAIN PAGE)
# =========================
def render_dashboard(df31, df32):

    if df32 is None or df32.empty:
        st.stop()

    # ✅ Detect asset
    asset = detect_asset(df32)

    # =========================
    # ✅ HEADER
    # =========================
    render_header()
    st.markdown("<br>", unsafe_allow_html=True)

    # =========================
    # ✅ DELIVERABLE TRACKING (FULL WIDTH)
    # =========================
    st.markdown(f"""
    <div style="
        background:white;
        padding:15px;
        border-radius:10px;
        box-shadow:0 1px 4px rgba(0,0,0,0.08);
        margin-bottom:15px;
    ">
    <div style="font-size:16px;font-weight:600;margin-bottom:10px;">
        🔴 Key Deliverable Tracking – {asset}
    </div>
    """, unsafe_allow_html=True)

    if asset == "Ferry":
        ferry_ms(df32)
    elif asset == "Flass":
        flass_ms(df32)
    elif asset == "Rossall":
        rossall_ms(df32)
    else:
        st.warning("No deliverable logic defined for this dataset")

    st.markdown("</div>", unsafe_allow_html=True)

    # =========================
    # ✅ NEXT 7 DAYS
    # =========================
    st.markdown("""
    <div style="
        background:white;
        padding:15px;
        border-radius:10px;
        box-shadow:0 1px 4px rgba(0,0,0,0.08);
        margin-bottom:15px;
    ">
    <div style="font-size:16px;font-weight:600;margin-bottom:10px;">
        🟢 Next 7 Days
    </div>
    """, unsafe_allow_html=True)

    render_next7days_table(df32)

    st.markdown("</div>", unsafe_allow_html=True)

    # =========================
    # ✅ REGISTER (CL31 / CL32)
    # =========================
    st.markdown("""
    <div style="
        background:white;
        padding:15px;
        border-radius:10px;
        box-shadow:0 1px 4px rgba(0,0,0,0.08);
        margin-bottom:15px;
    ">
    <div style="font-size:16px;font-weight:600;margin-bottom:10px;">
        📋 CL31 & CL32 Tracker
    </div>
    """, unsafe_allow_html=True)

    render_table(df31)

    st.markdown("</div>", unsafe_allow_html=True)
