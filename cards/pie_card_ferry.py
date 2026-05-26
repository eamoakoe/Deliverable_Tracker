import pandas as pd
import plotly.graph_objects as go


def render_pie_ferry(df, container):

    # ---------- CLEAN ----------
    df = df.copy()
    df.columns = df.columns.str.strip()

    # ✅ Clean Activity ID
    df["Activity ID"] = df["Activity ID"].astype(str).str.strip()

    # ✅ Keep only ferry activities
    df = df[df["Activity ID"].str.startswith("FER-")]

    # ✅ Clean % Complete
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

    # ✅ Replace missing progress with 0
    df["Activity % Complete"] = df["Activity % Complete"].fillna(0)

    # ✅ Clean Finish Date
    df["Finish"] = pd.to_datetime(
        df["Finish"],
        dayfirst=True,
        errors="coerce"
    )

    # ✅ Safety check
    if df.empty:
        container.info("No valid Ferry activities")
        return

    today = pd.Timestamp.today().normalize()

    # ---------- CLASSIFICATION ----------
    def classify(row):

        progress = row["Activity % Complete"]
        finish = row["Finish"]

        # ✅ Completed
        if progress >= 100:
            return "Completed"

        # ✅ If finish missing → treat as On Track (or change to "Unknown" if needed)
        if pd.isna(finish):
            return "On Track"

        # ✅ Delayed (past finish & not completed)
        if finish < today and progress < 100:
            return "Delayed"

        # ✅ Otherwise
        return "On Track"

    df["Status"] = df.apply(classify, axis=1)

    # ---------- DEBUG (VERY IMPORTANT) ----------
    # Shows you exactly how rows are classified
    debug_sample = df[[
        "Activity ID",
        "Activity % Complete",
        "Finish",
        "Status"
    ]].head(20)

    print("\n=== DEBUG SAMPLE ===")
    print(debug_sample)

    # ---------- SUMMARY ----------
    summary = df["Status"].value_counts()

    summary = summary.reindex(
        ["On Track", "Delayed", "Completed"]
    ).fillna(0)

    # ✅ Remove zero values
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
            marker=dict(
                colors=[colors[k] for k in summary.index]
            ),
            sort=False
        )]
    )

    fig.update_layout(
        height=240,
        margin=dict(l=5, r=5, t=5, b=5),
        showlegend=False
    )

    container.plotly_chart(fig, width="stretch")