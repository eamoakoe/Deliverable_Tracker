import streamlit as st
import base64
import pandas as pd
import datetime
import os


# ✅ LOAD LOGO
def get_base64_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


# ✅ PROGRAMME TRACKER (DATAFRAME VERSION - WORKS IN SIDEBAR)
def render_programme_tracker():
    file_path = "components/contract_submission_dates.xlsx"

    if not os.path.exists(file_path):
        st.sidebar.error("Programme tracker file not found")
        return

    df = pd.read_excel(file_path)

    # Clean column names
    df.columns = df.columns.str.strip()

    # Get current month
    today = datetime.datetime.today()
    month = today.strftime("%B")
    today_day = today.day

    if month not in df.columns:
        st.sidebar.warning(f"{month} not found in tracker")
        return

    current = df[["KEY", month]].dropna()

    # ✅ Short cleaner labels
    labels = {
        "Data date for Murphy & Sub-contractor programme": "Data date",
        "Sub contractor submits PFA to Murphy": "PFA submission",
        "Murphy Programme submission to client": "Client submission",
        "Deadline for Murphy to accept / reject programme": "Accept / Reject"
    }

    data = []

    for _, row in current.iterrows():
        key = labels.get(row["KEY"], row["KEY"])
        day = int(row[month])

        # ✅ Status icons (safe + clean)
        if day < today_day:
            status = "🟢 Completed"
        elif day == today_day:
            status = "🟡 Today"
        else:
            status = "⚪ Upcoming"

        data.append({
            "Activity": key,
            "Date": day,
            "Status": status
        })

    display_df = pd.DataFrame(data)

    # ✅ DISPLAY
    st.sidebar.markdown("---")
    st.sidebar.markdown("## 📘 ARUP Contract Submission Dates 2025–2026")
    st.sidebar.markdown(f"### 📅 {month} Programme")

    st.sidebar.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )


# ✅ SIDEBAR
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

        # ✅ LOGO
        st.markdown(f"""
        <div style="text-align:center; padding:10px 0 20px 0;">
            <img src="data:image/png;base64,{logo}" width="80">
        </div>
        """, unsafe_allow_html=True)

        # ✅ PROJECT SELECTOR
        st.title("Projects")

        project = st.radio(
            "",
            ["Ferry PS", "Rossall Outfall", "Flass Lane"]
        )

        # ✅ PROGRAMME TRACKER
        render_programme_tracker()

    return project
