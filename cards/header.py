import streamlit as st
from datetime import datetime


def render_header():
    st.markdown("""
    <style>

    /* ===== HEADER CONTAINER ===== */
    .header-container {
        backdrop-filter: blur(12px);
        background: linear-gradient(135deg, rgba(240, 253, 244, 0.9), rgba(220, 252, 231, 0.9));
        border-bottom: 1px solid rgba(34, 197, 94, 0.2);
        padding: 14px 18px;
        border-radius: 0 0 14px 14px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.08);
    }

    div[data-testid="stHorizontalBlock"] {
        position: sticky;
        top: 0;
        z-index: 999;
    }

    /* ===== TITLE ===== */
    .title {
        font-size: 22px;
        font-weight: 800;
        color: #064e3b;
        letter-spacing: 0.5px;
        margin-bottom: 2px;
    }

    .subtitle {
        font-size: 12px;
        font-weight: 500;
        color: #047857;
    }

    /* ===== RIGHT ITEMS ===== */
    .info-pill {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 8px 14px;
        border-radius: 999px;
        font-size: 13px;
        font-weight: 600;
        background: rgba(16, 185, 129, 0.12);
        color: #065f46;
        border: 1px solid rgba(16, 185, 129, 0.25);
        transition: all 0.2s ease;
        white-space: nowrap;
    }

    .info-pill:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }

    /* STATUS DOT */
    .dot {
        height: 8px;
        width: 8px;
        border-radius: 50%;
        background: #22c55e;
        box-shadow: 0 0 8px #22c55e;
        animation: pulse 1.5s infinite;
    }

    @keyframes pulse {
        0% {opacity: 1;}
        50% {opacity: 0.4;}
        100% {opacity: 1;}
    }

    /* ALIGNMENT FIX */
    .right-box {
        display: flex;
        justify-content: flex-end;
        align-items: center;
        gap: 10px;
        height: 100%;
    }

    </style>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([6, 4])

    # ✅ LEFT: TITLE
    with col1:
        st.markdown("""
        <div class="header-container">
            <div class="title">UU DESIGN PROGRAMME DASHBOARD</div>
            <div class="subtitle">CL31 & CL32 • Delivery Tracking • Forecasting</div>
        </div>
        """, unsafe_allow_html=True)

    # ✅ RIGHT: DATE + STATUS INLINE
    with col2:
        st.markdown(f"""
        <div class="header-container right-box">
            <div class="info-pill">
                📅 {datetime.today().strftime('%d %b %Y')}
            </div>

            <div class="info-pill">
                <span class="dot"></span>
                Programme Live
            </div>
        </div>
        """, unsafe_allow_html=True)