import pandas as pd
import plotly.graph_objects as go


def render_pie_rossall(df, container):

    df = df.copy()
    df.columns = df.columns.str.strip()

    # ✅ Clean dates
    df["Start"] = pd.to_datetime(df.get("Start"), errors="coerce")
    df["Finish"] = pd.to_datetime(df.get("Finish"), errors="coerce")

    # ✅ OPTIONAL: % complete (may not exist)
    if "Activity % Complete" in df.columns:
        df["Activity % Complete"] = (
            df["Activity % Complete"]
            .astype(str)
            .str.replace("%", "", regex=False)
        )
        df["Activity % Complete"] = pd.to_numeric(
            df["Activity % Complete"], errors="coerce"
        ).fillna(0)
    else:
        df["Activity % Complete"] = None  # placeholder

    today = pd.Timestamp.today().normalize()

    # ✅ Status logic (handles missing % complete)
    def classify(row):

        finish = row["Finish"]
        progress = row["Activity % Complete"]

        # ✅ If no finish date → treat as On Track
        if pd.isna(finish):
            return "On Track"

        # ✅ If % exists → use normal logic
        if pd.notna(progress):

            if finish < today and progress < 100:
                return "Delayed"

            if progress >= 100:
                return "Completed"

            return "On Track"

        # ✅ If NO % complete → use DATE-ONLY logic
        else:

            if finish < today:
                return "Delayed"

            return "On Track"

    df["Status"] = df.apply(classify, axis=1)

    summary = df["Status"].value_counts()
    summary = summary.reindex(["On Track", "Delayed", "Completed"]).fillna(0)

    colors = {
        "On Track": "#FFD700",
        "Delayed": "#FF3B30",
        "Completed": "#00C853"
    }

    fig = go.Figure(
        data=[go.Pie(
            labels=summary.index,
            values=summary.values,
            textinfo="label+percent",
            hoverinfo="label+value+percent",
            marker=dict(colors=[colors[k] for k in summary.index])
        )]
    )

    fig.update_layout(height=220, showlegend=False)

    container.plotly_chart(fig, use_container_width=True)