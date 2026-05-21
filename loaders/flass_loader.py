import pandas as pdimportimport os


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


def clean_columns(df):
    df.columns = (
        df.columns
        .str.strip()
        .str.replace("\xa0", " ", regex=False)  # remove hidden Excel spaces
    )
    return df


def load_flass():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # move from /loaders → root → data/Flass
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

    # ✅ Skip top title row (Flass-specific issue)
    cl31 = pd.read_excel(cl31_path, engine="openpyxl", skiprows=1)
    cl32 = pd.read_excel(cl32_path, engine="openpyxl", skiprows=1)

    # ✅ Clean headers
    cl31 = clean_columns(cl31)
    cl32 = clean_columns(cl32)

    return cl31, cl32

