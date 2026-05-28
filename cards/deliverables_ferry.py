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

    cl31["Deliverable"] = cl31["Activity Name"].astype(str).str.strip()
    cl32["Deliverable"] = cl32["Activity Name"].astype(str).str.strip()

    cl31["CL31 Finish_raw"] = _to_date(cl31["BL Project Finish"])
    cl32["CL32 Finish_raw"] = _to_date(cl32["Finish"])

    order_map = {v: i for i, v in enumerate(cl31["Deliverable"].tolist())}

    df = cl31[["Deliverable", "CL31 Finish_raw"]].merge(
        cl32[["Deliverable", "CL32 Finish_raw"]],
        on="Deliverable",
        how="outer"
    )

    df["__order"] = df["Deliverable"].map(order_map)
    df = df.sort_values("__order", na_position="last").drop(columns="__order")

    def calc_delta(row):
        if pd.isna(row["CL31 Finish_raw"]) or pd.isna(row["CL32 Finish_raw"]):
            return None
        return int((row["CL32 Finish_raw"] - row["CL31 Finish_raw"]).days)

    df["Delta"] = df.apply(calc_delta, axis=1)

    def change_type(row):
        if pd.isna(row["CL31 Finish_raw"]) and pd.notna(row["CL32 Finish_raw"]):
            return "NEW"
        if pd.notna(row["CL31 Finish_raw"]) and pd.isna(row["CL32 Finish_raw"]):
            return "REMOVED"
        if row["Delta"] is None:
            return "UNCHANGED"
        if row["Delta"] > 0:
            return "DELAYED"
        if row["Delta"] < 0:
            return "EARLY"
        return "UNCHANGED"

    df["Change Type"] = df.apply(change_type, axis=1)

    def fmt(x):
        return x.strftime("%d-%b-%Y") if pd.notna(x) else "-"

    df["CL31 Finish"] = df["CL31 Finish_raw"].apply(fmt)
    df["CL32 Finish"] = df["CL32 Finish_raw"].apply(fmt)

    return df[[
        "Deliverable",
        "CL31 Finish",
        "CL32 Finish",
        "Delta",
        "Change Type",
    ]]


# =========================
# ✅ RENDER (FORCED DARK HTML)
# =========================
def render_deliverables_table(cl31, cl32):

    df = build_deliverables(cl31, cl32)

    if df.empty:
        st.warning("⚠️ No deliverable comparison available")
        return

    # KPI
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🔴 Delayed", (df["Change Type"] == "DELAYED").sum())
    col2.metric("🟢 Early", (df["Change Type"] == "EARLY").sum())
    col3.metric("🔵 New", (df["Change Type"] == "NEW").sum())
    col4.metric("⚫ Removed", (df["Change Type"] == "REMOVED").sum())

    df = df.sort_values("Delta", ascending=False)

    # =========================
    # BUILD DARK HTML TABLE ✅
    # =========================
    rows = ""

    for _, r in df.iterrows():

        # Delta colour
        if pd.isna(r["Delta"]):
            delta_style = ""
            delta_val = "-"
        else:
            delta_val = str(r["Delta"])
            if r["Delta"] > 0:
                delta_style = "background:#7f1d1d;color:white;font-weight:bold;"
            elif r["Delta"] < 0:
                delta_style = "background:#14532d;color:white;font-weight:bold;"
            else:
                delta_style = "background:#374151;color:white;"

        # Change type colour
        ct = r["Change Type"]
        if ct == "DELAYED":
            ct_style = "background:#b00020;color:white;"
        elif ct == "EARLY":
            ct_style = "background:#1e7e34;color:white;"
        elif ct == "NEW":
            ct_style = "background:#2563eb;color:white;"
        elif ct == "REMOVED":
            ct_style = "background:#6b7280;color:white;"
        else:
            ct_style = ""

        rows += f"""
        <tr>
            <td>{r["Deliverable"]}</td>
            <td>{r["CL31 Finish"]}</td>
            <td>{r["CL32 Finish"]}</td>
            <td style="{delta_style}">{delta_val}</td>
            <td style="{ct_style}">{ct}</td>
        </tr>
        """

    html = f"""
    <table style="width:100%; border-collapse:collapse; font-family:sans-serif;">
        <thead>
            <tr style="background:#2b3a55;color:white;">
                <th style="padding:10px;text-align:left;">Deliverable</th>
                <th style="padding:10px;text-align:left;">CL31 Finish</th>
                <th style="padding:10px;text-align:left;">CL32 Finish</th>
                <th style="padding:10px;text-align:left;">Δ Days</th>
                <th style="padding:10px;text-align:left;">Change Type</th>
            </tr>
        </thead>
        <tbody style="background:#1c2233;color:#f1f1f1;">
            {rows}
        </tbody>
    </table>
    """

    st.markdown(html, unsafe_allow_html=True)
