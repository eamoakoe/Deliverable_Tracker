import streamlit as st
from datetime import datetime

def render_header():

    st.markdown(f"""
    <style>
    .header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 14px 18px;
        background: linear-gradient(135deg, #ecfdf5, #d1fae5);
        border-bottom: 1px solid rgba(16,185,129,0.2);
        border-radius: 0 0 12px 12px;
    }

    .title {
        font-size: 22px;
        font-weight: 800;
        color: #064e3b;
    }

    .subtitle {
        font-size: 12px;
        color: #047857;
    }

    .right {
        display: flex;
        gap: 10px;
        align-items: center;
    }

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
    }

    .dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #22c55e;
        animation: pulse 1.5s infinite;
    }

    @keyframes pulse {
        0% {{opacity:1}}
        50% {{opacity:0.4}}
        100% {{opacity:1}}
    }
    </style>

    <div class="header">
        <div>
            <div class="title">DESIGN PROGRAMME DASHBOARD</div>
            <div class="subtitle">CL31 & CL32 • Delivery Tracking • Forecasting</div>
        </div>

        <div class="right">

            <div class="info-pill">
                📅 {datetime.today().strftime('%d %b %Y')}
            </div>

            <div class="info-pill">
                <div class="dot"></div>
                Programme Live
            </div>

        </div>
    </div>
    """, unsafe_allow_html=True)