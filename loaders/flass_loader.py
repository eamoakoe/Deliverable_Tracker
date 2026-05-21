import pandas as pd
import os


def get_latest(folder, prefix):
    files = [
        f for f inxlsx")        f for f in os.listdir(folder)
    ]

    if not files:
        return None

    files.sort()
    return os.path.join(folder, files[-1])


def clean_columns(df):
    df.columns = (
        df.columns
        .astype(str)                  # ✅ ensures no float column names
        .str.strip()                  # ✅ remove spaces
        .str.replace("\xa0", " ", regex=False)  # ✅ remove hidden Excel chars
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

    # ✅ Skip extra header row in Flass files
    cl31 = pd.read_excel(cl31_path, engine="openpyxl", skiprows=1)
    cl32 = pd.read_excel(cl32_path, engine="openpyxl", skiprows=1)

    # ✅ Clean column names
    cl31 = clean_columns(cl31)
    cl32 = clean_columns(cl32)

    # ✅ Rename columns to match deliverables.py expectations
    # CL31 uses BL1 Finish but your logic expects BL Project Finish
    if "BL1 Finish" in cl31.columns:
        cl31 = cl31.rename(columns={"BL1 Finish": "BL Project Finish"})

    # ✅ Ensure Activity Name exists EXACTLY
    def fix_activity_name(df):
        if "Activity Name" not in df.columns:
            for col in df.columns:
                col_str = str(col).lower()
                if "activity" in col_str and "name" in col_str:
                    df = df.rename(columns={col: "Activity Name"})
        return df

    cl31 = fix_activity_name(cl31)
    cl32 = fix_activity_name(cl32)

    return cl31, cl32
