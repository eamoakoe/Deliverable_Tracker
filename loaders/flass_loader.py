import pandas as pd
import os


def get_latest(folder, prefix):
    files = [f for f in os.listdir(folder) if f.startswith(prefix) and f.endswith(".xlsx")]
    files.sort()
    return os.path.join(folder, files[-1]) if files else None


def load_flass():
    base = "data/Flass/"

    cl31 = pd.read_excel(get_latest(base, "CL31-FL"), engine="openpyxl")
    cl32 = pd.read_excel(get_latest(base, "CL32-FL"), engine="openpyxl")

    return cl31, cl32