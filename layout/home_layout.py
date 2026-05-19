import streamlit as st
import pandas as pd
import os

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
    font-weight: 500;
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
# ✅ SAFE LOAD FUNCTION (WITH DEBUG)
# =========================
def safe_load(path):
    if os.path.exists(path):
        return pd.read_excel(path)
    else:
        return None


# =========================
# ✅ LOAD DATASETS
# =========================
@st.cache_data
def load_data():
    return {

        # ✅ FERRY PS (MAKE SURE PATH IS CORRECT)
        "Ferry PS": {
            "cl32": safe_load("data/ferry_ps_cl32.xlsx"),
            "cl31": safe_load("data/ferry_ps_cl31.xlsx"),
        },

        # ✅ FLASS LANE
        "Flass Lane": {
            "cl32": safe_load(r"data\Flass\CL32-FL-March.xlsx"),
            "cl31": safe_load(r"data\Flass\CL31-FL-March.xlsx"),
        },

        # ✅ ROSSALL OUTFALL
        "Rossall Outfall": {
            "cl32": safe_load(r"data\Rossall\CL32-RO-May.xlsx"),
            "cl31": safe_load(r"data\Rossall\CL31-RO-March.xlsx"),
        },

        # ✅ PLACEHOLDERS
        "Harbour Yard": {"cl32": None, "cl31": None},
        "Eccleston Bridge": {"cl32": None, "cl31": None},
        "Palace Nook": {"cl32": None, "cl31": None},
        "Rampside": {"cl32": None, "cl31": None},
    }


datasets = load_data()


# =========================
# ✅ SIDEBAR (FIXED LABEL)
# =========================
selected_project = st.sidebar.radio(
    "Project",
    list(datasets.keys()),
    label_visibility="collapsed"
)


# =========================
# ✅ LINK SIDEBAR → DATA
# =========================
project_data = datasets[selected_project]

df32 = project_data["cl32"]
df31 = project_data["cl31"]


# =========================
# ✅ DEBUG (REMOVE LATER)
# =========================
# Uncomment if still blank
# st.write("Selected:", selected_project)
# st.write("CL32 loaded:", df32 is not None)


# =========================
# ✅ STOP IF NO DATA (PLACEHOLDERS)
# =========================
if df32 is None or df32.empty:
    st.stop()


# =========================
# ✅ DASHBOARD (ONLY RUNS IF DATA EXISTS)
# =========================
render_header()

st.markdown("<br>", unsafe_allow_html=True)

col1, col2 = st.columns([1, 1.2])


# PIE
with col1:
    st.markdown("""
    <div style="background:white;padding:15px;border-radius:10px;
    box-shadow:0 1px 4px rgba(0,0,0,0.08);margin-bottom:15px;">
    <div style="font-size:16px;font-weight:600;margin-bottom:10px;">
    📊 CL32 Schedule Summary</div>
    """, unsafe_allow_html=True)

    render_pie(df32)
    st.markdown("</div>", unsafe_allow_html=True)


# DELAY
with col2:
    st.markdown("""
    <div style="background:white;padding:15px;border-radius:10px;
    box-shadow:0 1px 4px rgba(0,0,0,0.08);margin-bottom:15px;">
    <div style="font-size:16px;font-weight:600;margin-bottom:10px;">
    🔴 Delayed Activities</div>
    """, unsafe_allow_html=True)

    render_delayed_table(df32)
    st.markdown("</div>", unsafe_allow_html=True)


# NEXT 4 WEEKS
st.markdown("""
<div style="background:white;padding:15px;border-radius:10px;
box-shadow:0 1px 4px rgba(0,0,0,0.08);margin-bottom:15px;">
<div style="font-size:16px;font-weight:600;margin-bottom:10px;">
🟢 Next 4 Weeks</div>
""", unsafe_allow_html=True)

render_next4weeks_table(df32)
st.markdown("</div>", unsafe_allow_html=True)


# REGISTER (CL31 DATA)
st.markdown("""
<div style="background:white;padding:15px;border-radius:10px;
box-shadow:0 1px 4px rgba(0,0,0,0.08);margin-bottom:15px;">
<div style="font-size:16px;font-weight:600;margin-bottom:10px;">
📋 Register</div>
""", unsafe_allow_html=True)

render_table(df31)
st.markdown("</div>", unsafe_allow_html=True)