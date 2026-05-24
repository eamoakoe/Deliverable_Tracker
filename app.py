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
# LOAD DATA
# =========================
df31, df32 = None, None

if project == "Ferry PS":
    df31, df32 = load_ferry()

elif project == "Rossall Outfall":
    df31, df32 = load_rossall()

elif project == "Flass Lane":
    df31, df32 = load_flass()


# =========================
# DEBUG VISIBILITY (CRITICAL)
# =========================
st.sidebar.markdown("### Debug Info")
st.sidebar.write("CL31 shape:", None if df31 is None else df31.shape)
st.sidebar.write("CL32 shape:", None if df32 is None else df32.shape)


# =========================
# SAFETY CHECK
# =========================
if df31 is None or df32 is None:
    st.warning(f"❌ No data loaded for {project}")
    st.stop()

if df31.empty or df32.empty:
    st.error("❌ DataFrames are EMPTY — likely file path issue")
    st.write("CL31 sample", df31.head())
    st.write("CL32 sample", df32.head())
    st.stop()


# =========================
# BUILD RESULT
# =========================
result = build_deliverables(df31, df32)

# =========================
# DEBUG RESULT
# =========================
st.sidebar.write("Result shape:", result.shape)


# =========================
# FALLBACK DISPLAY (IMPORTANT)
# =========================
if result.empty:
    st.warning("⚠️ No deliverables produced — showing raw data instead")

    st.subheader("CL31 Data")
    st.dataframe(df31.head(50), width="stretch")

    st.subheader("CL32 Data")
    st.dataframe(df32.head(50), width="stretch")

else:
    # ✅ NORMAL DASHBOARD
    render_dashboard(result, df32)