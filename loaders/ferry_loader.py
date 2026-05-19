import pandas as pd
import os


def get_latest(folder, prefix):
    files = [f for f in os.listdir(folder) if f.startswith(prefix) and f.endswith(".xlsx")]
    files.sort()
    return os.path.join(folder, files[-1]) if files else None


def load_ferry():
    base = "data/Ferry/"

    cl31 = pd.read_excel(get_latest(base, "CL31"), engine="openpyxl")
    cl32 = pd.read_excel(get_latest(base, "CL32"), engine="openpyxl")

    return cl31, cl32
