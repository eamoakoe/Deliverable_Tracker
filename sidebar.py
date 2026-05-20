import streamlit as st
import base64
import pandas as pd
import datetime
import os


def get_base64_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


# ✅ PROGRAMME TRACKER (COLOUR-CODED TABLE)
def render_programme_tracker():
    file_path = "components/contract_submission_dates.xlsx"

    if not os.path.exists(file_path):
        st.sidebar.error("Programme tracker file not found")
        return

    df = pd.read_excel(file_path)
    df.columns = df.columns.str.strip()

    today = datetime.datetime.today()
    month = today.strftime("%B")
    today_day = today.day

    if month not in df.columns:
        st.sidebar.warning(f"{month} not found in tracker")
        return

    current = df[["KEY", month]].dropna()

    # ✅ Short labels for cleaner display
    labels = {
        "Data date for Man & Sub-contractor programme": "Data date",
        "Sub contractor submits PFA to Man": "PFA submission",
        "Man Programme submission to client": "Client submission",
        "Deadline for Man to accept / reject programme": "Accept / Reject"
    }

    rows_html = ""

    for _, row in current.iterrows():
        key = labels.get(row["KEY"], row["KEY"])
        day = int(row[month])

        # ✅ Colour logic
        if day < today_day:
            colour = "#4CAF50"   # green = complete
        elif day == today_day:
            colour = "#FFC107"   # amber = today
        else:
            colour = "#B0BEC5"   # grey = upcoming

        rows_html += f"""
        <tr>
            <td style="padding:4px 6px;">{key}</td>
            <td style="text-align:center;">{day}</td>
            <td style="text-align:center;">
                <span style="
                    display:inline-block;
                    width:10px;
                    height:10px;
                    border-radius:50%;
                    background:{colour};
                "></span>
            </td>
        </tr>
        """

    # ✅ FINAL DISPLAY
    st.sidebar.markdown("---")
    st.sidebar.markdown("## 📘 Contract Submission Dates 2026–2027")
    st.sidebar.markdown(f"### 📅 {month} Programme")

    st.sidebar.markdown(f"""
    <table style="width:100%; font-size:13px;">
        <thead>
            <tr>
                <th style="text-align:left;">Activity</th>
                <th>Date</th>
                <th></th>
            </tr>
        </thead>
        <tbody>
            {rows_html}
        </tbody>
    </table>
    """, unsafe_allow_html=True)


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

        # ✅ PROGRAMME TRACKER
        render_programme_tracker()

    return project
