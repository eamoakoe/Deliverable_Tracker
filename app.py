import streamlit as st

from deliverables import build_deliverables
from layout.home_layout import render_dashboard
from sidebar import render_sidebar


# =========================
# PAGE CONFIG
# =========================
st.set_page_config(layout="wide")


# =========================
# SIDEBAR (ONLY ONE ✅)
# =========================
project, df31, df32 = render_sidebar()


# =========================
# SAFETY CHECK
# =========================
if df31 is None or df32 is None:
    st.warning(f"No data available for {project}")
    st.stop()


# =========================
# YOUR ORIGINAL LOGIC ✅
# =========================
result = build_deliverables(df31, df32)
render_dashboard(result, df32)