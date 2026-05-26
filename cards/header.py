import streamlit as st
from datetime import datetime


def render_header():

    st.markdown("""
    <style>

    /* ===== HEADER CONTAINER ===== */
    .header-container {
        display: grid;
        grid-template-columns: 2fr 1fr 1fr 1fr;
        gap: 12px;
        margin-bottom: 10px;
    }

    /* ===== CARD STYLE ===== */
    .header-box {
        background: linear-gradient(135deg, #047857 0%, #065f46 100%);
        border-radius: 16px;
        padding: 18px;
        min-height: 110px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        box-shadow: 0 6px 16px rgba(0,0,0,0.12);
        transition: all 0.2s ease;
        color: white;
    }

    .header-box:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 22px rgba(0,0,0,0.18);
    }

    /* ===== TITLE ===== */
    .title {
        font-size: 22px;
        font-weight: 900;
        letter-spacing: 0.5px;
    }

    .subtitle {
        font-size: 13px;
        opacity: 0.85;
        margin-top: 4px;
        font-weight: 500;
    }

    /* ===== KPI STYLE ===== */
    .kpi-title {
        font-size: 12px;
        opacity: 0.8;
        margin-bottom: 6px;
    }

    .kpi-value {
        font-size: 24px;
        font-weight: 800;
    }

    /* ===== STATUS BADGE ===== */
    .status-box {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 8px 12px;
        border-radius: 10px;
        background: rgba(255,255,255,0.12);
        border: 1px solid rgba(255,255,255,0.25);
        font-size: 13px;
        font-weight: 600;
    }

    .dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #22c55e;
        box-shadow: 0 0 6px #22c55e;
        animation: pulse 1.5s infinite;
    }

    @keyframes pulse {
        0% {opacity:1;}
        50% {opacity:0.4;}
        100% {opacity:1;}
    }

    /* ===== STICKY HEADER ===== */
    div[data-testid="stHorizontalBlock"] {
        position: sticky;
        top: 0;
        z-index: 999;
        background: #fff;
        padding-top: 8px;
        padding-bottom: 8px;
    }

    </style>
    """, unsafe_allow_html=True)

    # ✅ HEADER LAYOUT
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1], gap="small")

    # ✅ MAIN TITLE
    with col1:
        st.markdown("""
        <div class="header-box">
            <div class="title">UU DESIGN PROGRAMME DASHBOARD</div>
            <div class="subtitle">CL31 & CL32 • Delivery Tracking • Forecasting</div>
        </div>
        """, unsafe_allow_html=True)

    # ✅ DATE KPI
    with col2:
        st.markdown(f"""
        <div class="header-box">
            <div class="kpi-title">📅 Today</div>
            <div class="kpi-value">{datetime.today().strftime('%d %b %Y')}</div>
        </div>
        """, unsafe_allow_html=True)

    # ✅ STATUS KPI
    with col3:
        st.markdown("""
        <div class="header-box">
            <div class="kpi-title">Status</div>
            <div class="status-box">
                <div class="dot"></div>
                Programme Live
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ✅ PLACEHOLDER KPI (you can replace later)
    with col4:
        st.markdown("""
        <div class="header-box">
            <div class="kpi-title">Overview</div>
            <div class="kpi-value">—</div>
        </div>
        """, unsafe_allow_html=True)
