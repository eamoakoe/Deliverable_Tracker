import pandas as pd


def _to_date(series):
    return pd.to_datetime(series, errors="coerce", dayfirst=True)


def build_deliverables(cl31, cl32):

    cl31 = cl31.copy()
    cl32 = cl32.copy()

    # =========================
    # NORMALISE COLUMNS
    # =========================
    cl31["Deliverable"] = cl31["Activity Name"].astype(str).str.strip()
    cl32["Deliverable"] = cl32["Activity Name"].astype(str).str.strip()

    # =========================
    # DATE PARSING (CRITICAL FIX)
    # =========================
    cl31["CL31 Finish_raw"] = _to_date(cl31["BL Project Finish"])
    cl32["CL32 Finish_raw"] = _to_date(cl32["Finish"])

    # =========================
    # KEEP ORDER FROM CL31
    # =========================
    order_map = {v: i for i, v in enumerate(cl31["Deliverable"].tolist())}

    # =========================
    # MERGE
    # =========================
    df = cl31[["Deliverable", "CL31 Finish_raw"]].merge(
        cl32[["Deliverable", "CL32 Finish_raw"]],
        on="Deliverable",
        how="outer"
    )

    df["__order"] = df["Deliverable"].map(order_map)
    df = df.sort_values("__order", na_position="last").drop(columns="__order")

    # =========================
    # DELTA (INTEGER FIX)
    # =========================
    def calc_delta(row):
        if pd.isna(row["CL31 Finish_raw"]) or pd.isna(row["CL32 Finish_raw"]):
            return None
        return int((row["CL32 Finish_raw"] - row["CL31 Finish_raw"]).days)

    df["Delta (Days)"] = df.apply(calc_delta, axis=1)

    # =========================
    # CHANGE TYPE
    # =========================
    def change_type(row):
        if pd.isna(row["CL31 Finish_raw"]) and pd.notna(row["CL32 Finish_raw"]):
            return "NEW"
        if pd.notna(row["CL31 Finish_raw"]) and pd.isna(row["CL32 Finish_raw"]):
            return "REMOVED"
        if row["Delta (Days)"] is None:
            return "UNCHANGED"
        if row["Delta (Days)"] > 0:
            return "DELAYED"
        if row["Delta (Days)"] < 0:
            return "EARLY"
        return "UNCHANGED"

    df["Change Type"] = df.apply(change_type, axis=1)

    # =========================
    # COMMENT
    # =========================
    def comment(row):
        return {
            "NEW": "Added scope in CL32",
            "REMOVED": "Removed from CL32",
            "DELAYED": "Shifted later, coordination required",
            "EARLY": "Pulled forward",
            "UNCHANGED": "Stable"
        }.get(row["Change Type"], "Stable")

    df["Status / Comment"] = df.apply(comment, axis=1)

    # =========================
    # FORMAT FOR DISPLAY ONLY
    # =========================
    def fmt(x):
        if pd.isna(x):
            return "-"
        return x.strftime("%d-%b-%y")

    df["CL31 Finish"] = df["CL31 Finish_raw"].apply(fmt)
    df["CL32 Finish"] = df["CL32 Finish_raw"].apply(fmt)

    # FINAL CLEANUP
    return df[[
        "Deliverable",
        "CL31 Finish",
        "CL32 Finish",
        "Delta (Days)",
        "Change Type",
        "Status / Comment"
    ]]