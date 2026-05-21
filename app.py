Aimport streamlit as st

from deliverables import build_deliverables
from layout.home_layout import render_dashboard
from sidebar import render_sidebar

from loaders.ferry_loader import load_ferry
from loaders.rossall_loader import load_rossall
from loaders.flass_loader import load_flass


# =========================
# PAGE CONFIG
# =========================
st.set_page_config(layout="wide")


# =========================
# SIDEBAR
# =========================
project = render_sidebar()


# =========================
# LOAD DATA
# =========================
if project == "Ferry PS":
    df31, df32 = load_ferry()

elif project == "Rossall Outfall":
    df31, df32 = load_rossall()

elif project == "Flass Lane":
    df31, df32 = load_flass()


# =========================
# SAFETY CHECK
# =========================
if df31 is None or df32 is None:
    st.warning(f"No data available for {project}")
    st.stop()


# =========================
# YOUR LOGIC (UNCHANGED ✅)
# =========================
result = build_deliverables(df31, df32)
render_dashboard(result, df32)
