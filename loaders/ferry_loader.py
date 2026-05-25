import pandas as pd
import pdfplumber
import os


# =========================
# EXTRACT PDF TABLE (FERRY-SPECIFIC)
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
        print("No table extracted")
        return df

    # =========================
    # ✅ HEADER DETECTION (FERRY-TUNED)
    # =========================
    header_idx = None

    for i, row in df.iterrows():

        row_values = [str(c).strip().lower() for c in row if c]

        score = 0

        if any("id" in v for v in row_values):
            score += 1
        if any("name" in v for v in row_values):
            score += 1
        if any("duration" in v for v in row_values):
            score += 1
        if any("finish" in v for v in row_values):
            score += 1

        if score >= 2:
            header_idx = i
            break

    if header_idx is None:
        print("Header not found — fallback to row 0")
        header_idx = 0

    df.columns = df.iloc[header_idx]
    df = df.iloc[header_idx + 1:].reset_index(drop=True)

    return df


# =========================
# ✅ CLEAN (FERRY-SPECIFIC)
# =========================
def clean(df):

    if df.empty:
        return df

    # Clean column names
    df.columns = df.columns.astype(str).str.strip()

    rename_map = {
        "Finish Date": "Finish",
        "Actual Finish": "Finish",
        "Rem Dur": "Remaining Duration"
    }

    df = df.rename(columns=rename_map)

    # Remove repeated header rows
    if "Activity ID" in df.columns:
        df = df[df["Activity ID"] != "Activity ID"]

    # Drop empty rows
    df = df.dropna(how="all")

    # Keep valid activities
    if "Activity Name" in df.columns:
        df = df[df["Activity Name"].notna()]
    else:
        print("Missing Activity Name column")
        return pd.DataFrame()

    # ✅ Convert Finish date
    if "Finish" in df.columns:
        df["Finish"] = pd.to_datetime(
            df["Finish"],
            errors="coerce",
            dayfirst=True
        )

    # ✅ Convert Remaining Duration
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
        print("No Remaining Duration column")
        df["Remaining Duration"] = None

    return df.reset_index(drop=True)


# =========================
# ✅ MAIN LOADER
# =========================
def load_ferry():

    base = "data/Ferry/"

    cl31_path = os.path.join(base, "CL31.pdf")
    cl32_path = os.path.join(base, "CL32.pdf")

    # ✅ CL31
    cl31 = extract_pdf_table(cl31_path)
    cl31 = clean(cl31)

    print("CL31 shape:", cl31.shape)

    # ✅ CL32
    cl32 = extract_pdf_table(cl32_path)
    cl32 = clean(cl32)

    print("CL32 shape:", cl32.shape)

    return cl31, cl32