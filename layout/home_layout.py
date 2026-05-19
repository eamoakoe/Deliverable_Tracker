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
section[data-testid="stSidebar"] {
    background-color: #e6ffe6;
}
div[role="radiogroup"] label {
    padding: 6px 10px;
    border-radius: 6px;
}
div[role="radiogroup"] label[data-checked="true"] {
    background-color: #b3ffb3;
    color: #006600;
}
div[role="radiogroup"] input {
    display: none;
}
</style>
""", unsafe_allow_html=True)


# =========================
# ✅ SIDEBAR (UI ONLY)
# =========================
project_list = [
    "Ferry PS",
    "Rossall Outfall",
    "Flass Lane",
]

selected_project = st.sidebar.radio(
    "Project",
    project_list,
    label_visibility="collapsed"
)

# store selection for loader to use
st.session_state["selected_project"] = selected_project


# =========================
# ✅ DASHBOARD (REQUIRES DATA FROM LOADER)
# =========================
def render_dashboard(df31, df32):

    # =========================
    # ✅ STOP IF NO DATA (PLACEHOLDERS)
    # =========================
    if df32 is None or df32.empty:
        st.stop()   # ✅ blank screen for placeholders


    # =========================
    # HEADER
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

    render_table(df31)

    st.markdown("</div>", unsafe_allow_html=True)
