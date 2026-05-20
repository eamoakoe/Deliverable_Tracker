import streamlit as st
from datetime import datetime


def render_header():

    now = datetime.now()

    # =========================
    # STYLES
    # =========================
    st.markdown("""
    <style>

    .header-container {
        background: linear-gradient(135deg, #d8f3dc 0%, #b7e4c7 100%);
        border: 1px solid rgba(45, 106, 79, 0.25);
        border-radius: 16px;
        padding: 14px 20px;
        box-shadow: 0 6px 18px rgba(0,0,0,0.12);
        margin-bottom: 10px;
    }

    .header-grid {
        display: flex;
        align-items: center;
        justify-content: space-between;
    }

    .title {
        color: #1b4332;
        font-size: 24px;
        font-weight: 800;
        letter-spacing: 0.4px;
        line-height: 1.2;
    }

    .subtitle {
        color: #2d6a4f;
        font-size: 12px;
        font-weight: 600;
        opacity: 0.9;
        margin-top: 4px;
    }

    .right-panel {
        display: flex;
        align-items: center;
        gap: 18px;
    }

    .date-box {
        color: #1b4332;
        font-size: 13px;
        font-weight: 700;
        text-align: right;
    }

    .time {
        font-size: 11px;
        opacity: 0.7;
        margin-top: 2px;
    }

    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 6px 12px;
        border-radius: 999px;
        background: rgba(22, 163, 74, 0.12);
        border: 1px solid rgba(22, 163, 74, 0.35);
        color: #166534;
        font-size: 12px;
        font-weight: 700;
    }

    .dot {
        font-size: 10px;
        color: #16a34a;
        animation: pulse 1.4s infinite;
    }

    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.4; }
        100% { opacity: 1; }
    }

    /* Sticky behavior */
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

    # =========================
    # HEADER CONTENT
    # =========================
    st.markdown(f"""
    <div class="header-container">
        <div class="header-grid">

            <!-- LEFT -->
            <div>
                <div class="title">
                    Design Management Deliverables Dashboard
                </div>
                <div class="subtitle">
                    CL31 & CL32 Programmes • Delivery Tracking • Forecasting
                </div>
            </div>

            <!-- RIGHT -->
            <div class="right-panel">

                <div class="date-box">
                    📅 {now.strftime('%d %b %Y')}
                    <div class="time">
                        Updated: {now.strftime('%H:%M')}
                    </div>
                </div>

                <div class="status-pill">
                    <span class="dot">●</span>
                    Live
                </div>

            </div>

        </div>
    </div>
    """, unsafe_allow_html=True)
