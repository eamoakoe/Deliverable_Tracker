import streamlit as st

from cards.header import render_header

# ✅ Milestones
from cards.milestone_cl32_ferry import render_milestone_table as ferry_ms
from cards.milestone_cl32_flass import render_milestone_table as flass_ms
from cards.milestone_cl32_rossall import render_milestone_table as rossall_ms

# ✅ Lookahead
from cards.next7days_cl32_ferry import render_next7days_table as ferry_next7
from cards.next7days_cl32_flass import render_next7days_table as flass_next7
from cards.next7days_cl32_rossall import render_next7days_table as rossall_next7


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
# ✅ DASHBOARD
# =========================
def render_dashboard(deliverables_df, df32):

    if df32 is None or df32.empty:
        st.stop()

    asset = detect_asset(df32)

    # =========================
    # ✅ HEADER
    # =========================
    render_header()
    st.markdown("<br>", unsafe_allow_html=True)

    # =========================
    # ✅ DELIVERY STATUS (AMBER)
    # =========================
    st.markdown(f"""
    <div style="
        background:#fffbeb;
        padding:15px;
        border-radius:12px;
        border-left:5px solid #f59e0b;
        box-shadow:0 2px 6px rgba(0,0,0,0.08);
        margin-bottom:15px;
    ">
    <div style="
        font-size:18px;
        font-weight:700;
        margin-bottom:2px;
    ">
        {asset} — Delivery Status (CL32)
    </div>
    """, unsafe_allow_html=True)

    if asset == "Ferry":
        ferry_ms(df32)
    elif asset == "Flass":
        flass_ms(df32)
    elif asset == "Rossall":
        rossall_ms(df32)
    else:
        st.warning("No milestone logic defined")

    st.markdown("</div>", unsafe_allow_html=True)

    # =========================
    # ✅ 7-DAY LOOKAHEAD (GREEN)
    # =========================
    st.markdown("""
    <div style="
        background:#f0fdf4;
        padding:15px;
        border-radius:12px;
        border-left:5px solid #22c55e;
        margin-bottom:15px;
    ">
    <div style="font-size:18px;font-weight:700;">
        7-Day Lookahead (CL32)
    </div>
    """, unsafe_allow_html=True)

    if asset == "Ferry":
        ferry_next7(df32)
    elif asset == "Flass":
        flass_next7(df32)
    elif asset == "Rossall":
        rossall_next7(df32)
    else:
        st.warning("No lookahead logic defined")

    st.markdown("</div>", unsafe_allow_html=True)

    # =========================
    # ✅ PROGRAMME CONTROLS (BLUE)
    # =========================
    st.markdown("""
    <div style="
        background:#eff6ff;
        padding:15px;
        border-radius:12px;
        border-left:5px solid #3b82f6;
    ">
    <div style="font-size:18px;font-weight:700;">
        Programme Controls (CL31 / CL32)
    </div>
    """, unsafe_allow_html=True)

    if deliverables_df is not None and not deliverables_df.empty:
        st.dataframe(deliverables_df, use_container_width=True)
    else:
        st.warning("No deliverables data available")

    st.markdown("</div>", unsafe_allow_html=True)