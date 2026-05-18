import streamlit as st
import plotly.graph_objects as go
import pandas as pd


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


def render_pie(df):

    df = prepare(df)
    today = pd.Timestamp.today()

    # =========================
    # ✅ CLEAN CLASSIFICATION (ORDER MATTERS)
    # =========================
    df["Status"] = "On Track"

    # 1. Completed (highest priority)
    df.loc[df["Activity % Complete"] >= 100, "Status"] = "Completed"

    # 2. Delayed (overrides On Track only, not Completed)
    df.loc[
        (df["Finish"] < today) &
        (df["Activity % Complete"] < 100),
        "Status"
    ] = "Delayed"

    # 3. Accelerated (only future + started)
    df.loc[
        (df["Finish"] >= today) &
        (df["Activity % Complete"].between(1, 99)),
        "Status"
    ] = "Accelerated"

    # =========================
    # ✅ SUMMARY (CONTROLLED ORDER)
    # =========================
    order = ["Completed", "On Track", "Delayed", "Accelerated"]
    summary = df["Status"].value_counts().reindex(order, fill_value=0)

    colors = {
        "Completed": "#007AFF",
        "On Track": "#FFD700",
        "Delayed": "#FF3B30",
        "Accelerated": "#00C853"
    }

    total = int(summary.sum())

    # =========================
    # ✅ THICK PIE
    # =========================
    fig = go.Figure(
        data=[go.Pie(
            labels=summary.index,
            values=summary.values,
            sort=False,
            hole=0.0,  # full pie

            texttemplate="%{value}<br>(%{percent})",
            textfont=dict(size=13),

            marker=dict(colors=[colors[k] for k in summary.index]),

            hovertemplate="<b>%{label}</b><br>%{value} tasks<br>%{percent}<extra></extra>"
        )]
    )

    fig.update_layout(
        height=360,
        margin=dict(l=5, r=5, t=5, b=5),
        showlegend=False
    )

    # =========================
    # ✅ COMPACT CARD LAYOUT
    # =========================
    with st.container():

        col1, col2 = st.columns([2.1, 1])

        # LEFT → PIE
        with col1:
            st.plotly_chart(fig, use_container_width=True)

        # RIGHT → KPIs + NOTES
        with col2:

            # ✅ KPIs (compact)
            for k in order:
                pct = (summary[k] / total * 100) if total else 0
                st.markdown(f"**{k}:** {summary[k]} ({pct:.0f}%)")

            st.markdown("---")

            # ✅ LOGICALLY CONSISTENT SUMMARY
            d_pct = (summary["Delayed"] / total * 100) if total else 0
            c_pct = (summary["Completed"] / total * 100) if total else 0

            # ✅ SINGLE clear message (no noise)
            if d_pct >= 25:
                st.error("High delay risk")
            elif c_pct >= 60:
                st.success("Strong delivery")
            else:
                st.info("Stable performance")
