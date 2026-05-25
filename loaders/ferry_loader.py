import pandas as pd
import pdfplumber
import os


# =========================
# ✅ EXTRACT FROM TEXT (REAL FIX)
# =========================
def extract_pdf_table(file_path):

    rows = []

    if not os.path.exists(file_path):
        print("FILE NOT FOUND:", file_path)
        return pd.DataFrame()

    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:

            text = page.extract_text()

            if not text:
                continue

            lines = text.split("\n")

            for line in lines:

                # ✅ Only capture real activity rows
                # Ferry IDs always look like AMP8-FPS-XXXX
                if "AMP8" in line:

                    parts = line.split()

                    rows.append(parts)

    if not rows:
        print("No rows extracted from text")
        return pd.DataFrame()

    df = pd.DataFrame(rows)

    return df


# =========================
# ✅ CLEAN DATA (FERRY-SPECIFIC)
# =========================
def clean(df):

    if df.empty:
        return df

    # Drop empty rows
    df = df.dropna(how="all")

    # ✅ We don't have proper columns yet, so we standardise positions
    # Based on your PDF structure:
    # col0 = Activity ID
    # col1+ = Activity Name (variable length)
    # last columns = duration + dates

    cleaned_rows = []

    for _, row in df.iterrows():

        values = [str(x) for x in row if pd.notna(x)]

        if len(values) < 5:
            continue

        # ✅ Extract known structure
        activity_id = values[0]

        # Remaining Duration usually looks like "10d"
        duration = None
        finish = None

        for v in reversed(values):

            if "d" in v:
                duration = v

            if "-" in v and v[0].isdigit():
                finish = v

        # Activity name = everything between ID and duration
        name_parts = values[1:-3] if len(values) > 4 else values[1:]

        activity_name = " ".join(name_parts)

        cleaned_rows.append({
            "Activity ID": activity_id,
            "Activity Name": activity_name,
            "Remaining Duration": duration,
            "Finish": finish
        })

    df_clean = pd.DataFrame(cleaned_rows)

    # ✅ Convert Finish date
    if "Finish" in df_clean.columns:
        df_clean["Finish"] = pd.to_datetime(
            df_clean["Finish"],
            errors="coerce",
            dayfirst=True
        )

    # ✅ Convert duration
    if "Remaining Duration" in df_clean.columns:

        df_clean["Remaining Duration"] = (
            df_clean["Remaining Duration"]
            .astype(str)
            .str.replace("d", "", regex=False)
            .str.strip()
        )

        df_clean["Remaining Duration"] = pd.to_numeric(
            df_clean["Remaining Duration"],
            errors="coerce"
        )

    return df_clean


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

    print("CL31 rows:", len(cl31))

    # ✅ CL32
    cl32 = extract_pdf_table(cl32_path)
    cl32 = clean(cl32)

    print("CL32 rows:", len(cl32))

    return cl31, cl32