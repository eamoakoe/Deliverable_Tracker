import pandas as pd
import streamlit as st


# =========================
# DATE PARSER
# =========================
def _to_date(series):
    return pd.to_datetime(series, errors="coerce", dayfirst=True)


# =========================
# BUILD DATA
# =========================
def build_deliverables(cl31, cl32):
    cl31 = cl31.copy()
    cl32 = cl32.copy()

    # =========================
    # NORMALISE
    # =========================
    cl31["Deliverable"] = cl31["Activity Name"].astype(str).str.strip()
    cl32["Deliverable"] = cl32["Activity Name"].astype(str).str.strip()

    # =========================
    # DATES
    # =========================
    cl31["CL31 Finish_raw"] = _to_date(cl31["BL Project Finish"])
    cl32["CL32 Finish_raw"] = _to_date(cl32["Finish"])

    # =========================
    # ORDER (FROM CL31)
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
    # FORMAT DATES
    # =========================
    def fmt(x):
        return x.strftime("%d-%b-%Y") if pd.notna(x) else "-"

    df["CL31 Finish"] = df["CL31 Finish_raw"].apply(fmt)
    df["CL32 Finish"] = df["CL32 Finish_raw"].apply(fmt)

    return df[[
        "Deliverable",
        "CL31 Finish",
        "CL32 Finish",
        "Delta (Days)",
        "Change Type",
        "Status / Comment"
    ]]


# =========================
# RENDER TABLE ✅
# =========================
def render_deliverables_table(cl31, cl32):
    df = build_deliverables(cl31, cl32)

    if df.empty:
        st.warning("⚠️ No deliverable comparison available")
        return

    # =========================
    # KPI SUMMARY ✅
    # =========================
    delayed = (df["Change Type"] == "DELAYED").sum()
    early = (df["Change Type"] == "EARLY").sum()
    new = (df["Change Type"] == "NEW").sum()
    removed = (df["Change Type"] == "REMOVED").sum()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🔴 Delayed", delayed)
    col2.metric("🟢 Early", early)
    col3.metric("🆕 New", new)
    col4.metric("❌ Removed", removed)

    # =========================
    # SORT (impact first)
    # =========================
    df = df.sort_values("Delta (Days)", ascending=False)

    # =========================
    # COLOUR RULES ✅
    # =========================
    def colour_delta(val):
        if pd.isna(val):
            return "background-color:#374151;color:white"
        if val > 0:
            return "background-color:#7f1d1d;color:white;font-weight:bold"
        elif val < 0:
            return "background-color:#14532d;color:white;font-weight:bold"
        return "background-color:#374151;color:white"

    def colour_change(val):
        if val == "DELAYED":
            return "background-color:#b00020;color:white"
        elif val == "EARLY":
            return "background-color:#1e7e34;color:white"
        elif val == "NEW":
            return "background-color:#2563eb;color:white"
        elif val == "REMOVED":
            return "background-color:#6b7280;color:white"
        return ""

    # =========================
    # STYLE (MATCH DASHBOARD ✅)
    # =========================
    styled = (
        df.style
        .set_table_styles([
            {
                "selector": "th",
                "props": [
                    ("background-color", "#2b3a55"),
                    ("color", "white"),
                    ("font-weight", "600"),
                    ("padding", "10px"),
                    ("text-transform", "uppercase")
                ]
            },
            {
                "selector": "td",
                "props": [
                    ("background-color", "#1c2233"),
                    ("color", "#f1f1f1"),
                    ("padding", "8px")
                ]
            }
        ])
        .map(colour_delta, subset=["Delta (Days)"])
        .map(colour_change, subset=["Change Type"])
    )

    st.markdown(styled.to_html(), unsafe_allow_html=True)