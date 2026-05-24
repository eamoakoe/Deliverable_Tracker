import pandas as pd
import pdfplumber
import os


# -----------------------------
# PDF EXTRACTION
# -----------------------------
def extract_pdf_table(file_path):
    rows = []

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
        print("❌ EMPTY EXTRACTION:", file_path)
        return df

    # ✅ Find header row dynamically
    header_row_index = 0
    for i, row in df.iterrows():
        row_text = " ".join([str(cell) for cell in row if cell])
        if "Activity" in row_text and "ID" in row_text:
            header_row_index = i
            break

    df.columns = df.iloc[header_row_index]
    df = df.iloc[header_row_index + 1:].reset_index(drop=True)

    return df


# -----------------------------
# CLEAN DATA
# -----------------------------
def clean(df):
    if df.empty:
        return df

    df.columns = df.columns.astype(str).str.strip()

    # Remove repeated header rows
    if "Activity ID" in df.columns:
        df = df[df["Activity ID"] != "Activity ID"]

    df = df.dropna(how="all")

    return df


# -----------------------------
# MAIN LOADER
# -----------------------------
def load_rossall():

    # ✅ PROJECT ROOT
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    cl31_path = os.path.join(BASE_DIR, "data", "Rossall", "CL31-RO-November-2025.pdf")
    cl32_path = os.path.join(BASE_DIR, "data", "Rossall", "CL32-RO-May-2026.pdf")

    # ✅ DEBUG (will show in logs)
    print("BASE DIR:", BASE_DIR)
    print("CL31 EXISTS:", os.path.exists(cl31_path))
    print("CL32 EXISTS:", os.path.exists(cl32_path))

    cl31 = extract_pdf_table(cl31_path)
    cl32 = extract_pdf_table(cl32_path)

    cl31 = clean(cl31)
    cl32 = clean(cl32)

    print("CL31 SHAPE:", cl31.shape)
    print("CL32 SHAPE:", cl32.shape)

    return cl31, cl32