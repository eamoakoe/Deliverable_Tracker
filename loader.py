import pandas as pd
import re
import os


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
        raise FileNotFoundError(f"Missing file: {path}")

    df = pd.read_excel(path, engine="openpyxl")
    df = _clean_columns(df)
    df.columns = [c.strip() for c in df.columns]

    return df


# =========================
# PROJECT FILE MAP
# =========================
PROJECT_FILES = {
    "Ferry PS": {
        "cl31": "data/Ferry/CL31-Ferry.xlsx",
        "cl32": "data/Ferry/CL32-Ferry.xlsx",
    },
    "Flass Lane": {
        "cl31": "data/Flass/CL31-FL-March.xlsx",
        "cl32": "data/Flass/CL32-FL-March.xlsx",
    },
    "Rossall Outfall": {
        "cl31": "data/Rossall/CL31-RO-March.xlsx",
        "cl32": "data/Rossall/CL32-RO-May.xlsx",
    },
}


# =========================
# LOAD FUNCTIONS
# =========================
def load_cl31(project):
    return _load(PROJECT_FILES[project]["cl31"])


def load_cl32(project):
    return _load(PROJECT_FILES[project]["cl32"])


def load_project_data(project):
    df31 = load_cl31(project)
    df32 = load_cl32(project)
    return df31, df32
