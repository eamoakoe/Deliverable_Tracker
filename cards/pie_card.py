import streamlit as st
import pandas as pd
import plotly.graph_objects as go

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
# CLASSIFICATION (FAST)
# =========================
def classify(df):
    today = pd.Timestamp.today()

    df["Status"] = "On Track"

    df.loc[
        (df["Finish"] < today) & (df["Activity % Complete"] < 100),
        "Status"
    ] = "Delayed"

    df.loc[
        (df["Finish"] > today) & (df["Activity % Complete"].between(1, 99)),
        "Status"
    ] = "Accelerated"

    return df


# =========================
# KPI SECTION
# =========================
def render_kpis(df):
    total = len(df)
    completed = (df["Activity % Complete"] == 100).sum()
    delayed = (df["Status"] == "Delayed").sum()
    progress = round(df["Activity % Complete"].mean(), 1)

    cols = st.columns(4)

    cols[0].metric("Total Tasks", total)
    cols[1].metric("Completed", completed)
    cols[2].metric("Delayed", delayed, delta=None)
    cols[3].metric("Avg Progress %", f"{progress}%")


# =========================
# DONUT CHART
# =========================
def render_status_chart(df):
    summary = df["Status"].value_counts().reindex(
        ["On Track", "Delayed", "Accelerated"],
        fill_value=0
    )

    colors = {
        "On Track": "#FFD700",
        "Delayed": "#FF3B30",
        "Accelerated": "#00C853"
    }

    total = summary.sum()

    fig = go.Figure(
        data=[go.Pie(
            labels=summary.index,
            values=summary.values,
            hole=0.5,
            sort=False,

            texttemplate="%{label}<br>%{value} (%{percent})",

            marker=dict(colors=summary.index.map(colors)),

            hovertemplate="<b>%{label}</b><br>Tasks: %{value}<br>%{percent}<extra></extra>"
        )]
    )

    fig.add_annotation(
        text=f"<b>{total}</b><br>Total",
        showarrow=False
    )

    fig.update_layout(
        height=350,
        margin=dict(l=10, r=10, t=10, b=10)
    )

    st.plotly_chart(fig, use_container_width=True)


# =========================
# TREND ANALYSIS
# =========================
def render_timeline(df):
    timeline = df.copy()

    timeline["Month"] = timeline["Finish"].dt.to_period("M").astype(str)
    trend = timeline.groupby("Month")["Activity % Complete"].mean().reset_index()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=trend["Month"],
        y=trend["Activity % Complete"],
        mode="lines+markers",
        name="Progress Trend"
    ))

    fig.update_layout(
        title="Progress Trend Over Time",
        height=300
    )

    st.plotly_chart(fig, use_container_width=True)


# =========================
# FILTERS
# =========================
def render_filters(df):
    st.sidebar.header("Filters")

    status_filter = st.sidebar.multiselect(
        "Status",
        options=df["Status"].unique(),
        default=df["Status"].unique()
    )

    return df[df["Status"].isin(status_filter)]


# =========================
# MAIN DASHBOARD
# =========================
def render_dashboard(df):

    df = prepare(df)
    df = classify(df)

    st.title("📊 Executive Project Dashboard")

    # Filters
    df = render_filters(df)

    # KPI row
    render_kpis(df)

    st.divider()

    col1, col2 = st.columns([1.2, 1])

    with col1:
        st.subheader("Status Distribution")
        render_status_chart(df)

    with col2:
        st.subheader("Trend")
        render_timeline(df)

    st.divider()

    st.subheader("Task Details")
    st.dataframe(df, use_container_width=True)
``