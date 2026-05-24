import pandas as pd
import pdfplumber
import os


# =========================
# EXTRACT PDF TABLE
# =========================
def extract_pdf_table(file_path):
    rows = []

    if not os.path.exists(file_path):
        print("FILE NOT FOUND:", file_path)
        return pd.DataFrame()

    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            table = page.extract_table({
                "vertical_strategy": "lines",
                "horizontal_strategy": "lines"
            })
            if table:
                rows.extend(table)

    df = pd.DataFrame(rows)

    if df.empty:
        return df

    # Detect header row
    header_idx = 0
    for i, row in df.iterrows():
        text = " ".join([str(c) for c in row if c])
        if "Activity" in text and "ID" in text:
            header_idx = i
            break

    df.columns = df.iloc[header_idx]
    df = df.iloc[header_idx + 1:].reset_index(drop=True)

    return df


# =========================
# NORMALISE COLUMNS
# =========================
def normalise_columns(df):
    df.columns = df.columns.astype(str).str.strip()

    rename_map = {
        "Finish Date": "Finish",
        "Rem Dur": "Remaining Duration"
    }

    df = df.rename(columns=rename_map)

    return df


# =========================
# CLEAN DATA
# =========================
def clean(df):

    if df.empty:
        return df

    df = normalise_columns(df)

    df = df.dropna(how="all")

    if "Activity ID" in df.columns:
        df = df[df["Activity ID"] != "Activity ID"]

    if "Activity Name" in df.columns:
        df = df[df["Activity Name"].notna()]

    return df.reset_index(drop=True)


# =========================
# CLEAN DATES
# =========================
def clean_dates(df):
    if "Finish" in df.columns:
        df["Finish"] = pd.to_datetime(df["Finish"], errors="coerce", dayfirst=True)
    return df


# =========================
# CLEAN DURATION
# =========================
def clean_duration(df):
    if "Remaining Duration" in df.columns:
        df["Remaining Duration"] = (
            df["Remaining Duration"]
            .astype(str)
            .str.replace("d", "", regex=False)
            .str.strip()
        )

        df["Remaining Duration"] = pd.to_numeric(df["Remaining Duration"], errors="coerce")

    return df


# =========================
# MAIN LOADER
# =========================
def load_ferry():

    base = "data/Ferry/"

    cl31_path = os.path.join(base, "CL31.pdf")
    cl32_path = os.path.join(base, "CL32.pdf")

    cl31 = extract_pdf_table(cl31_path)
    cl31 = clean(cl31)
    cl31 = clean_dates(cl31)
    cl31 = clean_duration(cl31)

    cl32 = extract_pdf_table(cl32_path)
    cl32 = clean(cl32)
    cl32 = clean_dates(cl32)
    cl32 = clean_duration(cl32)

    return cl31, cl32