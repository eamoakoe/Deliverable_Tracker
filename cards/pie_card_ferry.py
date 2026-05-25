import pandas as pd
import plotly.graph_objects as go


def render_pie_ferry(df, container):

    # --- Copy & clean columns ---
    df = df.copy()
    df.columns = df.columns.str.strip()

    # --- Clean dates ---
    df["Start"] = pd.to_datetime(df["Start"], errors="coerce")
    df["Finish"] = pd.to_datetime(df["Finish"], errors="coerce")

    # --- Clean % complete ---
    df["Activity % Complete"] = (
        df["Activity % Complete"]
        .astype(str)
        .str.replace("%", "", regex=False)
    )

    df["Activity % Complete"] = pd.to_numeric(
        df["Activity % Complete"], errors="coerce"
    ).fillna(0)

    today = pd.Timestamp.today().normalize()

    # --- Status classification ---
    def classify(row):

        progress = row["Activity % Complete"]
        finish = row["Finish"]

        if progress >= 100:
            return "Completed"

        if pd.notna(finish) and finish < today:
            return "Delayed"

        return "On Track"

    df["Status"] = df.apply(classify, axis=1)

    # --- Summary ---
    summary = df["Status"].value_counts()
    summary = summary.reindex(
        ["On Track", "Delayed", "Completed"]
    ).fillna(0)

    total = int(summary.sum())

    # --- Colours ---
    colors = {
        "On Track": "#FFD700",
        "Delayed": "#FF3B30",
        "Completed": "#00C853"
    }

    # =========================
    # ✅ DONUT CHART (clean)
    # =========================
    fig = go.Figure(
        data=[go.Pie(
            labels=summary.index,
            values=summary.values,
            textinfo="none",
            marker=dict(colors=[colors[k] for k in summary.index]),
            hole=0.5
        )]
    )

    fig.update_layout(
        height=180,
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=False
    )

    container.plotly_chart(fig, use_container_width=True)

    # =========================
    # ✅ LEGEND (key fix)
    # =========================
    for status in ["On Track", "Delayed", "Completed"]:

        value = int(summary[status])
        pct = (value / total * 100) if total > 0 else 0

        container.markdown(f"""
        <div style="display:flex; justify-content:space-between;
                    align-items:center; font-size:12px; margin-bottom:4px;">

            <div style="display:flex; align-items:center;">
                <div style="
                    width:10px;
                    height:10px;
                    border-radius:50%;
                    background:{colors[status]};
                    margin-right:6px;">
                </div>
                {status}
            </div>

            <div><b>{value}</b> ({pct:.0f}%)</div>

        </div>
        """, unsafe_allow_html=True)