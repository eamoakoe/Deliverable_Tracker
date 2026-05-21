import pandas as pd
import os


def get_latest(folder, prefix):
 in os.listdir(folder)    files = [
        if f.startswith(prefix) and f.endswith(".xlsx")
    ]
    files.sort()
    return os.path.join(folder, files[-1]) if files else None


def load_flass():
    base = "data/Flass/"

    cl31 = pd.read_excel(get_latest(base, "CL31-FL"), engine="openpyxl", skiprows=1)
    cl32 = pd.read_excel(get_latest(base, "CL32-FL"), engine="openpyxl", skiprows=1)

    # ✅ critical fix
    cl31.columns = cl31.columns.str.strip()
    cl32.columns = cl32.columns.str.strip()

    return cl31, cl32
