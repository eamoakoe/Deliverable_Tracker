import pandas as pd


# ================= to_date(series):# =========================
    return pd.to_datetime(series, errors="coerce", dayfirst=True)


# =========================
# MAIN FUNCTION
# =========================
def build_deliverables(cl31, cl32):

    # ✅ Safety
    if cl31 is None or cl32 is None:
        return pd.DataFrame()

    if cl31.empty or cl32.empty:
        return pd.DataFrame()

    # ✅ Copy data
    df31 = cl31.copy()
    df32 = cl32.copy()

    # ✅ Normalise names
    if "Activity Name" not in df31.columns or "Activity Name" not in df32.columns:
        return pd.DataFrame()

    df31["Deliverable"] = df31["Activity Name"].astype(str).str.strip().str.lower()
    df32["Deliverable"] = df32["Activity Name"].astype(str).str.strip().str.lower()

    # ✅ Dates
    if "Finish" in df31.columns:
        df31["Finish31"] = to_date(df31["Finish"])
    else:
        df31["Finish31"] = pd.NaT

    if "Finish" in df32.columns:
        df32["Finish32"] = to_date(df32["Finish"])
    else:
        df32["Finish32"] = pd.NaT

    # ✅ Merge
    df = df31[["Deliverable", "Finish31"]].merge(
        df32[["Deliverable", "Finish32"]],
        on="Deliverable",
        how="outer"
    )

    # ✅ Delta
    def calc_delta(row):
        if pd.isna(row["Finish31"]) or pd.isna(row["Finish32"]):
            return None
        return (row["Finish32"] - row["Finish31"]).days

    df["Delta (Days)"] = df.apply(calc_delta, axis=1)

    # ✅ Clean output
    df["Deliverable"] = df["Deliverable"].str.title()

    return df[["Deliverable", "Finish31", "Finish32", "Delta (Days)"]]
# DATE CONVERSION
# =========================
