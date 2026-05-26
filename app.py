import streamlit as st

from layout.home_layout import render_dashboard
from sidebar import render_sidebar

# ✅ Loaders
from loaders.ferry_loader import load_ferry
from loaders.rossall_loader import load_rossall
from loaders.flass_loader import load_flass

# ✅ Deliverables (per asset)
from cards.deliverables_ferry import build_deliverables as ferry_deliv
from cards.deliverables_flass import build_deliverables as flass_deliv
from cards.deliverables_rossall import build_deliverables as rossall_deliv


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

else:
    st.warning("Project not recognised")
    st.stop()


# =========================
# SAFETY CHECK
# =========================
if df31 is None or df32 is None:
    st.warning(f"No data available for {project}")
    st.stop()


# =========================
# ✅ DELIVERABLES (PER ASSET)
# =========================
if project == "Ferry PS":
    result = ferry_deliv(df31, df32)

elif project == "Rossall Outfall":
    result = rossall_deliv(df31, df32)

elif project == "Flass Lane":
    result = flass_deliv(df31, df32)


# =========================
# ✅ DASHBOARD
# =========================
render_dashboard(result, df32)