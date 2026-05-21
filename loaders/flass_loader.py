import pandas as pd
import os


def get_latest(folder, prefix):
    files = [
        f for f in os.listdir(folder)
        if f.startswith(prefix) and f.endswith(".xlsx")
    ]
    files.sort()
    return os.path.join(folder, files[-1]) if files else None


def load_flass():
    base = "data/Flass/"

    cl31 = pd.read_excel(get_latest(base, "CL31-RO"), engine="openpyxl")
    cl32 = pd.read_excel(get_latest(base, "CL32-RO"), engine="openpyxl")

    # ✅ CLEAN COLUMN NAMES (prevents hidden space issues)
    cl31.columns = cl31.columns.str.strip()
    cl32.columns = cl32.columns.str.strip()

    # ✅ FIX 1: Finish → BL Project Finish
    if "Finish" in cl31.columns and "BL Project Finish" not in cl31.columns:
        cl31.rename(columns={"Finish": "BL Project Finish"}, inplace=True)

    # ✅ FIX 2: Ensure Comments column exists (Rossall file doesn't have it)
    if "Comments" not in cl32.columns:
        cl32["Comments"] = ""

    # ✅ FIX 3: Create Activity % Complete
    if "Activity % Complete" not in cl32.columns:
        if "Remaining Duration" in cl32.columns:
            cl32["Remaining Duration"] = pd.to_numeric(
                cl32["Remaining Duration"], errors="coerce"
            )

            cl32["Activity % Complete"] = cl32["Remaining Duration"].apply(
                lambda x: 0 if pd.notnull(x) and x > 0 else 100
            )
        else:
            cl32["Activity % Complete"] = 0

    return cl31, cl32