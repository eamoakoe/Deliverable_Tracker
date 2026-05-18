import streamlit as st

from cards.header import render_header
from cards.pie_card import render_pie
from cards.delay_cl32 import render_delayed_table
from cards.next4weeks_cl32 import render_next4weeks_table
from cards.table_card import render_table


# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# ✅ SIDEBAR STYLING (LIGHT RED)
# =========================
st.markdown("""
<style>
/* Sidebar background */
section[data-testid="stSidebar"] {
    background-color: #ffe6e6;  /* light red */
}

/* Project list styling */
div[role="radiogroup"] label {
    font-weight: 500;
    padding: 6px 10px;
    border-radius: 6px;
    cursor: pointer;
}

/* Selected item highlight */
div[role="radiogroup"] label[data-checked="true"] {
    background-color: #ffcccc;
    color: #800000;
}

/* Remove radio circle */
div[role="radiogroup"] input {
    display: none;
}
</style>
""", unsafe_allow_html=True)


# =========================
# ✅ SIDEBAR — CLICKABLE PROJECT LIST
# =========================
st.sidebar.markdown(
    '<div style="font-size:15px;font-weight:700;margin-bottom:10px;">PROJECT</div>',
    unsafe_allow_html=True
)

project_list = [
    "Tally Ho",
    "Ferry PS",
    "Rossall Outfall",
    "Flass Lane",
    "Harbour Yard",
    "Eccleston Bridge",
    "Palace Nook",
    "Rampside"
]

selected_project = st.sidebar.radio("", project_list)

st.session_state["selected_project"] = selected_project


# =========================
# MAIN DASHBOARD FUNCTION
# =========================
def render_dashboard(result, df32):

    # =========================
    # ✅ FILTER DATA
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

    with col1:
        st.markdown("""
        <div style="
            background:white;
            padding:15px;
            border-radius:10px;
            box-shadow:0 1px 4px rgba(0,0,0,0.08);
            margin-bottom:15px;
        ">
            <div style="font-size:16px;font-weight:600;margin-bottom:10px;color:#1f2a44;">
            📊 CL32 Schedule Summary</div>
        """, unsafe_allow_html=True)

        render_pie(df32)

        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style="
            background:white;
            padding:15px;
            border-radius:10px;
            box-shadow:0 1px 4px rgba(0,0,0,0.08);
            margin-bottom:15px;
        ">
            <div style="font-size:16px;font-weight:600;margin-bottom:10px;color:#1f2a44;">
            🔴 Delayed Activities</div>
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
        <div style="font-size:16px;font-weight:600;margin-bottom:10px;color:#1f2a44;">
        🟢 Next 4 Weeks (Forecast)</div>
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
        <div style="font-size:16px;font-weight:600;margin-bottom:10px;color:#1f2a44;">
        📋 CL31 vs CL32 Deliverable Register</div>
    """, unsafe_allow_html=True)

    render_table(result)

    st.markdown("</div>", unsafe_allow_html=True)