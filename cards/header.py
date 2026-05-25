import streamlit as st
from datetime import datetime


def render_header():
    today = datetime.today().strftime('%d %b %Y')

    # ✅ CSS (safe + simple)
    st.markdown("""
    <style>

    .header-card {
        background: linear-gradient(135deg, #ecfdf5, #d1fae5);
        border: 1px solid rgba(16,185,129,0.25);
        border-radius: 14px;
        padding: 18px 20px;
        box-shadow: 0 4px 14px rgba(0,0,0,0.08);
        margin-bottom: 10px;
    }

    .title {
        font-size: 22px;
        font-weight: 800;
        color: #064e3b;
    }

    .subtitle {
        font-size: 12px;
        color: #047857;
        margin-top: 2px;
    }

    .pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 6px 12px;
        border-radius: 20px;
        background: #d1fae5;
        font-size: 13px;
        font-weight: 600;
        color: #065f46;
    }

    .dot {
        height: 8px;
        width: 8px;
        border-radius: 50%;
        background: #22c55e;
    }

    </style>
    """, unsafe_allow_html=True)

    # ✅ CARD LAYOUT USING STREAMLIT (stable)
    with st.container():
        col1, col2 = st.columns([6, 4])

        # LEFT
        with col1:
            st.markdown('<div class="title">DESIGN PROGRAMME DASHBOARD</div>', unsafe_allow_html=True)
            st.markdown('<div class="subtitle">CL31 & CL32 • Delivery Tracking • Forecasting</div>', unsafe_allow_html=True)

        # RIGHT
        with col2:
            c1, c2 = st.columns(2)

            with c1:
                st.markdown(f'<div class="pill">📅 {today}</div>', unsafe_allow_html=True)

            with c2:
                st.markdown(
                    '<div class="pill"><div class="dot"></div> Programme Live</div>',
                    unsafe_allow_html=True
                )

    # ✅ wrap card border AFTER layout (key trick)
    st.markdown('<div class="header-card"></div>', unsafe_allow_html=True)