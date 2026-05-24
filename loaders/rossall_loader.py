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

    if df.empty:
        return pd.DataFrame()

    # ✅ Header detection (flexible)
    header_row_index = None

    for i, row in df.iterrows():
        row_text = " ".join([str(cell) for cell in row if cell])

        if "Activity" in row_text and "ID" in row_text:
            header_row_index = i
            break

    if header_row_index is None:
        header_row_index = 0  # fallback

    df.columns = df.iloc[header_row_index]
    df = df.iloc[header_row_index + 1:].reset_index(drop=True)

    return df


# -----------------------------
# FIX COLUMN NAMES
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
# ENSURE ACTIVITY NAME EXISTS
# -----------------------------
def ensure_full_activity_name(df):
    # Case 1: already exists
    if "Activity Name" in df.columns:
        df["Activity Name"] = df["Activity Name"].fillna("").astype(str).str.strip()
        return df

    # Case 2: merged column
    for col in df.columns:
        col_str = str(col)

        if "Activity ID" in col_str and "Activity Name" in col_str:
            split_data = df[col].astype(str).str.split(" ", n=1, expand=True)

            df["Activity ID"] = split_data[0]

            if split_data.shape[1] > 1:
                df["Activity Name"] = split_data[1]
            else:
                df["Activity Name"] = ""

            df = df.drop(columns=[col])
            return df

    # Case 3: fallback (never fail)
    df["Activity Name"] = ""

    return df


# -----------------------------
# STANDARDISE STRUCTURE
# -----------------------------
def standardise(df):
    if df.empty:
        return df

    df.columns = df.columns.astype(str).str.strip()

    # ✅ Fix names
    df = fix_column_names(df)

    # ✅ Ensure name exists (fix your current error)
    df = ensure_full_activity_name(df)

    if "Activity ID" not in df.columns:
        return pd.DataFrame()

    # Remove repeated headers
    df = df[df["Activity ID"] != "Activity ID"]

    # Drop empty
    df = df.dropna(how="all")

    # Keep valid activities only
    df = df[
        df["Activity ID"]
        .astype(str)
        .str.contains(r"AMP|[A-Z0-9\-]+", na=False)
    ]

    # CL31 fallback
    if "BL Start" not in df.columns:
        df["BL Start"] = None
        df["BL Finish"] = None
        df["Variance"] = 0

    return df


# -----------------------------
# CLEAN NUMERIC
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
# CLEAN DATES
# -----------------------------
def clean_dates(df):
    if df.empty:
        return df

    for col in ["Start", "Finish", "BL Start", "BL Finish"]:
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
# DERIVED FIELDS
# -----------------------------
def add_fields(df):
    if df.empty:
        return df

    if "Comments" not in df.columns:
        df["Comments"] = ""

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

    cl31 = extract_pdf_table(cl31_path)
    cl32 = extract_pdf_table(cl32_path)

    cl31 = standardise(cl31)
    cl32 = standardise(cl32)

    cl31 = clean_numeric(cl31)
    cl32 = clean_numeric(cl32)

    cl31 = clean_dates(cl31)
    cl32 = clean_dates(cl32)

    cl31 = add_fields(cl31)
    cl32 = add_fields(cl32)

    return cl31, cl32