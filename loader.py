import pandas as pd
import re
import os
import streamlit as st


# =========================
# CLEAN COLUMNS
# =========================
def _clean_columns(df):
    cleaned = []

    for col in df.columns:
        col = str(col)
        col = col.replace("\u00a0", " ")
        col = col.replace("\n", " ")
        col = re.sub(r"\s+", " ", col)
        col = col.strip()
        cleaned.append(col)

    df.columns = cleaned
    return df


# =========================
# LOAD FILE
# =========================
def _load(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")

    df = pd.read_excel(path, engine="openpyxl")
    df = _clean_columns(df)
    df.columns = [c.strip() for c in df.columns]

    return df


# =========================
# BASE PATH (EXISTING - DO NOT TOUCH)
# =========================
BASE_PATH = "data/Ferry/"


# =========================
# AUTO DETECT LATEST FILE (EXISTING)
# =========================
def _get_latest(prefix):
    if not os.path.exists(BASE_PATH):
        raise FileNotFoundError(f"Folder not found: {BASE_PATH}")

    files = [
        f for f in os.listdir(BASE_PATH)
        if f.startswith(prefix) and f.endswith(".xlsx")
    ]

    if not files:
        raise FileNotFoundError(f"No files found for {prefix} in {BASE_PATH}")

    files.sort()

    return os.path.join(BASE_PATH, files[-1])


# =========================
# EXISTING LOADERS (UNCHANGED)
# =========================
def load_cl31(path=None):
    if path:
        return _load(path)
    else:
        return _load(_get_latest("CL31"))


def load_cl32(path=None):
    if path:
        return _load(path)
    else:
        return _load(_get_latest("CL32"))


# =========================
# NEW BASE PATHS
# =========================
BASE_PATH_FLASS = "data/Flass/"
BASE_PATH_ROSSALL = "data/Rossall/"


# =========================
# NEW GET LATEST (SAFE)
# =========================
def _get_latest_from(base_path, prefix):
    if not os.path.exists(base_path):
        raise FileNotFoundError(f"Folder not found: {base_path}")

    files = [
        f for f in os.listdir(base_path)
        if f.lower().startswith(prefix.lower()) and f.endswith(".xlsx")
    ]

    if not files:
        raise FileNotFoundError(f"No files found for {prefix} in {base_path}")

    files.sort()

    return os.path.join(base_path, files[-1])


# =========================
# FLASS (NEW)
# =========================
def load_cl31_flass(path=None):
    if path:
        return _load(path)
    return _load(_get_latest_from(BASE_PATH_FLASS, "CL31-FL"))


def load_cl32_flass(path=None):
    if path:
        return _load(path)
    return _load(_get_latest_from(BASE_PATH_FLASS, "CL32-FL"))


# =========================
# ROSSALL (NEW)
# =========================
def load_cl31_rossall(path=None):
    if path:
        return _load(path)
    return _load(_get_latest_from(BASE_PATH_ROSSALL, "CL31-RO"))


def load_cl32_rossall(path=None):
    if path:
        return _load(path)
    return _load(_get_latest_from(BASE_PATH_ROSSALL, "CL32-RO"))


# =========================
# SIDEBAR UI
# =========================
st.sidebar.title("Data Selection")

site = st.sidebar.selectbox(
    "Select Site",
    ["Ferry", "Flass", "Rossall"]
)

dataset = st.sidebar.selectbox(
    "Select Dataset",
    ["CL31", "CL32"]
)


# =========================
# LOAD DATA BASED ON SELECTION
# =========================
try:
    if site == "Ferry":
        if dataset == "CL31":
            df = load_cl31()
        else:
            df = load_cl32()

    elif site == "Flass":
        if dataset == "CL31":
            df = load_cl31_flass()
        else:
            df = load_cl32_flass()

    elif site == "Rossall":
        if dataset == "CL31":
            df = load_cl31_rossall()
        else:
            df = load_cl32_rossall()

    # =========================
    # DISPLAY
    # =========================
    st.title("Data Viewer")

    st.write(f"📍 Site: {site}")
    st.write(f"📊 Dataset: {dataset}")

    st.dataframe(df)

except Exception as e:
    st.error(f"Error loading data: {e}")
