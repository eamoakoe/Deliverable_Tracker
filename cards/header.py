import streamlit as st
from datetime import datetime


def render_header():

    now = datetime.now()

    st.markdown("""
    <style>
    .header-container {
        background: linear-gradient(135deg, #d8f3dc 0%, #b7e4c7 100%);
        border-radius: 16px;
        padding: 14px 20px;
        margin-bottom: 10px;
    }

    .header-grid {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .title {
        font-size: 24px;
        font-weight: 800;
        color: #1b4332;
    }

    .subtitle {
        font-size: 12px;
        color: #2d6a4f;
        margin-top: 4px;
    }

    .right {
        display: flex;
        gap: 15px;
        align-items: center;
    }

    .pill {
        background: #dcfce7;
        border-radius: 999px;
        padding: 5px 10px;
        font-size: 12px;
        font-weight: bold;
        color: #166534;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="header-container">
        <div class="header-grid">

            <div>
                <div class="title">Design Management Deliverables Dashboard</div>
                <div class="subtitle">CL31 & CL32 Programmes • Tracking • Forecasting</div>
            </div>

            <div class="right">
                <div>📅 {now.strftime('%d %b %Y')}</div>
                <div class="pill">● Live</div>
            </div>

        </div>
    </div>
    """, unsafe_allow_html=True)


# ✅ IMPORTANT: CALL IT
render_header()
