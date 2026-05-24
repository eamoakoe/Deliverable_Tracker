import pandas as pd
import pdfplumber
import os
import re


# -----------------------------
# PDF EXTRACTION
# -----------------------------
def extract_pdf_table(file_path):
    rows = []

    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            table = page.extract_table()

            if table:
                for row in table:
                    if row:
                        rows.append(row)

    df = pd.DataFrame(rows)

    # Use first real header row
    df.columns = df.iloc[0]
    df = df[1:]

    return df


# -----------------------------
# CLEAN / NORMALISE STRUCTURE
# -----------------------------
def standardise(df):
    # Clean column names
    df.columns = df.columns.astype(str).str.strip()

    # Drop repeated header rows
    if "Activity ID" in df.columns:
        df = df[df["Activity ID"] != "Activity ID"]

    # Drop completely empty rows
    df = df.dropna(how="all")

    # Filter only real activities (removes timeline junk)
    df = df[
        df["Activity ID"].astype(str).str.contains(
            r"AMP|[A-Z0-9\-]+", na=False
        )
    ]

    # -----------------------------
    # CL32 STRUCTURE (baseline columns present)
    # -----------------------------
    if "BL1 Start" in df.columns:
        df = df.rename(columns={
            "BL1 Start": "BL Start",
            "BL1 Finish": "BL Finish",
            "Variance - BL1 Duration": "Variance"
        })

    # -----------------------------
    # CL31 STRUCTURE (no baseline)
    # -----------------------------
    else:
        df["BL Start"] = None
        df["BL Finish"] = None
        df["Variance"] = 0

        # Fix Finish column
        if "Finish" in df.columns and "BL Project Finish" not in df.columns:
            df.rename(columns={"Finish": "BL Project Finish"}, inplace=True)

    return df


# -----------------------------
# CLEAN NUMERIC FIELDS
# -----------------------------
def clean_duration(df):
    if "Remaining Duration" in df.columns:
        df["Remaining Duration"] = (
            df["Remaining Duration"]
            .astype(str)
            .str.replace("d", "", regex=False)
        )
        df["Remaining Duration"] = pd.to_numeric(
            df["Remaining Duration"], errors="coerce"
        )

    if "Total Float" in df.columns:
        df["Total Float"] = (
            df["Total Float"]
            .astype(str)
            .str.replace("d", "", regex=False)
        )
        df["Total Float"] = pd.to_numeric(
            df["Total Float"], errors="coerce"
        )

    return df


# -----------------------------
# CLEAN DATE FIELDS
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
def add_progress(df):
    # Add Comments column if missing
    if "Comments" not in df.columns:
        df["Comments"] = ""

    # Create Activity % Complete
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

    # Extract
    cl31 = extract_pdf_table(cl31_path)
    cl32 = extract_pdf_table(cl32_path)

    # Standardise
    cl31 = standardise(cl31)
    cl32 = standardise(cl32)

    # Clean
    cl31 = clean_duration(cl31)
    cl32 = clean_duration(cl32)

    cl31 = clean_dates(cl31)
    cl32 = clean_dates(cl32)

    # Add derived fields
    cl31 = add_progress(cl31)
    cl32 = add_progress(cl32)

    return cl31, cl32