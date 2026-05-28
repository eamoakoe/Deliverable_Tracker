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

    # ✅ Normalise names
    cl31["Deliverable"] = cl31["Activity Name"].astype(str).str.strip()
    cl32["Deliverable"] = cl32["Activity Name"].astype(str).str.strip()

    # ✅ Parse dates
    cl31["CL31 Finish_raw"] = _to_date(cl31["BL Project Finish"])
    cl32["CL32 Finish_raw"] = _to_date(cl32["Finish"])

    # ✅ Preserve CL31 order
    order_map = {v: i for i, v in enumerate(cl31["Deliverable"].tolist())}

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

    df["Δ Change vs CL32 May (days)"] = df.apply(calc_delta, axis=1)

    # =========================
    # CHANGE TYPE
    # =========================
    def change_type(row):
        if pd.isna(row["CL31 Finish_raw"]) and pd.notna(row["CL32 Finish_raw"]):
            return "NEW"
        if pd.notna(row["CL31 Finish_raw"]) and pd.isna(row["CL32 Finish_raw"]):
            return "REMOVED"
        if row["Δ Change vs CL32 May (days)"] is None:
            return "UNCHANGED"
        if row["Δ Change vs CL32 May (days)"] > 0:
            return "DELAYED"
        if row["Δ Change vs CL32 May (days)"] < 0:
            return "EARLY"
        return "UNCHANGED"

    df["Change Type"] = df.apply(change_type, axis=1)

    # =========================
    # STATUS (FOR COLOURING)
    # =========================
    def status(row):
        if row["Change Type"] == "DELAYED":
            return "🔴 Issue"
        elif row["Change Type"] == "EARLY":
            return "🟢 Improved"
        elif row["Change Type"] == "NEW":
            return "🔵 New"
        elif row["Change Type"] == "REMOVED":
            return "⚫ Removed"
        return "🟢 Stable"

    df["Status (CL32 May)"] = df.apply(status, axis=1)

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
        "Δ Change vs CL32 May (days)",
        "Change Type",
        "Status (CL32 May)",
        "Status / Comment"
    ]]


# =========================
# ✅ RENDER TABLE (FINAL FIX)
# =========================
def render_deliverables_table(cl31, cl32):

    df = build_deliverables(cl31, cl32)

    if df.empty:
        st.warning("⚠️ No deliverable comparison available")
        return

    # =========================
    # KPI SUMMARY
    # =========================
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🔴 Delayed", (df["Change Type"] == "DELAYED").sum())
    col2.metric("🟢 Early", (df["Change Type"] == "EARLY").sum())
    col3.metric("🔵 New", (df["Change Type"] == "NEW").sum())
    col4.metric("⚫ Removed", (df["Change Type"] == "REMOVED").sum())

    # ✅ Sort by worst first
    df = df.sort_values("Δ Change vs CL32 May (days)", ascending=False)

    # =========================
    # COLOUR RULES
    # =========================
    def colour_delta(val):
        if pd.isna(val):
            return ""
        if val > 0:
            return "background-color:#7f1d1d;color:white;font-weight:bold"
        elif val < 0:
            return "background-color:#14532d;color:white;font-weight:bold"
        return "background-color:#374151;color:white"

    def colour_status(val):
        if "🔴" in val:
            return "background-color:#b00020;color:white"
        elif "🟢" in val:
            return "background-color:#1e7e34;color:white"
        elif "🔵" in val:
            return "background-color:#2563eb;color:white"
        elif "⚫" in val:
            return "background-color:#6b7280;color:white"
        return ""

    styled = (
        df.style
        .map(colour_delta, subset=["Δ Change vs CL32 May (days)"])
        .map(colour_status, subset=["Status (CL32 May)"])
    )

    # =========================
    # ✅ FORCE DARK THEME (KEY FIX)
    # =========================
    html = f"""
    <style>
    table {{
        width: 100%;
        border-collapse: collapse;
        background-color: #1c2233;
        color: #f1f1f1;
    }}
    th {{
        background-color: #2b3a55 !important;
        color: white !important;
        font-weight: 600;
        padding: 10px;
        text-align: left;
    }}
    td {{
        background-color: #1c2233;
        padding: 8px;
    }}
    </style>

    {styled.to_html(index=False)}
    """

    st.markdown(html, unsafe_allow_html=True)