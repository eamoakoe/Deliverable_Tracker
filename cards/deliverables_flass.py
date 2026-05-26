import pandas as pd


def _to_date(series):
    return pd.to_datetime(series, errors="coerce", dayfirst=True)


def build_deliverables(cl31, cl32):

    cl31 = cl31.copy()
    cl32 = cl32.copy()

    # =========================
    # ✅ STANDARDISE KEYS
    # =========================
    cl31["Activity ID"] = cl31["Activity ID"].astype(str).str.strip()
    cl32["Activity ID"] = cl32["Activity ID"].astype(str).str.strip()

    cl31["Deliverable"] = cl31["Activity Name"].astype(str).str.strip()
    cl32["Deliverable"] = cl32["Activity Name"].astype(str).str.strip()

    # =========================
    # ✅ DATE PARSING
    # =========================
    cl31["CL31 Finish_raw"] = _to_date(cl31["BL Project Finish"])
    cl32["CL32 Finish_raw"] = _to_date(cl32["Finish"])

    # =========================
    # ✅ KEEP ONLY TRUE DELIVERABLES (YOUR LOGIC)
    # =========================
    deliverable_ids = ["-KD-", "-DRIA-", "-DDST-", "-DDGD-"]

    cl31 = cl31[cl31["Activity ID"].str.contains("|".join(deliverable_ids), na=False)]
    cl32 = cl32[cl32["Activity ID"].str.contains("|".join(deliverable_ids), na=False)]

    # =========================
    # ✅ ORDER FROM CL31
    # =========================
    order_map = {v: i for i, v in enumerate(cl31["Activity ID"].tolist())}

    # =========================
    # ✅ MERGE ON ACTIVITY ID (FIXED ✅)
    # =========================
    df = cl31[["Activity ID", "Deliverable", "CL31 Finish_raw"]].merge(
        cl32[["Activity ID", "CL32 Finish_raw"]],
        on="Activity ID",
        how="outer"
    )

    # ✅ Restore name if missing from one side
    name_map = pd.concat([
        cl31[["Activity ID", "Deliverable"]],
        cl32[["Activity ID", "Deliverable"]]
    ]).drop_duplicates().set_index("Activity ID")["Deliverable"]

    df["Deliverable"] = df["Activity ID"].map(name_map)

    # ✅ KEEP ORDER
    df["__order"] = df["Activity ID"].map(order_map)
    df = df.sort_values("__order", na_position="last").drop(columns="__order")

    # =========================
    # ✅ DELTA
    # =========================
    def calc_delta(row):
        if pd.isna(row["CL31 Finish_raw"]) or pd.isna(row["CL32 Finish_raw"]):
            return None
        return int((row["CL32 Finish_raw"] - row["CL31 Finish_raw"]).days)

    df["Delta (Days)"] = df.apply(calc_delta, axis=1)

    # =========================
    # ✅ CHANGE TYPE (IMPROVED ✅)
    # =========================
    def change_type(row):

        if pd.isna(row["CL31 Finish_raw"]) and pd.notna(row["CL32 Finish_raw"]):
            return "NEW"

        if pd.notna(row["CL31 Finish_raw"]) and pd.isna(row["CL32 Finish_raw"]):
            return "REMOVED"

        if row["Delta (Days)"] is None:
            return "UNKNOWN"

        if row["Delta (Days)"] > 0:
            return "DELAYED"

        if row["Delta (Days)"] < 0:
            return "EARLY"

        return "UNCHANGED"

    df["Change Type"] = df.apply(change_type, axis=1)

    # =========================
    # ✅ COMMENTS
    # =========================
    comment_map = {
        "NEW": "Added in CL32",
        "REMOVED": "Removed from CL32",
        "DELAYED": "Moved later vs CL31",
        "EARLY": "Pulled forward",
        "UNCHANGED": "No change",
        "UNKNOWN": "Insufficient data"
    }

    df["Status / Comment"] = df["Change Type"].map(comment_map)

    # =========================
    # ✅ FORMAT DATES
    # =========================
    def fmt(x):
        return x.strftime("%d-%b-%y") if pd.notna(x) else "-"

    df["CL31 Finish"] = df["CL31 Finish_raw"].apply(fmt)
    df["CL32 Finish"] = df["CL32 Finish_raw"].apply(fmt)

    # =========================
    # ✅ FINAL OUTPUT
    # =========================
    return df[[
        "Deliverable",
        "CL31 Finish",
        "CL32 Finish",
        "Delta (Days)",
        "Change Type",
        "Status / Comment"
    ]]