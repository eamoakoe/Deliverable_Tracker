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

    cl31_path = get_latest(base, "CL31-FL")
    cl32_path = get_latest(base, "CL32-FL")

    if not cl31_path or not cl32_path:
        raise FileNotFoundError("Flass files not found in data/Flass/")

    cl31 = pd.read_excel(cl31_path, engine="openpyxl")
    cl32 = pd.read_excel(cl32_path, engine="openpyxl")

    # ✅ Clean column names
    cl31.columns = cl31.columns.str.strip()
    cl32.columns = cl32.columns.str.strip()

    # ✅ Ensure Comments column exists
    if "Comments" not in cl32.columns:
        cl32["Comments"] = ""

    # ✅ Ensure Activity % Complete exists
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