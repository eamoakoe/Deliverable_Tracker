import pandas as pd
import os


def get_latest(folder, prefix):
    files = [f for f in os.listdir(folder) if f.startswith(prefix) and f.endswith(".xlsx")]
    files.sort()
    return os.path.join(folder, files[-1]) if files else None


# ✅ NEW: load ALL CL32 files
def get_all(folder, prefix):
    files = [f for f in os.listdir(folder) if f.startswith(prefix) and f.endswith(".xlsx")]
    files.sort()
    return [os.path.join(folder, f) for f in files]


def load_ferry():

    base = "data/Ferry/"

    # ✅ Keep CL31 as latest only (unchanged)
    cl31_path = get_latest(base, "CL31")
    cl31 = pd.read_excel(cl31_path, engine="openpyxl") if cl31_path else pd.DataFrame()

    # ✅ Load ALL CL32 files
    cl32_files = get_all(base, "CL32")

    cl32_list = []

    for file_path in cl32_files:

        df = pd.read_excel(file_path, engine="openpyxl")

        file_name = os.path.basename(file_path).replace(".xlsx", "")

        # ✅ Add snapshot name
        df["Snapshot"] = file_name

        # ✅ Extract date from filename (CL32-May-2026)
        try:
            parts = file_name.split("-")[1:]  # ['May', '2026']
            df["SnapshotDate"] = pd.to_datetime(
                "01-" + "-".join(parts),
                format="%d-%b-%Y"
            )
        except:
            df["SnapshotDate"] = pd.NaT

        cl32_list.append(df)

    # ✅ Combine all months
    if cl32_list:
        cl32 = pd.concat(cl32_list, ignore_index=True)
        cl32 = cl32.dropna(subset=["SnapshotDate"])
        cl32 = cl32.sort_values("SnapshotDate")
    else:
        cl32 = pd.DataFrame()

    return cl31, cl32