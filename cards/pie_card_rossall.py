import plotly.graph_objects as go
import pandas as pd


def render_pie_rossall(df, container):

    df = df.copy()
    df.columns = df.columns.astype(str).str.strip()

    # ✅ Clean dates
    df["Start"] = pd.to_datetime(df["Start"], errors="coerce")
    df["Finish"] = pd.to_datetime(df["Finish"], errors="coerce")

    # ✅ Clean % complete
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

    # ✅ Status logic
    def classify(row):
        if pd.isna(row["Start"]) or pd.isna(row["Finish"]):
            return "On Track"

        if row["Finish"] < today and row["Activity % Complete"] < 100:
            return "Delayed"

        if row["Activity % Complete"] >= 100:
            return "Completed"

        return "On Track"

    df["Status"] = df.apply(classify, axis=1)

    summary = df["Status"].value_counts()

    colors = {
        "On Track": "#FFD700",
        "Delayed": "#FF3B30",
        "Completed": "#00C853"
    }

    order = ["On Track", "Delayed", "Completed"]
    summary = summary.reindex([k for k in order if k in summary.index])

    # ✅ Pie chart
    fig = go.Figure(
        data=[go.Pie(
            labels=summary.index,
            values=summary.values,
            sort=False,
            textinfo="none",
            marker=dict(colors=[colors[k] for k in summary.index]),
        )]
    )

    # ✅ Sidebar layout
    fig.update_layout(
        height=220,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        showlegend=False
    )

    container.plotly_chart(fig, use_container_width=True)
