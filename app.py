import streamlit as st
import pandas as pd
import os
import re

from deliverables import build_deliverables
from layout.home_layout import render_dashboard
from sidebar import render_sidebar


# =========================
# PAGE CONFIG
# =========================
st.set_page_config(layout="wide")


# =========================
# SIDEBAR
# =========================
project = render_sidebar()


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
# LOAD DATA (BASED ON PROJECT)
# =========================
if project == "Ferry PS":
    df31 = load_file(get_latest("data/Ferry/", "CL31"))
    df32 = load_file(get_latest("data/Ferry/", "CL32"))

elif project == "Rossall Outfall":
    df31 = load_file(get_latest("data/Rossall/", "CL31-RO"))
    df32 = load_file(get_latest("data/Rossall/", "CL32-RO"))

elif project == "Flass Lane":
    df31 = load_file(get_latest("data/Flass/", "CL31-FL"))
    df32 = load_file(get_latest("data/Flass/", "CL32-FL"))


# =========================
# FIX ROSSALL SCHEMA ✅
# =========================
if project == "Rossall Outfall":

    # ----- CL31 FIX -----
    if "Finish" in df31.columns and "BL Project Finish" not in df31.columns:
        df31.rename(columns={"Finish": "BL Project Finish"}, inplace=True)

    # ----- CL32 FIX -----
    # Create missing Activity % Complete
    if "Activity % Complete" not in df32.columns:

        if "Remaining Duration" in df32.columns:
            df32["Activity % Complete"] = df32["Remaining Duration"].apply(
                lambda x: 0 if pd.notnull(x) and x > 0 else 100
            )
        else:
            df32["Activity % Complete"] = 0


# =========================
# SAFETY CHECK
# =========================
if df31 is None or df32 is None:
    st.warning(f"No data available for {project}")
    st.stop()


# =========================
# YOUR ORIGINAL LOGIC ✅
# =========================
result = build_deliverables(df31, df32)
render_dashboard(result, df32)