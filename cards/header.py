import streamlit as st
from datetime import datetime


def render_header():

    st.markdown("""
    <style>

    .header-box {
        background: linear-gradient(135deg, #ef4444 0%, #b91c1c 100%);
        border: 1px solid rgba(255, 255, 255, 0.2);
        min-height: 95px;
        border-radius: 16px;
        padding: 20px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        box-shadow: 0 6px 16px rgba(0,0,0,0.15);
        transition: all 0.2s ease;
    }

    .header-box:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(0,0,0,0.2);
    }

    .title {
        color: white;
        font-size: 26px;
        font-weight: 900;
        letter-spacing: 1px;
    }

    .subtitle {
        color: rgba(255,255,255,0.85);
        font-size: 13px;
        font-weight: 600;
        margin-top: 4px;
    }

    .date-box {
        color: white;
        font-size: 16px;
        font-weight: 800;
        text-align: center;
    }

    .status-box {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        padding: 10px 14px;
        border-radius: 12px;
        background: rgba(255,255,255,0.15);
        border: 1px solid rgba(255,255,255,0.25);
        color: white;
        font-size: 13px;
        font-weight: 700;
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

    col1, col2, col3 = st.columns([5, 3, 2], gap="small")

    # ✅ LEFT
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
        <div class="header-box" style="align-items:center;">
            <div class="date-box">
                📅 {datetime.today().strftime('%d %b %Y')}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ✅ STATUS
    with col3:
        st.markdown("""
        <div class="header-box" style="align-items:center;">
            <div class="status-box">
                <div class="dot"></div>
                Programme Live
            </div>
        </div>
        """, unsafe_allow_html=True)