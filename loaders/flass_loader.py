import pandas as pd
import os


def get_latest(folder, prefix):
    files = [
        f for f in os.listdir(folder)
        if f.startswith(prefix)
        and f.lower().endswith(".xlsx")
        and not f.startswith("~$")
    ]

    if not files:
        return None

    files.sort()
    return os.path.join(folder, files[-1])


def load_flass():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    base = os.path.join(BASE_DIR, "..", "data", "Flass")
    base = os.path.normpath(base)

    if not os.path.exists(base):
        raise FileNotFoundError(f"Folder not found: {base}")

    cl31_path = get_latest(base, "CL31-FL")
    cl32_path = get_latest(base, "CL32-FL")

    if not cl31_path:
        raise FileNotFoundError(f"CL31 not found in {base}")
    if not cl32_path:
        raise FileNotFoundError(f"CL32 not found in {base}")

    # ✅ skip first row (Flass files have title row)
    cl31 = pd.read_excel(cl31_path, engine="openpyxl", skiprows=1)
    cl32 = pd.read_excel(cl32_path, engine="openpyxl", skiprows=1)

    # ✅ clean column names
    cl31.columns = cl31.columns.str.strip()
    cl32.columns = cl32.columns.str.strip()

    return cl31, cl32
