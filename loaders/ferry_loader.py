import pandas as pd
import pdfplumber
import os
import re


# =========================
# ✅ EXTRACT FROM PDF TEXT
# =========================
def extract_pdf_table(file_path):

    rows = []

    if not os.path.exists(file_path):
        print("❌ FILE NOT FOUND:", file_path)
        return pd.DataFrame()

    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:

            text = page.extract_text()

            if not text:
                continue

            lines = text.split("\n")

            for line in lines:

                # ✅ Ferry activity IDs always contain AMP8-FPS
                if "AMP8-FPS" in line:
                    rows.append(line.strip())

    if not rows:
        print("❌ NO ROWS FOUND")
        return pd.DataFrame()

    return pd.DataFrame({"raw": rows})


# =========================
# ✅ CLEAN + PARSE STRUCTURE
# =========================
def clean(df):

    if df.empty:
        return df

    parsed = []

    for line in df["raw"]:

        parts = line.split()

        # skip broken rows
        if len(parts) < 4:
            continue

        activity_id = parts[0]

        # =========================
        # ✅ FIND FINISH DATE (last valid date)
        # =========================
        finish = None
        for p in reversed(parts):
            if re.match(r"\d{2}-[A-Za-z]{3}-\d{2}", p):
                finish = p
                break

        # =========================
        # ✅ FIND DURATION (value ending with d)
        # =========================
        duration = None
        for p in parts:
            if p.endswith("d"):
                duration = p

        # =========================
        # ✅ ACTIVITY NAME
        # =========================
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

    df_clean = pd.DataFrame(parsed)

    if df_clean.empty:
        print("❌ CLEANED DATA EMPTY")
        return df_clean

    # =========================
    # ✅ CONVERT DATE
    # =========================
    df_clean["Finish"] = pd.to_datetime(
        df_clean["Finish"],
        errors="coerce",
        dayfirst=True
    )

    # =========================
    # ✅ CONVERT DURATION
    # =========================
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

    cl31 = clean(extract_pdf_table(cl31_path))
    cl32 = clean(extract_pdf_table(cl32_path))

    print("✅ CL31 rows:", len(cl31))
    print("✅ CL32 rows:", len(cl32))

    return cl31, cl32
