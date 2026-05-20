import streamlit as st
import base64
import pandas as pd
import datetime
import os


def get_base64_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


# ✅ ADDED: Programme Tracker Function
def render_programme_tracker():
    file_path = "components/contract_submission_dates.xlsx"

    if not os.path.exists(file_path):
        st.sidebar.error("Programme tracker file not found")
        return

    df = pd.read_excel(file_path)

    # Clean column names
    df.columns = df.columns.str.strip()

    # Get current month
    month = datetime.datetime.today().strftime("%B")

    if month not in df.columns:
        st.sidebar.warning(f"{month} not found in tracker")
        return

    current = df[["KEY", month]].dropna()

    st.sidebar.markdown("---")
    st.sidebar.markdown(f"### 📅 {month} Programme")

    for _, row in current.iterrows():
        st.sidebar.markdown(
            f"• **{row['KEY']}** → {int(row[month])}"
        )


def render_sidebar():
    logo = get_base64_image("assets/logo.png")

    # ✅ LIGHT GREEN SIDEBAR STYLE
    st.markdown("""
    <style>
        [data-testid="stSidebarNav"] {
            display: none;
        }

        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #d4f5d0 0%, #a8e6a3 100%);
        }

        /* Optional: Improve text visibility */
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

        st.markdown(f"""
        <div style="text-align:center; padding:10px 0 20px 0;">
            <img src="data:image/png;base64,{logo}" width="80">
        </div>
        """, unsafe_allow_html=True)

        st.title("Projects")

        project = st.radio(
            "",
            ["Ferry PS", "Rossall Outfall", "Flass Lane"]
        )

        # ✅ ADDED: Programme Tracker display
        render_programme_tracker()

    return project
