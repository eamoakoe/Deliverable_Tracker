import pandas as pd
import pdfplumber
import os


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
                if "AMP" in line:
                    rows.append(line.strip())

    if not rows:
        print("NO ROWS FOUND")
        return pd.DataFrame()

    return pd.DataFrame({"raw": rows})


def clean(df):

    if df.empty:
        return df

    parsed = []

    for line in df["raw"]:

        parts = line.split()

        if len(parts) < 4:
            continue

        parsed.append({
            "Activity ID": parts[0],
            "Activity Name": " ".join(parts[1:])
        })

    return pd.DataFrame(parsed)


def load_ferry():

    base = "data/Ferry/"

    cl31 = clean(extract_pdf_table(os.path.join(base, "CL31.pdf")))
    cl32 = clean(extract_pdf_table(os.path.join(base, "CL32.pdf")))

    print("CL31 rows:", len(cl31))
    print("CL32 rows:", len(cl32))

    return cl31, cl32