import streamlit as st
from datetime import datetime


def render_header():

    st.markdown("""
    <style>

    .header-box {
        background: linear-gradient(135deg, #d8f3dc 0%, #b7e4c7 100%);
        border: 1px solid rgba(45, 106, 79, 0.25);
        min-height: 90px;
        border-radius: 14px;
        padding: 18px 20px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        box-shadow: 0 4px 14px rgba(0,0,0,0.12);
    }

    .left-box {
        border-radius: 14px;
    }

    .title {
        color: #1b4332;
        font-size: 26px;
        font-weight: 900;
        line-height: 1.1;
        margin-bottom: 4px;
        letter-spacing: 1px;
    }

    .subtitle {
        color: #2d6a4f;
        font-size: 13px;
        font-weight: 600;
    }

    .date-box {
        color: #1b4332;
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
        border-radius: 10px;
        background: rgba(45, 106, 79, 0.12);
        border: 1px solid rgba(45, 106, 79, 0.25);
        color: #1b4332;
        font-size: 13px;
        font-weight: 700;
    }

    .dot {
        color: #16a34a;
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
        background: #f8fdf9;
        padding-top: 6px;
        padding-bottom: 6px;
    }

    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([5, 3, 2], gap="small")

    with col1:
        st.markdown("""
        <div class="header-box left-box">
            <div class="title">FL DM PROGRAMME DASHBOARD</div>
            <div class="subtitle">CL31 vs CL32 • Delivery Tracking • Forecasting</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="header-box" style="align-items:center;">
            <div class="date-box">
                📅 {datetime.today().strftime('%d %b %Y')}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="header-box" style="align-items:center;">
            <div class="status-box">
                <span class="dot">●</span>
                Programme Live
            </div>
        </div>
        """, unsafe_allow_html=True)