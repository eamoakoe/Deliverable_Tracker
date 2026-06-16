import pandas as pd
import plotly.graph_objects as go


def render_pie_ferry(df, container):

    df = df.copy()
    df.columns = df.columns.str.strip()

    # ✅ Deliverables filter
    df = df[df["Activity Name"].notna()]

    # ✅ Clean fields
    df["Activity ID"] = df["Activity ID"].astype(str).str.strip()
    df["Finish"] = pd.to_datetime(df["Finish"], errors="coerce")

    df["Activity % Complete"] = (
        df["Activity % Complete"]
        .astype(str)
        .str.replace("%", "", regex=False)
        .str.strip()
    )

    df["Activity % Complete"] = pd.to_numeric(
        df["Activity % Complete"], errors="coerce"
    ).fillna(0)

    # =========================
    # ✅ SNAPSHOTS
    # =========================
    dates = sorted(df["SnapshotDate"].dropna().unique())

    if len(dates) < 2:
        container.warning("Not enough snapshots to calculate change")
        return

    base_date = dates[0]
    latest_date = dates[-1]

    base_df = df[df["SnapshotDate"] == base_date][
        ["Activity ID", "Finish"]
    ].rename(columns={"Finish": "Base Finish"})

    latest_df = df[df["SnapshotDate"] == latest_date][
        ["Activity ID", "Finish", "Activity % Complete"]
    ].rename(columns={"Finish": "Latest Finish"})

    # ✅ MERGE ONLY REQUIRED COLUMNS
    merged = pd.merge(
        latest_df,
        base_df,
        on="Activity ID",
        how="left"
    )

    # ✅ SAFE Δ CHANGE
    merged["Δ Change (days)"] = (
        merged["Latest Finish"] - merged["Base Finish"]
    ).dt.days

    merged["Δ Change (days)"] = merged["Δ Change (days)"].fillna(0)

    # =========================
    # ✅ STATUS (MATCH MILESTONE)
    # =========================
    def classify(row):

        if row["Activity % Complete"] >= 100:
            return "Completed"

        if row["Δ Change (days)"] > 0:
            return "Delayed"

        return "On Track"

    merged["Status"] = merged.apply(classify, axis=1)

    # =========================
    # ✅ SUMMARY (FORCE VALUES)
    # =========================
    summary = merged["Status"].value_counts()

    summary = summary.reindex(
        ["On Track", "Delayed", "Completed"]
    ).fillna(0)

    # ✅ DEBUG (optional remove later)
    print("Summary:", summary)

    # =========================
    # ✅ COLOURS
    # =========================
    colors = {
        "On Track": "#FFD700",
        "Delayed": "#FF3B30",
        "Completed": "#00C853"
    }

    # =========================
    # ✅ PIE (ALWAYS SHOWS)
    # =========================
    fig = go.Figure(
        data=[go.Pie(
            labels=summary.index,
            values=summary.values,

            textinfo="label+value+percent",
            textposition="inside",
            insidetextorientation="radial",

            marker=dict(
                colors=[colors[k] for k in summary.index]
            ),

            sort=False
        )]
    )

    fig.update_layout(
        height=260,
        margin=dict(l=5, r=5, t=5, b=5),
        showlegend=False
    )

    container.plotly_chart(fig, width="stretch")
