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
st.set_page_config(layout="wide")


# =========================
# ✅ SIDEBAR STYLE
# =========================
st.markdown("""
<style>
section[data-testid="stSidebar"] {
    background-color: #e6ffe6;
}
div[role="radiogroup"] label {
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
# ✅ SAFE LOAD (CLOUD DEBUG FRIENDLY)
# =========================
def safe_load(path):
    if os.path.exists(path):
        return pd.read_excel(path)
    else:
        st.warning(f"Missing file: {path}")  # helps debug cloud
        return None


# =========================
# ✅ LOAD DATA (USE / NOT \ )
# =========================
@st.cache_data
def load_data():
    return {

        "Ferry PS": {
            "cl32": safe_load("data/ferry_ps_cl32.xlsx"),
            "cl31": safe_load("data/ferry_ps_cl31.xlsx"),
        },

        "Flass Lane": {
            "cl32": safe_load("data/Flass/CL32-FL-March.xlsx"),
            "cl31": safe_load("data/Flass/CL31-FL-March.xlsx"),
        },

        "Rossall Outfall": {
            "cl32": safe_load("data/Rossall/CL32-RO-May.xlsx"),
            "cl31": safe_load("data/Rossall/CL31-RO-March.xlsx"),
        },

        # placeholders
        "Harbour Yard": {"cl32": None, "cl31": None},
        "Eccleston Bridge": {"cl32": None, "cl31": None},
        "Palace Nook": {"cl32": None, "cl31": None},
        "Rampside": {"cl32": None, "cl31": None},
    }


datasets = load_data()


# =========================
# ✅ SIDEBAR
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
# st.write("Selected:", selected_project)
# st.write("Files in data:", os.listdir("data"))


# =========================
# ✅ STOP IF NO DATA
# =========================
if df32 is None or df32.empty:
    st.stop()


# =========================
# ✅ DASHBOARD
# =========================
render_header()

st.markdown("<br>", unsafe_allow_html=True)

col1, col2 = st.columns([1, 1.2])


with col1:
    render_pie(df32)

with col2:
    render_delayed_table(df32)

render_next4weeks_table(df32)
render_table(df31)