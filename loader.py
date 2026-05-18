import pandas as pd
import re


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


def _load(path):
    df = pd.read_excel(path, engine="openpyxl")

    df = _clean_columns(df)

    # FINAL SAFETY CHECK (VERY IMPORTANT)
    df.columns = [c.strip() for c in df.columns]

    return df


def load_cl31(path="data/CL31-February.xlsx"):
    return _load(path)


def load_cl32(path="data/CL32-May.xlsx"):
    return _load(path)