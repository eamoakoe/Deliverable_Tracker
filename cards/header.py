import streamlit as st
from datetime import datetime


def render_header():

    st.markdown("""
    <style>

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

    /* ✅ FIXED TITLE (ONE LINE ALWAYS) */
    .title {
        font-size: 22px;
        font-weight: 900;
        white-space: nowrap;      /* ✅ stops wrapping */
        overflow: hidden;
        text-overflow: ellipsis;  /* ✅ prevents overflow breaking */
    }

    .subtitle {
        font-size: 13px;
        opacity: 0.85;
        margin-top: 4px;
    }

    .kpi-title {
        font-size: 13px;
        font-weight: 700;
        margin-bottom: 6px;
    }

    .kpi-value {
        font-size: 18px;
        font-weight: 800;
    }

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

    </style>
    """, unsafe_allow_html=True)

    # ✅ ✅ BETTER COLUMN BALANCE
    col1, col2, col3 = st.columns([2, 1, 1], gap="small")

    # ✅ TITLE CARD
    with col1:
        st.markdown("""
        <div class="header-box">
            <div class="title">UU DESIGN PROGRAMME DASHBOARD</div>
            <div class="subtitle">CL31 & CL32 • Delivery Tracking • Forecasting</div>
        </div>
        """, unsafe_allow_html=True)

    # ✅ DATE
    with col2:
        st.markdown(f"""
        <div class="header-box">
            <div class="kpi-title">📅 Today</div>
            <div class="kpi-value">{datetime.today().strftime('%d %b %Y')}</div>
        </div>
        """, unsafe_allow_html=True)

    # ✅ STATUS
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