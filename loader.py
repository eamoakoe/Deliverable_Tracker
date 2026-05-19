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

    df.columns = [c.strip() for c in df.columns]

    return df


# =========================
# BASE PATHS
# =========================
BASE_PATH_FERRY = "data/Ferry/"
BASE_PATH_FLASS = "data/Flass/"
BASE_PATH_ROSSALL = "data/Rossall/"


# =========================
# AUTO DETECT LATEST FILE
# =========================
def _get_latest(prefix, base_path):
    if not os.path.exists(base_path):
        raise FileNotFoundError(f"Folder not found: {base_path}")

    files = [
        f for f in os.listdir(base_path)
        if f.lower().startswith(prefix.lower()) and f.endswith(".xlsx")
    ]

    if not files:
        raise FileNotFoundError(
            f"No files found for '{prefix}' in {base_path}"
        )

    files.sort()

    return os.path.join(base_path, files[-1])


# =========================
# FERRY LOADERS
# =========================
def load_cl31(path=None):
    if path:
        return _load(path)
    return _load(_get_latest("CL31", BASE_PATH_FERRY))


def load_cl32(path=None):
    if path:
        return _load(path)
    return _load(_get_latest("CL32", BASE_PATH_FERRY))


# =========================
# FLASS LOADERS
# =========================
def load_cl31_flass(path=None):
    if path:
        return _load(path)
    return _load(_get_latest("CL31-FL", BASE_PATH_FLASS))


def load_cl32_flass(path=None):
    if path:
        return _load(path)
    return _load(_get_latest("CL32-FL", BASE_PATH_FLASS))


# =========================
# ROSSALL LOADERS
# =========================
def load_cl31_rossall(path=None):
    if path:
        return _load(path)
    return _load(_get_latest("CL31-RO", BASE_PATH_ROSSALL))


def load_cl32_rossall(path=None):
    if path:
        return _load(path)
    return _load(_get_latest("CL32-RO", BASE_PATH_ROSSALL))


# =========================
# OPTIONAL UNIVERSAL LOADER (BEST PRACTICE)
# =========================
def load_site(site, prefix, path=None):
    """
    Generic loader for any site and prefix
    """

    base_paths = {
        "ferry": BASE_PATH_FERRY,
        "flass": BASE_PATH_FLASS,
        "rossall": BASE_PATH_ROSSALL,
    }

    if path:
        return _load(path)

    site = site.lower()

    if site not in base_paths:
        raise ValueError(f"Unknown site: {site}")

    return _load(_get_latest(prefix, base_paths[site]))
``