import streamlit as st

from loader import load_cl31, load_cl32
from deliverables import build_deliverables
from layout.home_layout import render_dashboard


# =========================
# PAGE CONFIG
# =========================

st.set_page_config(
    layout="wide"
)


# =========================
# TITLE
# =========================

st.title("CL31 vs CL32 Programme Dashboard")


# =========================
# LOAD DATA
# =========================

try:

    df31 = load_cl31()

    st.success(f"CL31 Loaded: {len(df31)} rows")

except Exception as e:

    st.error(f"Failed to load CL31 PDF: {e}")

    st.stop()


try:

    df32 = load_cl32()

    st.success(f"CL32 Loaded: {len(df32)} rows")

except Exception as e:

    st.error(f"Failed to load CL32 PDF: {e}")

    st.stop()


# =========================
# DEBUG VIEW (OPTIONAL)
# =========================

with st.expander("Preview Extracted Data"):

    st.write("CL31 Columns:")
    st.write(df31.columns.tolist())

    st.dataframe(df31.head())

    st.write("CL32 Columns:")
    st.write(df32.columns.tolist())

    st.dataframe(df32.head())


# =========================
# BUILD COMPARISON
# =========================

try:

    result = build_deliverables(df31, df32)

except Exception as e:

    st.error(f"Error building deliverables: {e}")

    st.stop()


# =========================
# RENDER DASHBOARD
# =========================

try:

    render_dashboard(result, df32)

except Exception as e:

    st.error(f"Dashboard render failed: {e}")