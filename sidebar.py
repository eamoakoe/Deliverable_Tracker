import streamlit as st
import base64
import pandas as pd
import datetime
import os


# ✅ LOAD LOGO
def get_base64_image(path):
    if not os.path.exists(path):
        return ""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


# ✅ PROGRAMME TRACKER
def render_programme_tracker():

    file_path = "components/contract_submission_dates.xlsx"

    if not os.path.exists(file_path):
        st.sidebar.warning("Tracker file missing")
        return

    df = pd.read_excel(file_path)
    df.columns = df.columns.str.strip()

    today = datetime.datetime.today()
    month = today.strftime("%B")
    today_day = today.day

    if month not in df.columns:
        st.sidebar.warning(f"{month} not in tracker")
        return

    current = df[["KEY", month]].dropna()

    st.sidebar.markdown("---")

    # ✅ HEADER
    st.sidebar.markdown("""
    <div style="
        background:#0b3d0b;
        padding:8px;
        border-radius:6px;
        text-align:center;
        color:white;
        font-weight:600;
        font-size:13px;
    ">
        📘 Contract Submission Dates 2026–2027
    </div>
    """, unsafe_allow_html=True)

    st.sidebar.markdown(f"**📅 {month} Programme**")

    # ✅ TABLE HEADER
    st.sidebar.markdown("""
    <div style="
        display:flex;
        justify-content:space-between;
        font-weight:600;
        padding:4px 6px;
        border-bottom:1px solid #ccc;
        font-size:12px;
    ">
        <span>Activity</span>
        <span>Date</span>
    </div>
    """, unsafe_allow_html=True)

    # ✅ ROWS (YOUR EXACT COLOUR RULES)
    for _, row in current.iterrows():
        key = row["KEY"]
        day = int(row[month])

        if "Data date" in key:
            bg = "#cfe2f3"   # light blue
            label = "Data date"

        elif "PFA" in key:
            bg = "#f4cccc"   # red
            label = "PFA submission"

        elif "submission to client" in key:
            bg = "#ffe599"   # gold
            label = "Client submission"

        elif "accept / reject" in key:
            bg = "#d9f2d9"   # green
            label = "Accept / Reject"

        else:
            bg = "#f2f2f2"
            label = key

        # ✅ STATUS ICON (independent of colour)
        if day < today_day:
            status = "✅"
        elif day == today_day:
            status = "⚠️"
        else:
            status = ""

        st.sidebar.markdown(f"""
        <div style="
            display:flex;
            justify-content:space-between;
            background:{bg};
            padding:6px;
            margin:2px 0;
            border-radius:4px;
            font-size:12px;
        ">
            <span>{label}</span>
            <span><b>{day}</b> {status}</span>
        </div>
        """, unsafe_allow_html=True)


# ✅ SIDEBAR
def render_sidebar():
    logo = get_base64_image("assets/logo.png")

    st.markdown("""
    <style>
        [data-testid="stSidebarNav"] {
            display: none;
        }

        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #d4f5d0 0%, #a8e6a3 100%);
        }

        section[data-testid="stSidebar"] .stRadio label {
            color: #0b3d0b;
            font-weight: 500;
        }

        section[data-testid="stSidebar"] h1 {
            color: #0b3d0b;
        }
    </style>
    """, unsafe_allow_html=True)

    with st.sidebar:

        # ✅ LOGO (FIXED PROPERLY)
        if logo:
            st.markdown(f"""
            <div style="text-align:center; padding:10px 0 15px 0;">
                <img src="data:image/png;base64,{logo}" width="90">
            </div>
            """, unsafe_allow_html=True)

        # ✅ PROJECT SELECTOR
        st.title("Projects")

        project = st.radio(
            "",
            ["Ferry PS", "Rossall Outfall", "Flass Lane"]
        )

        # ✅ TRACKER
        render_programme_tracker()

    return project
