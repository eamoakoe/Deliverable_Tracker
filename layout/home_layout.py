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
# ✅ SIDEBAR STYLE (LIGHT GREEN)
# =========================
st.markdown("""
<style>

/* Sidebar background */
section[data-testid="stSidebar"] {
    background-color: #e6ffe6;
}

/* Project list style */
div[role="radiogroup"] label {
    font-weight: 500;
    padding: 6px 10px;
    border-radius: 6px;
    cursor: pointer;
}

/* Selected item */
div[role="radiogroup"] label[data-checked="true"] {
    background-color: #b3ffb3;
    color: #006600;
}

/* Remove radio buttons */
div[role="radiogroup"] input {
    display: none;
}

</style>
""", unsafe_allow_html=True)


# =========================
# ✅ SIDEBAR PROJECT LIST
# =========================
st.sidebar.markdown(
    '<div style="font-size:15px;font-weight:700;margin-bottom:10px;">PROJECT</div>',
    unsafe_allow_html=True
)

project_list = [
    "Ferry PS",
    "Rossall Outfall",
    "Flass Lane",
    "Harbour Yard / Tally Ho",
    "Eccleston Bridge",
    "Palace Nook",
    "Rampside"
]

selected_project = st.sidebar.radio("", project_list)

# Store selection
st.session_state["selected_project"] = selected_project


# =========================
# ✅ MAIN DASHBOARD FUNCTION
# =========================
def render_dashboard(result, df32):

    selected_project = st.session_state.get("selected_project")

    # =========================
    # ✅ ONLY FERRY PS IS ALLOWED
    # =========================
    if selected_project != "Ferry PS":
        st.stop()  # 🔴 HARD STOP → NOTHING renders


    # =========================
    # ✅ FERRY PS DASHBOARD ONLY
    # =========================
    render_header()

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1.2])

    # -------------------------
    # PIE CARD
    # -------------------------
    with col1:
        st.markdown("""
        <div style="background:white;padding:15px;border-radius:10px;
        box-shadow:0 1px 4px rgba(0,0,0,0.08);margin-bottom:15px;">
        <div style="font-size:16px;font-weight:600;margin-bottom:10px;">
        📊 CL32 Schedule Summary</div>
        """, unsafe_allow_html=True)

        render_pie(df32)

        st.markdown("</div>", unsafe_allow_html=True)

    # -------------------------
    # DELAY CARD
    # -------------------------
    with col2:
        st.markdown("""
        <div style="background:white;padding:15px;border-radius:10px;
        box-shadow:0 1px 4px rgba(0,0,0,0.08);margin-bottom:15px;">
        <div style="font-size:16px;font-weight:600;margin-bottom:10px;">
        🔴 Delayed Activities</div>
        """, unsafe_allow_html=True)

        render_delayed_table(df32)

        st.markdown("</div>", unsafe_allow_html=True)


    # -------------------------
    # NEXT 4 WEEKS
    # -------------------------
    st.markdown("""
    <div style="background:white;padding:15px;border-radius:10px;
    box-shadow:0 1px 4px rgba(0,0,0,0.08);margin-bottom:15px;">
    <div style="font-size:16px;font-weight:600;margin-bottom:10px;">
    🟢 Next 4 Weeks</div>
    """, unsafe_allow_html=True)

    render_next4weeks_table(df32)

    st.markdown("</div>", unsafe_allow_html=True)


    # -------------------------
    # REGISTER
    # -------------------------
    st.markdown("""
    <div style="background:white;padding:15px;border-radius:10px;
    box-shadow:0 1px 4px rgba(0,0,0,0.08);margin-bottom:15px;">
    <div style="font-size:16px;font-weight:600;margin-bottom:10px;">
    📋 Register</div>
    """, unsafe_allow_html=True)

    render_table(result)

    st.markdown("</div>", unsafe_allow_html=True)
