import streamlit as st

from loaders.rossall_loader import load_rossall
from deliverables import build_deliverables
from cards.pie_card import render_pie

st.set_page_config(layout="wide")

st.title("Rossall Deliverables Tracker")

# =========================
# LOAD DATA
# =========================
df31, df32 = load_rossall()

# =========================
# DEBUG (VISIBLE)
# =========================
st.sidebar.write("CL31 shape:", df31.shape)
st.sidebar.write("CL32 shape:", df32.shape)

# =========================
# SAFETY CHECK
# =========================
if df31.empty or df32.empty:
    st.error("❌ Data not loading — check files")
    st.stop()

# =========================
# DELIVERABLES
# =========================
result = build_deliverables(df31, df32)

st.subheader("Deliverables Comparison")
st.dataframe(result, width="stretch")

# =========================
# PROGRAMME STATUS
# =========================
render_pie(df32)