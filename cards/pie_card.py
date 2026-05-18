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

    # ✅ FAST classification (improved but same intent)
    df["Status"] = "On Track"

    df.loc[
        (df["Finish"] < today) & (df["Activity % Complete"] < 100),
        "Status"
    ] = "Delayed"

    df.loc[
        (df["Finish"] > today) & (df["Activity % Complete"].between(1, 99)),
        "Status"
    ] = "Accelerated"

    # ✅ Summary
    order = ["On Track", "Delayed", "Accelerated"]
    summary = df["Status"].value_counts().reindex(order, fill_value=0)

    colors = {
        "On Track": "#FFD700",
        "Delayed": "#FF3B30",
        "Accelerated": "#00C853"
    }

    total = int(summary.sum())

    # =========================
    # DONUT CHART
    # =========================
    fig = go.Figure(
        data=[go.Pie(
            labels=summary.index,
            values=summary.values,
            sort=False,
            hole=0.5,

            texttemplate="%{label}<br>%{value} (%{percent})",
            textfont=dict(color="black", size=13),

            marker=dict(colors=[colors[k] for k in summary.index]),

            pull=[0.04, 0.04, 0.04],

            hovertemplate="<b>%{label}</b><br>Tasks: %{value}<br>%{percent}<extra></extra>"
        )]
    )

    # ✅ center label
    fig.add_annotation(
        text=f"<b>{total}</b><br>Total",
        showarrow=False,
        font=dict(size=18, color="black")
    )

    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        height=380,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        font=dict(color="black")
    )

    # =========================
    # CARD STYLE (SAFE)
    # =========================
    st.markdown(
        """
        <style>
        .pie-card {
            background: #ffffff;
            border-radius: 18px;
            padding: 16px;
            box-shadow: 0 4px 14px rgba(0,0,0,0.15);
        }

        .item {
            font-size: 15px;
            margin-bottom: 14px;
            color: black;
            display: flex;
            align-items: center;
        }

        .dot {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 10px;
        }

        .value {
            font-weight: 700;
            margin-left: 6px;
            color: black;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # =========================
    # RENDER CARD
    # =========================
    with st.container():

        st.markdown('<div class="pie-card">', unsafe_allow_html=True)

        col1, col2 = st.columns([2.3, 1])

        # ✅ Chart
        with col1:
            st.plotly_chart(
                fig,
                use_container_width=True,
                config={"displayModeBar": False}
            )

        # ✅ SAFE legend loop (no syntax risk)
        with col2:
            for k in order:
                st.markdown(
                    f"""
                    <div class="item">
                        <div class="dot" style="background:{colors[k]};"></div>
                        {k} <span class="value">{int(summary[k])}</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        st.markdown('</div>', unsafe_allow_html=True)
``