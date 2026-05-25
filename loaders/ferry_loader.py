import pandas as pd
import pdfplumber
import os
import re


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

import(file_path):

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

                # ✅ Strict pattern: Activity IDs look like AMP8-FPS-XXXX
                if re.match(r"AMP\d+-FPS-", line):

                    rows.append(line.strip())

    if not rows:
        print("❌ NO MATCHED ACTIVITY ROWS")
        return pd.DataFrame()

    parsed = []

    for line in rows:

        parts = line.split()

        # ✅ Skip broken lines
        if len(parts) < 4:
            continue

        activity_id = parts[0]

        # ✅ Extract finish date (last valid date-looking token)
        finish = None

        for p in reversed(parts):
            if re.match(r"\d{2}-[A-Za-z]{3}-\d{2}", p):
                finish = p
                break

        # ✅ Extract duration (token ending with d)
        duration = None
        for p in parts:
            if p.endswith("d"):
                duration = p

        # ✅ Activity name = everything between ID and duration
        try:
            dur_index = parts.index(duration) if duration else len(parts)
        except:
            dur_index = len(parts)

        name_parts = parts[1:dur_index]

        activity_name = " ".join(name_parts)

        parsed.append({
            "Activity ID": activity_id,
            "Activity Name": activity_name,
            "Remaining Duration": duration,
            "Finish": finish
        })

    df = pd.DataFrame(parsed)

    return df


# =========================
# ✅ CLEAN DATA (SAFE)
# =========================
def clean(df):

    if df.empty:
        return df

    # Convert Finish
    df["Finish"] = pd.to_datetime(
        df["Finish"],
        errors="coerce",
        dayfirst=True
    )

    # Convert duration
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

    return df


# =========================
# ✅ MAIN LOADER
# =========================
def load_ferry():

    base = "data/Ferry/"

    cl31_path = os.path.join(base, "CL31.pdf")
    cl32_path = os.path.join(base, "CL32.pdf")

    cl31 = clean(extract_pdf_table(cl31_path))
    cl32 = clean(extract_pdf_table(cl32_path))

    print("✅ CL31 rows:", len(cl31))
    print("✅ CL32 rows:", len(cl32))

    return cl31, cl32
import pdfplumber
import os
import re


# =========================
# ✅ EXTRACT + PARSE CORRECTLY
# =========================
