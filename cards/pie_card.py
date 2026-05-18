import streamlit as st
import plotly.graph_objects as go
import pandas as pd


def prepare(df):
    df = df.copy()
    df.columns = df.columns.astype(str).str.strip()

    df["Start"] = pd.to_datetime(df["Start"], errors="coerce")
    df["Finish"] = pd.to_datetime(df["Finish"], errors="coerce")

    df["Activity % Complete"] = (
        df["Activity % Complete"]
        .astype(str)
        .str.replace("%", "", regex=False)
    )

    df["Activity % Complete"] = pd.to_numeric(
        df["Activity % Complete"],
        errors="coerce"
    ).fillna(0)

    return df


def render_pie(df):

    df = prepare(df)
    today = pd.Timestamp.today()

    df["Status"] = "On Track"

    df.loc[
        (df["Finish"] < today) & (df["Activity % Complete"] < 100),
        "Status"
    ] = "Delayed"

    df.loc[
        (df["Finish"] > today) & (df["Activity % Complete"].between(1, 99)),
        "Status"
    ] = "Accelerated"

    summary = df["Status"].value_counts().reindex(
        ["On Track", "Delayed", "Accelerated"],
        fill_value=0
    )

    colors = ["#FFD700", "#FF3B30", "#00C853"]

    fig = go.Figure(
        data=[go.Pie(
            labels=summary.index,
            values=summary.values,
            hole=0.5,
            marker=dict(colors=colors)
        )]
    )

    st.plotly_chart(fig, use_container_width=True)
