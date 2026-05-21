import pandas as pd
import os


def get_latest(folder, prefix):
    files = [
        f for f in os.listdir(folder)
        if f.startswith(prefix) and f.endswith(".xlsx")
    ]

    if not files:
        return None

    files.sort()
    return os.path.join(folder, files[-1])


def load_flass():
    base = "data/Flass/"

    cl31_path = get_latest(base, "CL31-FL")
    cl32_path = get_latest(base, "CL32-FL")

    if not cl31_path:
        raise FileNotFoundError(f"CL31 not found in {base}")
    if not cl32_path:
        raise FileNotFoundError(f"CL32 not found in {base}")

    # ✅ Flass needs this (extra header row)
    cl31 = pd.read_excel(cl31_path, engine="openpyxl", skiprows=1)
    cl32 = pd.read_excel(cl32_path, engine="openpyxl", skiprows=1)

    # ✅ clean column names
    cl31.columns = cl31.columns.str.strip()
    cl32.columns = cl32.columns.str.strip()

    return cl31, cl32