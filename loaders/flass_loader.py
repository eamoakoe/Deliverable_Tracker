import pandas as pd
import os


def get_latest(folder, prefix):
    files = [
        f for f in os.listdir(folder)
        if f.startswith(prefix)
        and f.endswith(".xlsx")
        and not f.startswith("~$")
    ]

    if not files:
        return None

    files.sort()
    return os.path.join(folder, files[-1])


def load_flass():
    # 🔥 Get absolute path of this file (loaders/)
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # 🔥 Move up to project root, then into data/Flass
    base = os.path.join(BASE_DIR, "..", "data", "Flass")
    base = os.path.normpath(base)

    # ✅ Debug (remove later)
    print("Looking in:", base)
    if os.path.exists(base):
        print("Files:", os.listdir(base))
    else:
        print("Folder NOT FOUND")

    cl31_path = get_latest(base, "CL31-FL")
    cl32_path = get_latest(base, "CL32-FL")

    if not cl31_path:
        raise FileNotFoundError(f"CL31 file not found in {base}")
    if not cl32_path:
        raise FileNotFoundError(f"CL32 file not found in {base}")

    cl31 = pd.read_excel(cl31_path, engine="openpyxl", skiprows=1)
    cl32 = pd.read_excel(cl32_path, engine="openpyxl", skiprows=1)

    return cl31, cl32