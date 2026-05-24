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

    # ✅ Detect header row
    header_idx = None
    for i, row in df.iterrows():
        text = " ".join([str(c) for c in row if c])
        if "Activity ID" in text and "Activity Name" in text:
            header_idx = i
            break

    if header_idx is None:
        return pd.DataFrame()

    df.columns = df.iloc[header_idx]
    df = df.iloc[header_idx + 1:].reset_index(drop=True)

    return df


# =========================
# ✅ UNIVERSAL CLEAN (FINAL)
# =========================
def clean(df):

    if df.empty:
        return df

    # ✅ Standardise column names
    df.columns = df.columns.astype(str).str.strip()

    rename_map = {
        "Finish Date": "Finish",
        "Actual Finish": "Finish",
        "Original Duration": "Remaining Duration",
        "Rem Dur": "Remaining Duration"
    }

    df = df.rename(columns=rename_map)

    # ✅ Remove junk rows
    if "Activity ID" in df.columns:
        df = df[df["Activity ID"] != "Activity ID"]

    df = df.dropna(how="all")

    if "Activity Name" in df.columns:
        df = df[df["Activity Name"].notna()]
    else:
        return pd.DataFrame()

    # ✅ Convert dates
    if "Finish" in df.columns:
        df["Finish"] = pd.to_datetime(
            df["Finish"],
            errors="coerce",
            dayfirst=True
        )

    # ✅ Convert duration (CRITICAL)
    if "Remaining Duration" in df.columns:

        df["Remaining Duration"] = (
            df["Remaining Duration"]
            .astype(str)
            .str.replace("d", "", regex=False)
            .str.strip()
        )

        df["Remaining Duration"] = pd.to_numeric(
            df["Remaining Duration"],
            errors="coerce"
        )

    else:
        # ✅ fallback for CL31 cases like Flass
        df["Remaining Duration"] = None

    return df.reset_index(drop=True)


# =========================
# ✅ MAIN LOADER (SIMPLIFIED)
# =========================
def load_ferry():

    base = "data/Ferry/"

    cl31_path = os.path.join(base, "CL31.pdf")
    cl32_path = os.path.join(base, "CL32.pdf")

    cl31 = extract_pdf_table(cl31_path)
    cl31 = clean(cl31)

    cl32 = extract_pdf_table(cl32_path)
    cl32 = clean(cl32)

    return cl31, cl32