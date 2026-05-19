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
        raise FileNotFoundError(f"File not found: {path}")

    df = pd.read_excel(path, engine="openpyxl")

    df = _clean_columns(df)
    df.columns = [c.strip() for c in df.columns]

    return df


# =========================
# PROJECT PATHS (✅ NEW)
# =========================
PROJECT_PATHS = {
    "Ferry PS": "data/Ferry/",
    "Flass Lane": "data/Flass/",
    "Rossall Outfall": "data/Rossall/",
}


# =========================
# AUTO DETECT LATEST FILE
# =========================
def _get_latest(prefix, project):

    base_path = PROJECT_PATHS.get(project)

    if not base_path:
        raise ValueError(f"Project not configured in loader: {project}")

    if not os.path.exists(base_path):
        raise FileNotFoundError(f"Folder not found: {base_path}")

    files = [
        f for f in os.listdir(base_path)
        if f.startswith(prefix) and f.endswith(".xlsx")
    ]

    if not files:
        raise FileNotFoundError(f"No {prefix} files in {base_path}")

    files.sort()  # assumes naming consistency

    return os.path.join(base_path, files[-1])


# =========================
# LOAD CL31
# =========================
def load_cl31(project):
    try:
        path = _get_latest("CL31", project)
        return _load(path)
    except Exception:
        return None  # ✅ Placeholder safe


# =========================
# LOAD CL32
# =========================
def load_cl32(project):
    try:
        path = _get_latest("CL32", project)
        return _load(path)
    except Exception:
        return None  # ✅ Placeholder safe


# =========================
# LOAD BOTH (MAIN FUNCTION)
# =========================
def load_project_data(project):
    """
    Main function used by app.py
    Returns df31, df32
    """

    df31 = load_cl31(project)
    df32 = load_cl32(project)

    return df31, df32
``