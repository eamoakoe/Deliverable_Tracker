import pandas as pd
import streamlit as st


# =========================
# DATE PARSER
# =========================
def _to_date(series):
    return pd.to_datetime(series, errors="coerce", dayfirst=True)


# =========================
# BUILD DATA (UNCHANGED ✅)
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

    df["Delta (Days)"] = df.apply(calc_delta, axis=1)

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

    comment_map = {
        "NEW": "Added scope in CL32",
        "REMOVED": "Removed from CL32",
        "DELAYED": "Shifted later, coordination required",
        "EARLY": "Pulled forward",
        "UNCHANGED": "Stable"
    }

    df["Status / Comment"] = df["Change Type"].map(comment_map)

    def fmt(x):
        return x.strftime("%d-%b-%y") if pd.notna(x) else "-"

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
# ✅ RENDER (PURE HTML DARK TABLE ✅)
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
    col3.metric("🆕 New", (df["Change Type"] == "NEW").sum())
    col4.metric("❌ Removed", (df["Change Type"] == "REMOVED").sum())

    df = df.sort_values("Delta (Days)", ascending=False)

    # =========================
    # BUILD HTML TABLE ✅
    # =========================
    rows = ""

    for _, r in df.iterrows():

        # Delta styling
        delta = r["Delta (Days)"]
        if pd.isna(delta):
            delta_display = "-"
            delta_style = ""
        elif delta > 0:
            delta_display = delta
            delta_style = "background:#7f1d1d;color:white;font-weight:bold;"
        elif delta < 0:
            delta_display = delta
            delta_style = "background:#14532d;color:white;font-weight:bold;"
        else:
            delta_display = delta
            delta_style = "background:#374151;color:white;"

        # Change type styling
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
            <td style="{delta_style}">{delta_display}</td>
            <td style="{ct_style}">{ct}</td>
            <td>{r["Status / Comment"]}</td>
        </tr>
        """

    html = f"""
    <div style="max-height:500px; overflow-y:auto; border:1px solid #2b3a55;">
        <table style="width:100%; border-collapse:collapse; font-family:sans-serif;">
            <thead>
                <tr style="background:#2b3a55;color:white;">
                    <th style="padding:10px;">Deliverable</th>
                    <th style="padding:10px;">CL31 Finish</th>
                    <th style="padding:10px;">CL32 Finish</th>
                    <th style="padding:10px;">Δ Days</th>
                    <th style="padding:10px;">Change Type</th>
                    <th style="padding:10px;">Status / Comment</th>
                </tr>
            </thead>
            <tbody style="background:#1c2233;color:#f1f1f1;">
                {rows}
            </tbody>
        </table>
    </div>
    """

    st.markdown(html, unsafe_allow_html=True)
