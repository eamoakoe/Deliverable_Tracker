import streamlit as st
from datetime import datetime


def render_header():
    today = datetime.today().strftime('%d %b %Y')

    # ✅ CSS (kept separate — avoids f-string issues)
    st.markdown("""
    <style>

    /* ===== HEADER BAR ===== */
    .header {
        position: sticky;
        top: 0;
        z-index: 999;
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 14px 20px;
        background: linear-gradient(135deg, #ecfdf5, #d1fae5);
        border-bottom: 1px solid rgba(16,185,129,0.25);
        border-radius: 0 0 14px 14px;
        box-shadow: 0 4px 18px rgba(0,0,0,0.08);
    }

    /* ===== LEFT SECTION ===== */
    .title {
        font-size: 22px;
        font-weight: 800;
        color: #064e3b;
        letter-spacing: 0.3px;
    }

    .subtitle {
        font-size: 12px;
        color: #047857;
        margin-top: 2px;
    }

    /* ===== RIGHT SECTION ===== */
    .right {
        display: flex;
        align-items: center;
        gap: 12px;
    }

    /* ===== PILLS ===== */
    .info-pill {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 8px 14px;
        border-radius: 999px;
        background: rgba(16,185,129,0.12);
        border: 1px solid rgba(16,185,129,0.25);
        font-size: 13px;
        font-weight: 600;
        color: #065f46;
        transition: all 0.2s ease;
    }

    .info-pill:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 14px rgba(0,0,0,0.08);
    }

    /* ===== STATUS DOT ===== */
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

    # ✅ HEADER HTML
    st.markdown(f"""
    <div class="header">

        <!-- LEFT -->
        <div>
            <div class="title">DESIGN PROGRAMME DASHBOARD</div>
            <div class="subtitle">CL31 & CL32 • Delivery Tracking • Forecasting</div>
        </div>

        <!-- RIGHT -->
        <div class="right">

            <div class="info-pill">
                📅 {today}
            </div>

            <div class="info-pill">
                <div class="dot"></div>
                Programme Live
            </div>

        </div>

    </div>
    """, unsafe_allow_html=True)