import pandas as pd
import pandas as pd # ---------- CLEAN ----------
    df = df.copy()
    df.columns = df.columns.str.strip()

    # ✅ Keep only real activities
    df = df[df["Activity ID"].astype(str).str.startswith("FER-")]

    # ✅ Clean % complete properly
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

    # ✅ Ignore blanks COMPLETELY
    df = df[df["Activity % Complete"].notna()]

    # ✅ Clean dates
    df["Finish"] = pd.to_datetime(df["Finish"], dayfirst=True, errors="coerce")

    today = pd.Timestamp.today().normalize()

    # ---------- LOGIC ----------
    def classify(row):

        progress = row["Activity % Complete"]
        finish = row["Finish"]

        if progress >= 100:
            return "Completed"

        if pd.notna(finish) and finish < today and progress < 100:
            return "Delayed"

        return "On Track"

    df["Status"] = df.apply(classify, axis=1)

    # ---------- SUMMARY ----------
    summary = df["Status"].value_counts()
    summary = summary.reindex(
        ["On Track", "Delayed", "Completed"]
    ).fillna(0)

    # ✅ Remove empty slices
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
            textinfo="label+value+percent",
            marker=dict(colors=[colors[k] for k in summary.index])
        )]
    )

    fig.update_layout(
        height=240,
        margin=dict(l=5, r=5, t=5, b=5),
        showlegend=False
    )

    container.plotly_chart(fig, width="stretch")
import plotly.graph_objects as go


def render_pie_ferry(df, container):

