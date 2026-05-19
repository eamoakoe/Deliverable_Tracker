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

        # Remove weird unicode spaces
        col = col.replace("\u00a0", " ")

        # Remove line breaks
        col = col.replace("\n", " ")

        # Collapse multiple spaces
        col = re.sub(r"\s+", " ", col)

        # Strip whitespace
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

    # Final safety strip
    df.columns = [c.strip() for c in df.columns]

    return df


# =========================
# BASE PATH (DEFAULT FALLBACK)
# =========================
BASE_PATH = "data/Ferry/"


# =========================
# AUTO DETECT LATEST FILE
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

    # Sort alphabetically (works if naming is consistent)
    files.sort()

    return os.path.join(BASE_PATH, files[-1])


# =========================
# LOAD CL31
# =========================
def load_cl31(path=None):
    """
    Load CL31 file.
    If path is provided → load that file (used by sidebar)
    If not → load latest from default BASE_PATH
    """
    if path:
        return _load(path)
    else:
        return _load(_get_latest("CL31"))


# =========================
# LOAD CL32
# =========================
def load_cl32(path=None):
    """
    Load CL32 file.
    If path is provided → load from sidebar selection
    If not → auto-load latest file
    """
    if path:
        return _load(path)
    else:
        return _load(_get_latest("CL32"))