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

        # remove weird unicode spaces
        col = col.replace("\u00a0", " ")

        # remove line breaks
        col = col.replace("\n", " ")

        # collapse multiple spaces
        col = re.sub(r"\s+", " ", col)

        # strip
        col = col.strip()

        cleaned.append(col)

    df.columns = cleaned
    return df


# =========================
# LOAD FILE
# =========================
def _load(path):
    df = pd.read_excel(path, engine="openpyxl")

    df = _clean_columns(df)

    # final safety
    df.columns = [c.strip() for c in df.columns]

    return df


# =========================
# BASE PATH
# =========================
BASE_PATH = "data/Ferry/"


# =========================
# AUTO DETECT LATEST FILE
# =========================
def _get_latest(prefix):
    if not os.path.exists(BASE_PATH):
        raise FileNotFoundError(f"Folder not found: {BASE_PATH}")

    files = [f for f in os.listdir(BASE_PATH)
             if f.startswith(prefix) and f.endswith(".xlsx")]

    if not files:
        raise FileNotFoundError(f"No files found for {prefix} in {BASE_PATH}")

    files.sort()
    return os.path.join(BASE_PATH, files[-1])


# =========================
# LOAD CL31
# =========================
def load_cl31(path=None):
    if path is None:
        path = _get_latest("CL31")

    return _load(path)


# =========================
# LOAD CL32
# =========================
def load_cl32(path=None):
    if path is None:
        path = _get_latest("CL32")

    return _load(path)
