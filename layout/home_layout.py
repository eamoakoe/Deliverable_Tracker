import streamlit as st

from cards.header import render_header
from cards.pie_card import render_pie
from cards.delay_cl32 import render_delayed_table
from cards.next4weeks_cl32 import render_next4weeks_table
from cards.table_card import render_table


# =========================
# PAGE CONFIG (MUST BE FIRST STREAMLIT CALL)
# =========================
st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# SIDEBAR — PROJECT SELECTOR
# =========================
st.sidebar.markdown(
    '<div style="font-size:14px;font-weight:600;margin-bottom:5px;">PROJECT</div>',
    unsafe_allow_html=True
)

project_list = [
    "Flass Lane",
    "Ferry PS",
    "Rossall Outfall",
    "Tally Ho",
    "Harbour Yard",
    "Eccleston Bridge",
    "Palace Nook",
    "Rampside"
]

selected_project = st.sidebar.selectbox("", project_list)

# Store selection globally (used elsewhere if needed)
st.session_state["selected_project"] = selected_project


# =========================
# MAIN DASHBOARD FUNCTION
# =========================
def render_dashboard(result, df32):

    # =========================
    # ✅ FILTER DATA BY PROJECT
    # =========================
    selected_project = st.session_state.get("selected_project")

    if "Project" in df32.columns:
        df32 = df32[df32["Project"] == selected_project]

    if "Project" in result.columns:
        result = result[result["Project"] == selected_project]

    # =========================
    # HEADER
    # =========================
    render_header()

    st.markdown("<br>", unsafe_allow_html=True)

    # =========================
    # SECTION 1 — PIE + DELAY
    # =========================
    col1, col2 = st.columns([1, 1.2])

    # ---- PIE CARD ----
    with col1:
        st.markdown("""
        <div style="
            background:white;
            padding:15px;
            border-radius:10px;
            box-shadow:0 1px 4px rgba(0,0,0,0.08);
            margin-bottom:15px;
        ">
            <div style="
                font-size:16px;
                font-weight:600;
                margin-bottom:10px;
                color:#1f2a44;
            ">📊 CL32 Schedule Summary</div>
        """, unsafe_allow_html=True)

        render_pie(df32)

        st.markdown("</div>", unsafe_allow_html=True)

    # ---- DELAY CARD ----
    with col2:
        st.markdown("""
        <div style="
            background:white;
            padding:15px;
            border-radius:10px;
            box-shadow:0 1px 4px rgba(0,0,0,0.08);
            margin-bottom:15px;
        ">
            <div style="
                font-size:16px;
                font-weight:600;
                margin-bottom:10px;
                color:#1f2a44;
            ">🔴 Delayed Activities</div>
        """, unsafe_allow_html=True)

        render_delayed_table(df32)

        st.markdown("</div>", unsafe_allow_html=True)


    # =========================
    # SECTION 2 — FORECAST
    # =========================
    st.markdown("""
    <div style="
        background:white;
        padding:15px;
        border-radius:10px;
        box-shadow:0 1px 4px rgba(0,0,0,0.08);
        margin-bottom:15px;
    ">
        <div style="
            font-size:16px;
            font-weight:600;
            margin-bottom:10px;
            color:#1f2a44;
        ">🟢 Next 4 Weeks (Forecast)</div>
    """, unsafe_allow_html=True)

    render_next4weeks_table(df32)

    st.markdown("</div>", unsafe_allow_html=True)


    # =========================
    # SECTION 3 — REGISTER
    # =========================
    st.markdown("""
    <div style="
        background:white;
        padding:15px;
        border-radius:10px;
        box-shadow:0 1px 4px rgba(0,0,0,0.08);
        margin-bottom:15px;
    ">
        <div style="
            font-size:16px;
            font-weight:600;
            margin-bottom:10px;
            color:#1f2a44;
        ">📋 CL31 vs CL32 Deliverable Register</div>
    """, unsafe_allow_html=True)

    render_table(result)

    st.markdown("</div>", unsafe_allow_html=True)