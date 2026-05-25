import streamlit as st
import base64
import pandas as pd
import datetime
import os
import plotly.graph_objects as go


# =========================
# ✅ LOAD LOGO
# =========================
def get_base64_image(path):
    if not os.path.exists(path):
        return ""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


# =========================
# ✅ PIE CHART (SIDEBAR OPTIMISED)
# =========================
def render_pie(df, container):

    df = df.copy()
    df.columns = df.columns.str.strip()

    df["Start"] = pd.to_datetime(df["Start"], errors="coerce")
    df["Finish"] = pd.to_datetime(df["Finish"], errors="coerce")

    df["Activity % Complete"] = (
        df["Activity % Complete"]
        .astype(str)
        .str.replace("%", "", regex=False)
    )

    df["Activity % Complete"] = pd.to_numeric(
        df["Activity % Complete"],
        errors="coerce"
    ).fillna(0)

    today = pd.Timestamp.today().normalize()

    def classify(row):
        if pd.isna(row["Start"]) or pd.isna(row["Finish"]):
            return "On Track"
        if row["Finish"] < today and row["Activity % Complete"] < 100:
            return "Delayed"
        if row["Activity % Complete"] >= 100:
            return "Completed"
        return "On Track"

    df["Status"] = df.apply(classify, axis=1)

    summary = df["Status"].value_counts()

    colors = {
        "On Track": "#FFD700",
        "Delayed": "#FF3B30",
        "Completed": "#00C853"
    }

    order = ["On Track", "Delayed", "Completed"]
    summary = summary.reindex([k for k in order if k in summary.index])

    fig = go.Figure(
        data=[go.Pie(
            labels=summary.index,
            values=summary.values,
            sort=False,
            textinfo="none",
            marker=dict(colors=[colors[k] for k in summary.index]),
        )]
    )

    fig.update_layout(
        height=220,  # ✅ smaller for sidebar
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        showlegend=False
    )

    container.plotly_chart(fig, use_container_width=True)


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

    label = key

    st.sidebar.markdown("---")

    st.sidebar.markdown(f"""
    <div style="background:#ffffff;padding:8px;border-radius:6px;border-left:5px solid #e53935;">
        <b>🎯 Next Deadline</b><br>
        {label}<br>
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
                <img src="data:image/png;base64,{logo}" width="90">
            </div>
            """, unsafe_allow_html=True)

        # ✅ PROJECT SELECTOR
        st.title("Projects")

        project = st.radio(
            "",
            ["Ferry PS", "Rossall Outfall", "Flass Lane"]
        )

        # =========================
        # ✅ PROGRAMME STATUS (PINES HERE 🔥)
        # =========================
        st.markdown("---")
        st.markdown("## 📊 Programme Status")

        st.markdown("### 🚢 Ferry")
        render_pie(df_ferry, st.sidebar)

        st.markdown("### 🏗️ Flass")
        render_pie(df_flass, st.sidebar)

        st.markdown("### 🌊 Rossall")
        render_pie(df_rossall, st.sidebar)

        # =========================
        # ✅ TRACKER + DEADLINE
        # =========================
        render_programme_tracker()
        render_next_deadline()

    return project
