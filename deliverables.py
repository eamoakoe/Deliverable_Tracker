import pandas as pd


def _to_date(series):
    return pd.to_datetime(series, errors="coerce", or cl32.empty:    return pd.to_datetime(series, errors="coerce", dayfirst=True)
        return pd.DataFrame()

    c31 = cl31.copy()
    c32 = cl32.copy()

    c31["Deliverable"] = c31["Activity Name"].astype(str).str.strip().str.lower()
    c32["Deliverable"] = c32["Activity Name"].astype(str).str.strip().str.lower()

    c31["Finish31"] = _to_date(c31["Finish"])
    c32["Finish32"] = _to_date(c32["Finish"])

    df = c31[["Deliverable", "Finish31"]].merge(
        c32[["Deliverable", "Finish32"]],
        on="Deliverable",
        how="outer"
    )

    def delta(r):
        if pd.isna(r["Finish31"]) or pd.isna(r["Finish32"]):
            return None
        return (r["Finish32"] - r["Finish31"]).days

    df["Delta (Days)"] = df.apply(delta, axis=1)

    df["Deliverable"] = df["Deliverable"].str.title()

    return df


def build_deliverables(cl31, cl32):

