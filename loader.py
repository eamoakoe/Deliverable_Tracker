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
