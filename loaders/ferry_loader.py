import pandas as pd
import os
import re
from datetime import datetime


def get_latest(folder, prefix):
    files = [f for f in os.listdir(folder) if f.startswith(prefix) and f.endswith(".xlsx")]
    files.sort()
    return os.path.join(folder, files[-1]) if files else None


# =========================
# NEW: extract CL32 date
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
# NEW: load ALL CL32 files
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

    # ✅ sort properly (chronological)
    files = sorted(files, key=lambda x: x["date"])

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
# MAIN LOADER
# =========================
def load_ferry():

    base = "data/Ferry/"

    # ✅ KEEP THIS (used by other pages)
    cl31 = pd.read_excel(get_latest(base, "CL31"), engine="openpyxl")

    # ✅ KEEP THIS (existing behaviour)
    cl32 = pd.read_excel(get_latest(base, "CL32"), engine="openpyxl")

    # ✅ ADD THIS (new capability)
    cl32_series = load_cl32_series(base)

    return cl31, cl32, cl32_series