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


# ✅ COMPACT PROGRAMME TRACKER (SIDEBAR FRIENDLY)
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

    # ✅ Short labels
    labels = {
        "Data date for Man & Sub-contractor programme": "Data date",
        "Sub contractor submits PFA to Man": "PFA submission",
        "Man Programme submission to client": "Client submission",
        "Deadline for Man to accept / reject programme": "Accept / Reject"
    }

    st.sidebar.markdown("---")

    # ✅ Styled header
    st.sidebar.markdown(f"""
    <div style="
        background:#0b3d0b;
        padding:8px;
        border-radius:6px;
        text-align:center;
        color:white;
        font-weight:600;
        font-size:14px;
    ">
        📘 Contract Submission Dates 2026–2027
    </div>
    """, unsafe_allow_html=True)

    st.sidebar.markdown(f"**📅 {month} Programme**")

    # ✅ Compact rows (fits sidebar)
    for _, row in current.iterrows():
        key = labels.get(row["KEY"], row["KEY"])
        day = int(row[month])

        # ✅ STATUS RULES
        if day < today_day:
            icon = "🟢"   # completed
        elif day == today_day:
            icon = "🟡"   # today
        else:
            icon = "🔴"   # upcoming (YOUR REQUEST)

        st.sidebar.markdown(
            f"{icon} **{key}**  \n&nbsp;&nbsp;&nbsp;&nbsp;{day} {month}"
        )


# ✅ SIDEBAR
def render_sidebar():
    logo = get_base64_image("assets/logo.png")

    # ✅ SIDEBAR STYLE
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

        # ✅ LOGO (FIXED)
        if logo:
            st.markdown(f"""
            <div style="text-align:center; padding:10px 0 15px 0;">
                <img src="data:image/png;base64,{logo}" width="100">
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