import pandas as pd
import plotly.graph_objects as go


def render_pie_ferry(df, container):

    # ---------- CLEAN ----------
    df = df.copy()
    df.columns = df.columns.str.strip()

    df["Activity ID"] = df["Activity ID"].astype(str).str.strip()
    df = df[df["Activity ID"].str.startswith("FER-")]

    # ✅ Clean % Complete
    df["Activity % Complete"] = (
        df["Activity % Complete"]
        .astype(str)
        .str.replace("%", "", regex=False)
        .str.strip()
    )

    df["Activity % Complete"] = pd.to_numeric(
        df["Activity % Complete"], errors="coerce"
    ).fillna(0)

    # ✅ Clean Finish date (FORCE DATE ONLY)
    df["Finish"] = pd.to_datetime(
        df["Finish"], dayfirst=True, errors="coerce"
    ).dt.normalize()

    today = pd.Timestamp.today().normalize()

    # ✅ DEBUG COUNTS
    print("Total rows:", len(df))
    print("Missing Finish:", df["Finish"].isna().sum())

    # ---------- CLASSIFICATION ----------
    def classify(row):

        progress = row["Activity % Complete"]
        finish = row["Finish"]

        # ✅ 1. Completed ALWAYS wins
        if progress >= 100:
            return "Completed"

        # ✅ 2. If no finish → treat as On Track (your rule)
        if pd.isna(finish):
            return "On Track"

        # ✅ 3. Delayed
        if finish < today:
            return "Delayed"

        # ✅ 4. Future = On Track
        return "On Track"

    df["Status"] = df.apply(classify, axis=1)

    # ---------- DEBUG BREAKDOWN ----------
    print("\nStatus Breakdown:")
    print(df["Status"].value_counts())

    print("\nSample Problem Rows:")
    print(df[
        (df["Status"] == "Delayed")
    ][["Activity ID", "Finish", "Activity % Complete"]].head(10))

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