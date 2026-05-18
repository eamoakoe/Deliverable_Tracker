import streamlit as st
import plotly.graph_objects as go
import pandas as pd


# =========================
# DATA PREP
# =========================
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


# =========================
# MAIN PIE RENDER
# =========================
def render_pie(df):

    df = prepare(df)
    today = pd.Timestamp.today()

    # =========================
    # STATUS CLASSIFICATION
    # =========================
    df["Status"] = "On Track"

    df.loc[
        (df["Activity % Complete"] == 100),
        "Status"
    ] = "Completed"

    df.loc[
        (df["Finish"] < today) & (df["Activity % Complete"] < 100),
        "Status"
    ] = "Delayed"

    df.loc[
        (df["Finish"] > today) & (df["Activity % Complete"].between(1, 99)),
        "Status"
    ] = "Accelerated"

    # =========================
    # SUMMARY
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
    # THICK DONUT
    # =========================
    fig = go.Figure(
        data=[go.Pie(
            labels=summary.index,
            values=summary.values,
            hole=0.65,  # ✅ thicker donut

            texttemplate="%{value}<br>(%{percent})",
            textfont=dict(size=14, color="black"),

            marker=dict(colors=[colors[k] for k in summary.index]),

            hovertemplate="<b>%{label}</b><br>Count: %{value}<br>%{percent}<extra></extra>"
        )]
    )

    # ✅ center KPI
    fig.add_annotation(
        text=f"<b>{total}</b><br>Total Tasks",
        showarrow=False,
        font=dict(size=20)
    )

    fig.update_layout(
        height=380,
        margin=dict(l=10, r=10, t=10, b=10),
        showlegend=False
    )

    # =========================
    # RENDER
    # =========================
    col1, col2 = st.columns([2.2, 1])

    # ✅ Chart
    with col1:
        st.plotly_chart(fig, use_container_width=True)

    # ✅ Summary panel
    with col2:
        for k in order:
            pct = (summary[k] / total * 100) if total > 0 else 0
            st.markdown(
                f"**{k}**: {summary[k]} ({pct:.1f}%)"
            )

    # =========================
    # EXECUTIVE NOTES
    # =========================
    delayed = summary["Delayed"]
    completed = summary["Completed"]

    if total > 0:
        delayed_pct = (delayed / total) * 100
        completed_pct = (completed / total) * 100
    else:
        delayed_pct = completed_pct = 0

    st.markdown("### 📌 Insights")

    if delayed_pct > 25:
        st.warning("High delivery risk: More than 25% of tasks are delayed.")
    elif delayed_pct > 10:
        st.info("Monitor closely: Some delays emerging.")
    else:
        st.success("Delivery performance is healthy.")

    st.markdown(
        f"- ✅ **Completion rate:** {completed_pct:.1f}%\n"
        f"- ⚠️ **Delay exposure:** {delayed_pct:.1f}%"
    )