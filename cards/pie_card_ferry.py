import pandas as pd
import plotly.graph_objects as go


def render_pie_ferry(df, container):

    # ---------- CLEAN ----------
    df = df.copy()
    df.columns = df.columns.str.strip()

    # ✅ Keep only real activities
    df = df[df["Activity ID"].astype(str).str.startswith("FER-")]

    # ✅ Clean % complete (safe now — no blanks)
    df["Activity % Complete"] = (
        df["Activity % Complete"]
        .astype(str)
        .str.replace("%", "", regex=False)
        .str.strip()
    )

    df["Activity % Complete"] = pd.to_numeric(
        df["Activity % Complete"],
        errors="coerce"
    )

    # ✅ Clean Finish date
    df["Finish"] = pd.to_datetime(
        df["Finish"],
        dayfirst=True,
        errors="coerce"
    )

    # ✅ Safety check (very unlikely now)
    if df.empty:
        container.info("No activity data available")
        return

    today = pd.Timestamp.today().normalize()

    # ---------- LOGIC ----------
    def classify(row):

        progress = row["Activity % Complete"]
        finish = row["Finish"]

        # ✅ Completed
        if progress >= 100:
            return "Completed"

        # ✅ Delayed
        if pd.notna(finish) and finish < today and progress < 100:
            return "Delayed"

        # ✅ On Track
        return "On Track"

    df["Status"] = df.apply(classify, axis=1)

    # ---------- SUMMARY ----------
    summary = df["Status"].value_counts()
    summary = summary.reindex(
        ["On Track", "Delayed", "Completed"]
    ).fillna(0)

    summary = summary[summary > 0]

    # ---------- COLORS ----------
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
            textinfo="label+value+percent",
            marker=dict(colors=[colors[k] for k in summary.index]),
            sort=False
        )]
    )

    fig.update_layout(
        height=240,
        margin=dict(l=5, r=5, t=5, b=5),
        showlegend=False
    )

    container.plotly_chart(
        fig,
        width="stretch"
    )
