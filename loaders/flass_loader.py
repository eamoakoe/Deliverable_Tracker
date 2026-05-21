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


def clean_columns(df):
    df.columns = (
        df.columns
        .str.strip()
        .str.replace("\xa0", " ", regex=False)
    )
    return df


def load_flass():
    base = "data/Flass/"

    cl31_path = get_latest(base, "CL31-FL")
    cl32_path = get_latest(base, "CL32-FL")

    if not cl31_path:
        raise FileNotFoundError(f"CL31 not found in {base}")
    if not cl32_path:
        raise FileNotFoundError(f"CL32 not found in {base}")

    # ✅ Skip title row
    cl31 = pd.read_excel(cl31_path, engine="openpyxl", skiprows=1)
    cl32 = pd.read_excel(cl32_path, engine="openpyxl", skiprows=1)

    # ✅ Clean headers
    cl31 = clean_columns(cl31)
    cl32 = clean_columns(cl32)

    # ✅ FORCE column names to match deliverables.py
    cl31 = cl31.rename(columns={
        "BL1 Finish": "BL Project Finish"   # critical fix
    })

    # ✅ Ensure Activity Name is exactly correct
    if "Activity Name" not in cl31.columns:
        for col in cl31.columns:
            if "activity" in col.lower() and "name" in col.lower():
                cl31 = cl31.rename(columns={col: "Activity Name"})

    if "Activity Name" not in cl32.columns:
        for col in cl32.columns:
            if "activity" in col.lower() and "name" in col.lower():
                cl32 = cl32.rename(columns={col: "Activity Name"})

    return cl31, cl32