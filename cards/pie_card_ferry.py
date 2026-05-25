import pandas as pd
import plotly.graph_objects as go


def render_pie_ferry(df, container):

    # ---------- CLEAN DATA ----------
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

    # ---------- CORRECT LOGIC ----------
    def classify(row):

        progress = row["Activity % Complete"]
        finish = row["Finish"]

        # ✅ COMPLETED (priority)
        if progress >= 100:
            return "Completed"

        # ✅ DELAYED (only if past finish AND not complete)
        if pd.notna(finish) and finish < today and progress < 100:
            return "Delayed"

        # ✅ ON TRACK
        return "On Track"

    df["Status"] = df.apply(classify, axis=1)

    # ---------- SUMMARY ----------
    summary = df["Status"].value_counts()
    summary = summary.reindex(
        ["On Track", "Delayed", "Completed"]
    ).fillna(0)

    # ✅ remove zeros for cleaner pie
    summary = summary[summary > 0]

    colors = {
        "On Track": "#FFD700",
        "Delayed": "#FF3B30",
        "Completed": "#00C853"
    }

    # ---------- PIE ----------
    fig = go.Figure(
        data=[go.Pie(
            labels=summary.index,
            values=summary.values,
            sort=False,
            textinfo="label+value+percent",
            textfont=dict(size=11, color="black"),
            marker=dict(colors=[colors[k] for k in summary.index]),
            pull=[0.02] * len(summary)
        )]
    )

    fig.update_layout(
        height=240,
        margin=dict(l=5, r=5, t=5, b=5),
        showlegend=False
    )

    container.plotly_chart(
        fig,
        use_container_width=True,
        config={"displayModeBar": False}
    )
