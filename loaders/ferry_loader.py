import pandas as pd
import os


# =========================
# GET LATEST FILE (for CL31 only)
# =========================
def get_latest(folder, prefix):
    files = [
        f for f in os.listdir(folder)
        if f.startswith(prefix) and f.endswith(".xlsx")
    ]
    files.sort()
    return os.path.join(folder, files[-1]) if files else None


# =========================
# GET ALL FILES (for CL32)
# =========================
def get_all(folder, prefix):
    files = [
        f for f in os.listdir(folder)
        if f.startswith(prefix) and f.endswith(".xlsx")
    ]
    files.sort()
    return [os.path.join(folder, f) for f in files]


# =========================
# MAIN LOADER
# =========================
def load_ferry():

    base = "data/Ferry/"

    # ✅ CL31 (latest only – unchanged)
    cl31_path = get_latest(base, "CL31")
    cl31 = (
        pd.read_excel(cl31_path, engine="openpyxl")
        if cl31_path else pd.DataFrame()
    )

    # ✅ CL32 (ALL files for baseline vs forecast)
    cl32_files = get_all(base, "CL32")

    cl32_list = []

    for file_path in cl32_files:

        df = pd.read_excel(file_path, engine="openpyxl")

        file_name = os.path.basename(file_path).replace(".xlsx", "")

        # ✅ Store snapshot name
        df["Snapshot"] = file_name

        # ✅ Convert "CL32-June-2026" → "01-June-2026"
        # ✅ IMPORTANT: %B (full month name)
        df["SnapshotDate"] = pd.to_datetime(
            file_name.replace("CL32-", "01-"),
            format="%d-%B-%Y",
            errors="coerce"
        )

        cl32_list.append(df)

    # ✅ Combine all CL32 files
    if cl32_list:
        cl32 = pd.concat(cl32_list, ignore_index=True)

        # ✅ Remove invalid dates
        cl32 = cl32.dropna(subset=["SnapshotDate"])

        # ✅ Ensure correct ordering
        cl32 = cl32.sort_values("SnapshotDate")

    else:
        cl32 = pd.DataFrame()

    return cl31, cl32
