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


# ✅ FINAL LOGIC
def classify(row, today):

    if pd.isna(row["Start"]) or pd.isna(row["Finish"]):
        return "On Track"

    # 🔴 Delayed = past finish AND not 100%
    if row["Finish"] < today and row["Activity % Complete"] < 100:
        return "Delayed"

    # ✅ Completed
    if row["Activity % Complete"] >= 100:
        return "Completed"

    return "On Track"


def render_pie(df):

    df = prepare(df)
    today = pd.Timestamp.today().normalize()

    df["Status"] = df.apply(lambda r: classify(r, today), axis=1)

    # ✅ REMOVE ZERO VALUES FROM PIE
    summary = df["Status"].value_counts()
    summary = summary[summary > 0]

    colors = {
        "On Track": "#FFD700",
        "Delayed": "#FF3B30",
        "Completed": "#00C853"
    }

    # Keep order but only for existing values
    order = ["On Track", "Delayed", "Completed"]
    summary = summary.reindex([k for k in order if k in summary.index])

    # =========================
    # PIE CHART
    # =========================
    fig = go.Figure(
        data=[go.Pie(
            labels=summary.index,
            values=summary.values,
            sort=False,
            textinfo="label+value",
            textfont=dict(color="black", size=13),
            marker=dict(colors=[colors[k] for k in summary.index]),
            pull=[0.03] * len(summary)
        )]
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
    # CARD STYLE (UNCHANGED)
    # =========================
    st.markdown("""
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
    """, unsafe_allow_html=True)

    # =========================
    # RENDER CARD (UNCHANGED)
    # =========================
    with st.container():

        st.markdown('<div class="pie-card">', unsafe_allow_html=True)

        col1, col2 = st.columns([2.3, 1])

        with col1:
            st.plotly_chart(
                fig,
                use_container_width=True,
                config={"displayModeBar": False}
            )

        with col2:

            # ✅ Dynamically show only existing categories
            display_labels = {
                "On Track": "On Track",
                "Delayed": "Delayed",
                "Completed": "Completed"
            }

            for k in summary.index:
                st.markdown(f"""
                    <div class="item">
                        <div class="dot" style="background:{colors[k]};"></div>
                        {display_labels[k]} <span class="value">{summary[k]}</span>
                    </div>
                """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)
