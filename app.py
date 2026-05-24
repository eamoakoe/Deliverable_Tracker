import streamlit as st

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
# LOAD DATA (SAFE)
# =========================
df31, df32 = None, None

if project == "Ferry PS":
    df31, df32 = load_ferry()

elif project == "Rossall Outfall":
    df31, df32 = load_rossall()

elif project == "Flass Lane":
    df31, df32 = load_flass()

else:
    st.warning("No project selected")
    st.stop()


# =========================
# SAFETY CHECK (CRITICAL)
# =========================
if df31 is None or df32 is None:
    st.warning(f"No data loaded for {project}")
    st.stop()

if df31.empty or df32.empty:
    st.warning(f"No usable data for {project}")
    st.stop()


# =========================
# DEBUG (OPTIONAL - REMOVE LATER)
# =========================
# Uncomment if needed
# st.write("Project:", project)
# st.write("CL31 shape:", df31.shape)
# st.write("CL32 shape:", df32.shape)
# st.write(df32.head())


# =========================
# BUILD DELIVERABLES
# =========================
result = build_deliverables(df31, df32)


# =========================
# RENDER DASHBOARD
# =========================
try:
    render_dashboard(result, df32)
except Exception as e:
    st.error(f"Dashboard rendering failed: {e}")