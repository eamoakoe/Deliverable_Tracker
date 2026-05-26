import pandas as pd
import plotly.graph_objects as go


def render_pie_rossall(df, container):

    # ---------- CLEAN ----------
    df = df.copy()
    df.columns = df.columns.str.strip()

    # ✅ Clean Activity ID
    df["Activity ID"] = df["Activity ID"].astype(str).str.strip()

    # ✅ Keep only real activities (has ID)
    df = df[df["Activity ID"].notna()]
    df = df[df["Activity ID"].str.len() > 0]

    # ✅ Remove summary rows (no ID pattern)
    df = df[df["Activity ID"].str.contains("ROS", na=False)]

    # ✅ Clean Remaining Duration
    df["Remaining Duration"] = (
        df["Remaining Duration"]
        .astype(str)
        .str.replace("d", "", regex=False)
        .str.strip()
    )

    df["Remaining Duration"] = pd.to_numeric(
        df["Remaining Duration"], errors="coerce"
    ).fillna(0)

    # ✅ Clean Finish date
    df["Finish"] = pd.to_datetime(
        df["Finish"].astype(str).str.replace("A", "").str.replace("*", ""),
        dayfirst=True,
        errors="coerce"
    ).dt.normalize()

    # ✅ Detect ACTUALS (key!)
    df["Is_Actual"] = df["Start"].astype(str).str.contains("A", na=False) | \
                      df["Finish"].astype(str).str.contains("A", na=False)

    today = pd.Timestamp.today().normalize()

    # ---------- CLASSIFICATION ----------
    def classify(row):

        finish = row["Finish"]
        remaining = row["Remaining Duration"]
        is_actual = row["Is_Actual"]

        # ✅ Completed
        if is_actual:
            return "Completed"

        # ✅ Delayed
        if pd.notna(finish) and finish < today and remaining > 0:
            return "Delayed"

        # ✅ On Track
        return "On Track"

    df["Status"] = df.apply(classify, axis=1)

    # ---------- DEBUG ----------
    print("\nRossall Breakdown:")
    print(df["Status"].value_counts())

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

            # ✅ FULL TEXT LIKE FERRY
            textinfo="label+value+percent",
            textposition="inside",
            insidetextorientation="auto",

            marker=dict(colors=[colors[k] for k in summary.index]),
            sort=False
        )]
    )

    fig.update_traces(textfont_size=14)

    fig.update_layout(
        height=240,
        margin=dict(l=5, r=5, t=5, b=5),
        showlegend=False
    )

    container.plotly_chart(fig, width="stretch")
