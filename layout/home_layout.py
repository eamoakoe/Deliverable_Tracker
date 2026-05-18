import streamlit as st

from cards.header import render_header
from cards.pie_card import render_pie
from cards.delay_cl32 import render_delayed_table
from cards.next4weeks_cl32 import render_next4weeks_table
from cards.table_card import render_table


# =========================
# FULL DASHBOARD (SCROLL VIEW)
# =========================
def render_dashboard(result, df32):

    # =========================
    # HEADER (NEW)
    # =========================
    render_header()

    # =========================
    # SECTION 1 — PIE CHART
    # =========================
    st.markdown("""
    <div class="dashboard-card">
        <div class="card-title">📊 CL32 Schedule Summary</div>
    """, unsafe_allow_html=True)

    render_pie(df32)

    st.markdown("</div>", unsafe_allow_html=True)


    # =========================
    # SECTION 2 — DELAY + FORECAST
    # =========================
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="dashboard-card">
            <div class="card-title">🔴 Delayed Activities</div>
        """, unsafe_allow_html=True)

        render_delayed_table(df32)

        st.markdown("</div>", unsafe_allow_html=True)


    with col2:
        st.markdown("""
        <div class="dashboard-card">
            <div class="card-title">🟢 Next 4 Weeks (Forecast)</div>
        """, unsafe_allow_html=True)

        render_next4weeks_table(df32)

        st.markdown("</div>", unsafe_allow_html=True)


    # =========================
    # SECTION 3 — FULL REGISTER
    # =========================
    st.markdown("""
    <div class="dashboard-card">
        <div class="card-title">📋 CL31 vs CL32 Deliverable Register</div>
    """, unsafe_allow_html=True)

    render_table(result)

    st.markdown("</div>", unsafe_allow_html=True)