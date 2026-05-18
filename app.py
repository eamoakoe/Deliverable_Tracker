import streamlit as st

from loader import load_cl31, load_cl32
from deliverables import build_deliverables
from layout.home_layout import render_dashboard

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(layout="wide")


# =========================
# LOAD DATA
# =========================
df31 = load_cl31()
df32 = load_cl32()
result = build_deliverables(df31, df32)

# =========================
# RENDER FULL DASHBOARD
# =========================
render_dashboard(result, df32)