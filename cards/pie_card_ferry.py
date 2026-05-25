import pandas as pd
import plotly.graph_objects as go


def render_pie_ferry(df, container):

    # --- Clean data ---
    df = df.copy()
    df.columns = df.columns.str.strip()

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

    today = pd.Timestamp.today().normalize()

    # --- Status logic ---
    def classify(row):
        if pd.isna(row["Start"]) or pd.isna(row["Finish"]):
            return "On Track"

        if row["Finish"] < today and row["Activity % Complete"] < 100:
            return "Delayed"

        if row["Activity % Complete"] >= 100:
            return "Completed"

        return "On Track"

    df["Status"] = df.apply(classify, axis=1)

    # --- Summary ---
    summary = df["Status"].value_counts()
    summary = summary.reindex(["On Track", "Delayed", "Completed"]).fillna(0)

    colors = {
        "On Track": "#FFD700",
        "Delayed": "#FF3B30",
        "Completed": "#00C853"
    }

    # --- Pie chart ---
    fig = go.Figure(
        data=[go.Pie(
            labels=summary.index,
            values=summary.values,
            textinfo="label+percent",
            hoverinfo="label+value+percent",
            marker=dict(colors=[colors[k] for k in summary.index])
        )]
    )

    fig.update_layout(
        height=220,
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=False
    )

    container.plotly_chart(fig, use_container_width=True)