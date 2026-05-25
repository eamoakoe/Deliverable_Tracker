import streamlit as st
from datetime import datetime


def render_header():
    today = datetime.today().strftime('%d %b %Y')

    # ✅ STYLING
    st.markdown("""
    <style>

    .header-card {
        background: linear-gradient(135deg, #ecfdf5, #d1fae5);
        border: 1px solid rgba(16,185,129,0.25);
        border-radius: 16px;
        padding: 18px 22px;
        box-shadow: 0 6px 18px rgba(0,0,0,0.08);
        margin-bottom: 12px;
    }

    .header-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .title {
        font-size: 22px;
        font-weight: 800;
        color: #064e3b;
        margin-bottom: 4px;
    }

    .subtitle {
        font-size: 13px;
        color: #047857;
    }

    .right {
        display: flex;
        gap: 10px;
        align-items: center;
    }

    .pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 6px 12px;
        border-radius: 20px;
        background: #d1fae5;
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
        box-shadow: 0 0 6px #22c55e;
    }

    </style>
    """, unsafe_allow_html=True)

    # ✅ SINGLE CARD WITH EVERYTHING INSIDE
    st.markdown(f"""
    <div class="header-card">

        <div class="header-row">

            <!-- LEFT -->
            <div>
                <div class="title">DESIGN PROGRAMME DASHBOARD</div>
                <div class="subtitle">CL31 & CL32 • Delivery Tracking • Forecasting</div>
            </div>

            <!-- RIGHT -->
            <div class="right">

                <div class="pill">
                    📅 {today}
                </div>

                <div class="pill">
                    <div class="dot"></div>
                    Programme Live
                </div>

            </div>

        </div>

    </div>
    """, unsafe_allow_html=True)