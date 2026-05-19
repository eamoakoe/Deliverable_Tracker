import streamlit as st
import pandas as pd
import os
import re

from deliverables import build_deliverables
from layout.home_layout import render_dashboard


# =========================
# PAGE CONFIG
# =========================
st.set_page_config(layout="wide")


# =========================
# SIDEBAR (THIS IS THE KEY)
# =========================
site = st.sidebar.selectbox(
    "Select Site",
    ["Ferry", "Flass", "Rossall"]
)


# =========================
# CLEAN COLUMNS
# =========================
def clean_columns(df):
    df.columns = [
        re.sub(r"\s+", " ", str(c).replace("\n", " ").replace("\u00a0", " ")).strip()
        for c in df.columns
    ]
    return df


# =========================
# LOAD FILE
# =========================
def load_file(path):
    if not path or not os.path.exists(path):
        return None

    df = pd.read_excel(path, engine="openpyxl")
    return clean_columns(df)


# =========================
# GET LATEST FILE
# =========================
def get_latest(folder, prefix):
    if not os.path.exists(folder):
        return None

    files = [
        f for f in os.listdir(folder)
        if f.lower().startswith(prefix.lower()) and f.endswith(".xlsx")
    ]

    if not files:
        return None

    files.sort()
    return os.path.join(folder, files[-1])


# =========================
# LOAD DATA (ONLY SWITCH SOURCE)
# =========================
if site == "Ferry":
    df31 = load_file(get_latest("data/Ferry/", "CL31"))
    df32 = load_file(get_latest("data/Ferry/", "CL32"))

elif site == "Flass":
    df31 = load_file(get_latest("data/Flass/", "CL31-FL"))
    df32 = load_file(get_latest("data/Flass/", "CL32-FL"))

elif site == "Rossall":
    df31 = load_file(get_latest("data/Rossall/", "CL31-RO"))
    df32 = load_file(get_latest("data/Rossall/", "CL32-RO"))


# =========================
# SAFETY CHECK
# =========================
if df31 is None or df32 is None:
    st.warning(f"No data available for {site}")
    st.stop()


# =========================
# YOUR ORIGINAL LOGIC (UNCHANGED)
# =========================
result = build_deliverables(df31, df32)
render_dashboard(result, df32)
