import pandas as pd
import pdfplumber
import os


# -----------------------------
# PDF EXTRACTION (ROBUST + SAFE)
# -----------------------------
def extract_pdf_table(file_path):
    rows = []

    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            table = page.extract_table()
            if table:
                rows.extend(table)

    df = pd.DataFrame(rows)

    if df.empty:
        return pd.DataFrame()

    # ✅ FLEXIBLE HEADER DETECTION
    header_row_index = None

    for i, row in df.iterrows():
        row_text = " ".join([str(cell) for cell in row if cell])

        if (
            "Activity ID" in row_text
            or ("Activity" in row_text and "ID" in row_text)
        ):
            header_row_index = i
            break

    # ✅ FALLBACK IF HEADER NOT FOUND
    if header_row_index is None:
        header_row_index = 0

    # ✅ SET HEADER
    df.columns = df.iloc[header_row_index]
    df = df.iloc[header_row_index + 1:].reset_index(drop=True)

    return df


# -----------------------------
# FIX COLUMN NAMES (FUZZY MATCH)
# -----------------------------
def fix_column_names(df):
    new_cols = {}

    for col in df.columns:
        col_str = str(col)

        if "Activity ID" in col_str:
            new_cols[col] = "Activity ID"
        elif "Activity Name" in col_str:
            new_cols[col] = "Activity Name"
        elif "Start" in col_str:
            new_cols[col] = "Start"
        elif "Finish" in col_str:
            new_cols[col] = "Finish"
        elif "Remaining" in col_str:
            new_cols[col] = "Remaining Duration"
        elif "Float" in col_str:
            new_cols[col] = "Total Float"
        elif "BL1 Start" in col_str:
            new_cols[col] = "BL Start"
        elif "BL1 Finish" in col_str:
            new_cols[col] = "BL Finish"
        elif "Variance" in col_str:
            new_cols[col] = "Variance"

    return df.rename(columns=new_cols)


# -----------------------------
# STANDARDISE STRUCTURE
# -----------------------------
def standardise(df):
    if df.empty:
        return df

    df.columns = df.columns.astype(str).str.strip()

    # ✅ Fix broken column names first
    df = fix_column_names(df)

    # ✅ If still broken → return safely instead of crashing
    if "Activity ID" not in df.columns:
        return pd.DataFrame()

    # Remove repeated header rows
    df = df[df["Activity ID"] != "Activity ID"]

    # Drop empty rows
    df = df.dropna(how="all")

    # Keep only valid activity rows
    df = df[
        df["Activity ID"]
        .astype(str)
        .str.contains(r"AMP|[A-Z0-9\-]+", na=False)
    ]

    # -----------------------------
    # Handle CL31 vs CL32
    # -----------------------------
    if "BL Start" not in df.columns:
        df["BL Start"] = None
        df["BL Finish"] = None
        df["Variance"] = 0

    return df


# -----------------------------
# CLEAN NUMERIC FIELDS
# -----------------------------
def clean_numeric(df):
    if df.empty:
        return df

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
# CLEAN DATE FIELDS
# -----------------------------
def clean_dates(df):
    if df.empty:
        return df

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
    if df.empty:
        return df

    # Ensure Comments
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

    # ✅ Extract safely
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