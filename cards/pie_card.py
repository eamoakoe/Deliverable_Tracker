import streamlit as st
import plotly.graph_objects as go
import pandas as pd


# =========================
# LOAD CL32 (FIXED FILE PATH)
# =========================
def load_data():
    file_path = "data/Ferry/CL32-May.xlsx"
    return pd.read_excel(file_path, engine="openpyxl")


# =========================
# RENDER PIE
# =========================
def render_pie(df):

    df = df.copy()

    # Clean column names
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
    )

    # Convert Finish date
    df["Finish"] = pd.to_datetime(df.get("Finish"), errors="coerce")

    # ✅ CRITICAL FIX (handles hidden Excel % characters)
    df["Activity % Complete"] = (
        df["Activity % Complete"]
        .astype(str)
        .str.replace(r"[^0-9.]", "", regex=True)
    )

    df["Activity % Complete"] = pd.to_numeric(
        df["Activity % Complete"],
        errors="coerce"
    ).fillna(0)

    today = pd.Timestamp.today()

    # =========================
    # STATUS LOGIC
    # =========================
    df["Status"] = "On Track"

    df.loc[
        (df["Finish"] < today) &
        (df["Activity % Complete"] < 100),
        "Status"
    ] = "Delayed"

    df.loc[
        df["Activity % Complete"] >= 100,
        "Status"
    ] = "Completed"

    # =========================
    # SUMMARY
    # =========================
    order = ["On Track", "Delayed", "Completed"]

    summary = df["Status"].value_counts().reindex(order, fill_value=0)

    colors = {
        "On Track": "#FFD700",
        "Delayed": "#FF3B30",
        "Completed": "#00C853"
    }

    # =========================
    # PIE CHART
    # =========================
    fig = go.Figure(
        data=[go.Pie(
            labels=summary.index,
            values=summary.values,
            sort=False,
            texttemplate="%{value}<br>(%{percent})",
            marker=dict(colors=[colors[k] for k in summary.index])
        )]
    )

    fig.update_layout(
        height=360,
        margin=dict(l=5, r=5, t=5, b=5),
        showlegend=False
    )

    # ✅ FIX: unique key + new width param
    st.plotly_chart(
        fig,
        width="stretch",
        key="cl32_status_pie"
    )


# =========================
# MAIN APP
# =========================
st.title("Ferry Tracker (CL32 Only)")

df = load_data()

render_pie(df)