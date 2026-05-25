import pandas as pd
import plotly.graph_objects as go


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


def classify(row, today):

    if pd.isna(row["Start"]) or pd.isna(row["Finish"]):
        return "On Track"

    if row["Finish"] < today and row["Activity % Complete"] < 100:
        return "Delayed"

    if row["Activity % Complete"] >= 100:
        return "Completed"

    return "On Track"


def render_pie_ferry(df, container):

    df = prepare(df)
    today = pd.Timestamp.today().normalize()

    df["Status"] = df.apply(lambda r: classify(r, today), axis=1)

    summary = df["Status"].value_counts()

    # ✅ Ensure consistent order
    order = ["On Track", "Delayed", "Completed"]
    summary = summary.reindex(order).fillna(0)

    total = df.shape[0]

    colors = {
        "On Track": "#FFD700",
        "Delayed": "#FF3B30",
        "Completed": "#00C853"
    }

    # =========================
    # ✅ PIE (clean for sidebar)
    # =========================
    fig = go.Figure(
        data=[go.Pie(
            labels=summary.index,
            values=summary.values,
            sort=False,
            textinfo="none",  # ✅ no clutter
            marker=dict(colors=[colors[k] for k in summary.index])
        )]
    )

    fig.update_layout(
        height=200,
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=False
    )

    container.plotly_chart(
        fig,
        use_container_width=True,
        config={"displayModeBar": False}
    )

    # =========================
    # ✅ LEGEND (clean + stable)
    # =========================
    for k in ["On Track", "Delayed", "Completed"]:

        value = int(summary[k])
        pct = (value / total * 100) if total > 0 else 0

        container.markdown(
            f"""
            <div style="
                display:flex;
                justify-content:space-between;
                align-items:center;
                font-size:13px;
                margin-bottom:6px;
            ">
                <div style="display:flex; align-items:center;">
                    <div style="
                        width:10px;
                        height:10px;
                        border-radius:50%;
                        background:{colors[k]};
                        margin-right:6px;
                    "></div>
                    {k}
                </div>
                <div><b>{value}</b> ({pct:.0f}%)</div>
            </div>
            """,
            unsafe_allow_html=True
        )