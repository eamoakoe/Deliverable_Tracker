import pandas as pd
import os
import re
from datetime import datetime


# =========================
# EXISTING (UNCHANGED)
# =========================
def get_latest(folder, prefix):
    files = [f for f in os.listdir(folder) if f.startswith(prefix) and f.endswith(".xlsx")]
    files.sort()
    return os.path.join(folder, files[-1]) if files else None


# =========================
# NEW: EXTRACT CL32 DATE FROM FILENAME
# =========================
def extract_cl32_date(file_name):

    match = re.search(
        r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[^\d]*(\d{4})",
        file_name,
        re.IGNORECASE
    )

    if not match:
        return None

    month, year = match.groups()
    month = month[:3].title()

    return datetime.strptime(f"{month} {year}", "%b %Y")


# =========================
# NEW: LOAD ALL CL32 FILES (SORTED)
# =========================
def load_cl32_series(folder):

    files = []

    for f in os.listdir(folder):

        if f.startswith("CL32") and f.endswith(".xlsx"):

            date = extract_cl32_date(f)

            if date:
                files.append({
                    "file": f,
                    "date": date
                })

    if not files:
        return []

    # ✅ Sort by real date (NOT alphabetical)
    files = sorted(files, key=lambda x: x["date"])

    # ✅ Load into dataframe list
    data = []

    for item in files:

        path = os.path.join(folder, item["file"])

        df = pd.read_excel(path, engine="openpyxl")

        data.append({
            "name": item["file"],
            "date": item["date"],
            "df": df
        })

    return data


# =========================
# MAIN LOADER (CL31 SAFE ✅)
# =========================
def load_ferry():

    base = "data/Ferry/"

    # ✅ DO NOT TOUCH CL31
    cl31 = pd.read_excel(get_latest(base, "CL31"), engine="openpyxl")

    # ✅ NEW: CL32 SERIES (not single file anymore)
    cl32_series = load_cl32_series(base)

    return cl31, cl32_series
