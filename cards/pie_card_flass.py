import pandas as pd
import plotly.graph_objects as go


def render_pie_flass(df, container):
    # ---------- CLEAN ----------
    df = df.copy()
    df.columns = df.columns.str.strip()

    # ✅ Clean Activity ID
    df["Activity ID"] = df["Activity ID"].astype(str).str.strip()

    # ✅ Correct Flass filter (IMPORTANT)
    df = df[df["Activity ID"].str.contains("FL", na=False)]

    # ✅ Numeric % complete
    df["Activity % Complete"] = pd.to_numeric(
        df["Activity % Complete"], errors="coerce"
    ).fillna(0)

    # ✅ Clean Finish date
    df["Finish"] = pd.to_datetime(
        df["Finish"], dayfirst=True, errors="coerce"
    ).dt.normalize()

    # ✅ Remaining Duration
    df["Remaining Duration"] = pd.to_numeric(
        df["Remaining Duration"], errors="coerce"
    ).fillna(0)

    # ---------- REMOVE NON-REAL ACTIVITIES ----------

    # ❌ Remove milestones / summary rows
    df = df[~df["Activity Name"].str.contains(
        "Completion|Terminal Float|Planned Completion",
        case=False,
        na=False
    )]

    # ❌ Remove zero-duration + not started rows
    df = df[~(
            (df["Remaining Duration"] == 0) &
            (df["Activity % Complete"] == 0)
    )]

    # ✅ Safety check
    if df.empty:
        container.info("No valid Flass activities")
        return

    # ✅ Today
    today = pd.Timestamp.today().normalize()

    # ---------- CLASSIFICATION (SAME AS FERRY) ----------
    def classify(row):

        progress = row["Activity % Complete"]
        finish = row["Finish"]

        # ✅ Completed
        if progress >= 100:
            return "Completed"

        # ✅ Delayed
        if pd.notna(finish) and finish < today:
            return "Delayed"

        # ✅ On Track
        return "On Track"

    df["Status"] = df.apply(classify, axis=1)

    # ---------- DEBUG (KEEP FIRST RUN ONLY) ----------
    print("\nFlass Status Breakdown:")
    print(df["Status"].value_counts())

    # ---------- SUMMARY ----------
    summary = df["Status"].value_counts()

    summary = summary.reindex(
        ["On Track", "Delayed", "Completed"]
    ).fillna(0)

    summary = summary[summary > 0]

    # ---------- COLORS ----------
    colors = {
        "On Track": "#FFD700",  # Yellow
        "Delayed": "#FF3B30",  # Red
        "Completed": "#00C853"  # Green
    }

    # ---------- PIE ----------
    fig = go.Figure(
        data=[go.Pie(
            labels=summary.index,
            values=summary.values,

            # ✅ FULL TEXT DISPLAY (LIKE FERRY)
            textinfo="label+value+percent",
            textposition="inside",
            insidetextorientation="auto",

            marker=dict(colors=[colors[k] for k in summary.index]),
            sort=False
        )]
    )

    # ✅ Improve readability
    fig.update_traces(textfont_size=14)

    fig.update_layout(
        height=240,
        margin=dict(l=5, r=5, t=5, b=5),
        showlegend=False
    )

    container.plotly_chart(fig, width="stretch")