import pandas as pd
import pdfplumber
import os


# -----------------------------
# PDF EXTRACTION (ROBUST)
# -----------------------------
def extract_pdf_table(file_path):
    rows = []

    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            table = page.extract_table()

            if table:
                rows.extend(table)

    df = pd.DataFrame(rows)

    # ✅ FIND REAL HEADER ROW
    header_row_index = None

    for i, row in df.iterrows():
        if any("Activity ID" in str(cell) for cell in row):
            header_row_index = i
            break

    if header_row_index is None:
        raise ValueError(f"Header row not found in {file_path}")

    # ✅ SET HEADER
    df.columns = df.iloc[header_row_index]
    df = df.iloc[header_row_index + 1:]

    df = df.reset_index(drop=True)

    return df


# -----------------------------
# STANDARDISE STRUCTURE
# -----------------------------
def standardise(df):
    df.columns = df.columns.astype(str).str.strip()

    # ✅ SAFETY CHECK
    if "Activity ID" not in df.columns:
        raise ValueError("Column 'Activity ID' not found after parsing")

    # Remove repeated headers
    df = df[df["Activity ID"] != "Activity ID"]

    # Drop empty rows
    df = df.dropna(how="all")

    # Keep valid rows only (removes timeline junk)
    df = df[
        df["Activity ID"]
        .astype(str)
        .str.contains(r"AMP|[A-Z0-9\-]+", na=False)
    ]

    # -----------------------------
    # CL32 (baseline present)
    # -----------------------------
    if "BL1 Start" in df.columns:
        df = df.rename(columns={
            "BL1 Start": "BL Start",
            "BL1 Finish": "BL Finish",
            "Variance - BL1 Duration": "Variance"
        })

    # -----------------------------
    # CL31 (no baseline)
    # -----------------------------
    else:
        df["BL Start"] = None
        df["BL Finish"] = None
        df["Variance"] = 0

        if "Finish" in df.columns:
            df.rename(columns={"Finish": "BL Project Finish"}, inplace=True)

    return df


# -----------------------------
# CLEAN NUMERIC COLUMNS
# -----------------------------
def clean_numeric(df):
    for col in ["Remaining Duration", "Total Float"]:
        if col in df.columns:
            df[col] = (
                df[col]
                .astype(str)
                .str.replace("d", "", regex=False)
            )
            df[col] = pd.to_numeric(df[col], errors="coerce")

    if "Variance" in df.columns:
        df["Variance"] = pd.to_numeric(df["Variance"], errors="coerce")

    return df


# -----------------------------
# CLEAN DATE COLUMNS
# -----------------------------
def clean_dates(df):
    date_cols = ["Start", "Finish", "BL Start", "BL Finish"]

    for col in date_cols:
        if col in df.columns:
            df[col] = (
                df[col]
                .astype(str)
                .str.replace(" A", "", regex=False)
                .str.replace("*", "", regex=False)
            )
            df[col] = pd.to_datetime(df[col], errors="coerce")

    return df


# -----------------------------
# ADD DERIVED FIELDS
# -----------------------------
def add_fields(df):
    # Ensure Comments column
    if "Comments" not in df.columns:
        df["Comments"] = ""

    # Activity % Complete
    if "Activity % Complete" not in df.columns:
        if "Remaining Duration" in df.columns:
            df["Activity % Complete"] = df["Remaining Duration"].apply(
                lambda x: 0 if pd.notnull(x) and x > 0 else 100
            )
        else:
            df["Activity % Complete"] = 0

    return df


# -----------------------------
# MAIN LOADER
# -----------------------------
def load_rossall():
    base = "data/Rossall/"

    cl31_path = os.path.join(base, "CL31-RO-November-2025.pdf")
    cl32_path = os.path.join(base, "CL32-RO-May-2026.pdf")

    # ✅ Extract
    cl31 = extract_pdf_table(cl31_path)
    cl32 = extract_pdf_table(cl32_path)

    # ✅ Standardise
    cl31 = standardise(cl31)
    cl32 = standardise(cl32)

    # ✅ Clean
    cl31 = clean_numeric(cl31)
    cl32 = clean_numeric(cl32)

    cl31 = clean_dates(cl31)
    cl32 = clean_dates(cl32)

    # ✅ Derived fields
    cl31 = add_fields(cl31)
    cl32 = add_fields(cl32)

    return cl31, cl32
