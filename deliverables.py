import pandas as pd


def _to_date(series):
    return pd.to_datetime(series, errors="coerce", dayfirst=True)


def build_deliverables(cl31, cl32):

    cl31 = cl31.copy()
    cl32 = cl32.copy()

    # =========================
    # SAFETY CHECK
    # =========================
    if cl31.empty or cl32.empty:
        print("DEBUG: One of the dataframes is empty")
        return pd.DataFrame(columns=[
            "Deliverable",
            "CL31 Finish",
            "CL32 Finish",
            "Delta (Days)",
            "Change Type",
            "Status / Comment"
        ])

    # =========================
    # NORMALISE DELIVERABLES ✅ (CRITICAL FIX)
    # =========================
    cl31["Deliverable"] = (
        cl31["Activity Name"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    cl32["Deliverable"] = (
        cl32["Activity Name"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    # ✅ DO NOT OVER-FILTER (FIX FOR BLANK SCREEN)
    cl31 = cl31[cl31["Deliverable"].str.len() > 0]
    cl32 = cl32[cl32["Deliverable"].str.len() > 0]

    # Debug
    print("DEBUG: CL31 rows after clean:", len(cl31))
    print("DEBUG: CL32 rows after clean:", len(cl32))

    # =========================
    # DATE HANDLING
    # =========================
    cl31_finish_col = (
        "BL Project Finish" if "BL Project Finish" in cl31.columns else "Finish"
    )

    cl32_finish_col = (
        "Finish" if "Finish" in cl32.columns else None
    )

    cl31["CL31 Finish_raw"] = _to_date(cl31[cl31_finish_col])

    if cl32_finish_col:
        cl32["CL32 Finish_raw"] = _to_date(cl32[cl32_finish_col])
    else:
        cl32["CL32 Finish_raw"] = pd.NaT

    # =========================
    # ORDER MAP
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

    print("DEBUG: Rows after merge:", len(df))

    # ✅ CRITICAL: prevent blank result
    if df.empty:
        print("DEBUG: Merge returned empty dataframe")
        print("CL31 sample:", cl31.head())
        print("CL32 sample:", cl32.head())

        return pd.DataFrame(columns=[
            "Deliverable",
            "CL31 Finish",
            "CL32 Finish",
            "Delta (Days)",
            "Change Type",
            "Status / Comment"
        ])

    # =========================
    # SORT
    # =========================
    df["__order"] = df["Deliverable"].map(order_map)
    df = df.sort_values("__order", na_position="last").drop(columns="__order")

    # =========================
    # DELTA
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
    # COMMENTS
    # =========================
    comment_map = {
        "NEW": "Added scope in CL32",
        "REMOVED": "Removed from CL32",
        "DELAYED": "Shifted later, coordination required",
        "EARLY": "Pulled forward",
        "UNCHANGED": "Stable"
    }

    df["Status / Comment"] = df["Change Type"].map(comment_map)

    # =========================
    # FORMAT
    # =========================
    def fmt(x):
        return x.strftime("%d-%b-%y") if pd.notna(x) else "-"

    df["CL31 Finish"] = df["CL31 Finish_raw"].apply(fmt)
    df["CL32 Finish"] = df["CL32 Finish_raw"].apply(fmt)

    # ✅ Optional: make names readable again
    df["Deliverable"] = df["Deliverable"].str.title()

    return df[[
        "Deliverable",
        "CL31 Finish",
        "CL32 Finish",
        "Delta (Days)",
        "Change Type",
        "Status / Comment"
    ]]