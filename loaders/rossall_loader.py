import pandas as pd
import rows = []import pdfplumber

    if not os.path.exists(file_path):
        print("❌ FILE NOT FOUND:", file_path)
        return pd.DataFrame()

    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            table = page.extract_table()
            if table:
                rows.extend(table)

    df = pd.DataFrame(rows)

    if df.empty:
        return df

    # ✅ Detect header
    header_row_index = 0
    for i, row in df.iterrows():
        row_text = " ".join([str(cell) for cell in row if cell])
        if "Activity" in row_text and "ID" in row_text:
            header_row_index = i
            break

    df.columns = df.iloc[header_row_index]
    df = df.iloc[header_row_index + 1:].reset_index(drop=True)

    return df


def clean(df):
    if df.empty:
        return df

    df.columns = df.columns.astype(str).str.strip()

    if "Activity ID" in df.columns:
        df = df[df["Activity ID"] != "Activity ID"]

    df = df.dropna(how="all")

    return df


def load_rossall():

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    cl31_path = os.path.join(BASE_DIR, "data", "Rossall", "CL31-RO-November-2025.pdf")
    cl32_path = os.path.join(BASE_DIR, "data", "Rossall", "CL32-RO-May-2026.pdf")

    cl31 = extract_pdf_table(cl31_path)
    cl32 = extract_pdf_table(cl32_path)

    cl31 = clean(cl31)
    cl32 = clean(cl32)

    return cl31, cl32
import os


def extract_pdf_table(file_path):
