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

    # Clean percentage column
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
    # ✅ FINAL STATUS LOGIC
    # =========================
    df["Status"] = "On Track"

    # 🟢 Completed → 100%
    df.loc[
        df["Activity % Complete"] >= 100,
        "Status"
    ] = "Completed"

    # 🔴 Delayed → overdue & not completed
    df.loc[
        (df["Finish"] < today) &
        (df["Activity % Complete"] < 100),
        "Status"
    ] = "Delayed"

    # =========================
    # SUMMARY
    # =========================
    order = ["On Track", "Delayed", "Completed"]

    summary = df["Status"].value_counts().reindex(order, fill_value=0)

    colors = {
        "On Track": "#FFD700",   # Yellow
        "Delayed": "#FF3B30",    # Red
        "Completed": "#00C853"   # Green
    }

    total = int(summary.sum())

    # =========================
    # PIE CHART
    # =========================
    fig = go.Figure(
        data=[go.Pie(
            labels=summary.index,
            values=summary.values,
            sort=False,
            hole=0.0,

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
    # LAYOUT
    # =========================
    with st.container():

        col1, col2 = st.columns([2.1, 1])

        # LEFT → PIE
        with col1:
            st.plotly_chart(fig, use_container_width=True)

        # RIGHT → KPIs
        with col2:

            for k in order:
                pct = (summary[k] / total * 100) if total else 0

                st.markdown(
                    f"""
                    <div style="display:flex;align-items:center;margin-bottom:8px;">
                        <div style="
                            width:10px;
                            height:10px;
                            border-radius:50%;
                            background:{colors[k]};
                            margin-right:8px;">
                        </div>
                        <span><b>{k}:</b> {summary[k]} ({pct:.0f}%)</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            # =========================
            # LOGIC NOTES
            # =========================
            st.markdown("---")

            st.caption(
                "🔴 Delayed: past finish date & incomplete\n"
                "🟢 Completed: 100% complete\n"
                "🟡 On Track: not started or in progress"
            )
