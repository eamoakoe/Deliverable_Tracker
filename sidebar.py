import streamlit as st
import base64
import pandas as pd
import datetime
import os

# ✅ IMPORT PIE CARDS
from cards.pie_card_ferry import render_pie_ferry
from cards.pie_card_flass import render_pie_flass
from cards.pie_card_rossall import render_pie_rossall


# =========================
# ✅ LOAD LOGO
# =========================
def get_base64_image(path):
    if not os.path.exists(path):
        return ""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


# =========================
# ✅ NEXT DEADLINE
# =========================
def render_next_deadline():

    file_path = "components/contract_submission_dates.xlsx"

    if not os.path.exists(file_path):
        return

    df = pd.read_excel(file_path)
    df.columns = df.columns.str.strip()

    today = datetime.datetime.today()
    month = today.strftime("%B")
    year = today.year
    today_date = today.date()

    if month not in df.columns:
        return

    current = df[["KEY", month]].dropna()

    next_item = None
    min_days = None

    for _, row in current.iterrows():
        day = int(row[month])

        try:
            deadline_date = datetime.date(year, today.month, day)
        except:
            continue

        days_remaining = (deadline_date - today_date).days

        if days_remaining >= 0:
            if min_days is None or days_remaining < min_days:
                min_days = days_remaining
                next_item = row

    if next_item is None:
        return

    key = next_item["KEY"]
    day = int(next_item[month])

    st.sidebar.markdown("---")

    st.sidebar.markdown(f"""
    <div style="background:#ffffff;padding:8px;border-radius:6px;border-left:5px solid #e53935;">
        <b>🎯 Next Deadline</b><br>
        {key}<br>
        → <b>{day} {month}</b><br>
        ⏳ In {min_days} day(s)
    </div>
    """, unsafe_allow_html=True)


# =========================
# ✅ PROGRAMME TRACKER
# =========================
def render_programme_tracker():

    file_path = "components/contract_submission_dates.xlsx"

    if not os.path.exists(file_path):
        return

    df = pd.read_excel(file_path)
    df.columns = df.columns.str.strip()

    today = datetime.datetime.today()
    month = today.strftime("%B")
    today_day = today.day

    if month not in df.columns:
        return

    current = df[["KEY", month]].dropna()

    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**📅 {month} Programme**")

    for _, row in current.iterrows():
        key = row["KEY"]
        day = int(row[month])

        status = "✅" if day < today_day else ("⚠️" if day == today_day else "")

        st.sidebar.markdown(f"""
        <div style="display:flex;justify-content:space-between;background:#f2f2f2;padding:6px;margin:2px 0;border-radius:4px;font-size:12px;">
            <span>{key}</span>
            <span><b>{day}</b> {status}</span>
        </div>
        """, unsafe_allow_html=True)


# =========================
# ✅ SIDEBAR MAIN
# =========================
def render_sidebar(df_ferry, df_flass, df_rossall):

    logo = get_base64_image("assets/logo.png")

    with st.sidebar:

        # ✅ LOGO
        if logo:
            st.markdown(f"""
            <div style="text-align:center;">
                <img src="data:image/png;base64,{logo}" width="100">
            </div>
            """, unsafe_allow_html=True)

        # ✅ PROJECT SELECTOR
        st.title("Projects")

        project = st.radio(
            "",
            ["Ferry PS", "Rossall Outfall", "Flass Lane"]
        )

        # =========================
        # ✅ PROGRAMME STATUS 🔥 (BEST POSITION)
        # =========================
        st.markdown("---")
        st.markdown("## 📊 Programme Status")

        st.markdown("### 🚢 Ferry")
        render_pie_ferry(df_ferry, st.sidebar)

        st.markdown("### 🏗️ Flass")
        render_pie_flass(df_flass, st.sidebar)

        st.markdown("### 🌊 Rossall")
        render_pie_rossall(df_rossall, st.sidebar)

        # =========================
        # ✅ DETAIL + ALERT
        # =========================
        render_programme_tracker()
        render_next_deadline()

    return project
