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

    df.loc[df["Activity % Complete"] == 100, "Status"] = "Completed"

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
    # ✅ THICK PIE (NO HOLE)
    # =========================
    fig = go.Figure(
        data=[go.Pie(
            labels=summary.index,
            values=summary.values,
            sort=False,

            hole=0.0,  # ✅ full pie

            texttemplate="%{value}<br>(%{percent})",
            textfont=dict(size=14, color="black"),

            marker=dict(colors=[colors[k] for k in summary.index]),

            hovertemplate="<b>%{label}</b><br>%{value} tasks<br>%{percent}<extra></extra>"
        )]
    )

    fig.update_layout(
        height=380,
        margin=dict(l=10, r=10, t=10, b=10),
        showlegend=False
    )

    # =========================
    # CARD STYLE
    # =========================
    st.markdown(
        """
        <style>
        .exec-card {
            background: #ffffff;
            border-radius: 18px;
            padding: 18px;
            box-shadow: 0 5px 18px rgba(0,0,0,0.15);
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # =========================
    # RENDER CARD
    # =========================
    with st.container():

        st.markdown('<div class="exec-card">', unsafe_allow_html=True)

        col1, col2 = st.columns([2.2, 1])

        # =========================
        # LEFT → PIE
        # =========================
        with col1:
            st.plotly_chart(fig, use_container_width=True)

        # =========================
        # RIGHT → KPIs + NOTES
        # =========================
        with col2:

            st.markdown("### 📊 Status")

            for k in order:
                pct = (summary[k] / total * 100) if total > 0 else 0
                st.markdown(
                    f"**{k}**: {summary[k]} ({pct:.1f}%)"
                )

            st.markdown("---")
            st.markdown("### 📌 Summary")

            completed = summary["Completed"]
            on_track = summary["On Track"]
            delayed = summary["Delayed"]
            accelerated = summary["Accelerated"]

            if total > 0:
                c_pct = (completed / total) * 100
                d_pct = (delayed / total) * 100
                a_pct = (accelerated / total) * 100
            else:
                c_pct = d_pct = a_pct = 0

            # ✅ Overall interpretation
            if d_pct > 25:
                st.error("🚨 Delivery at risk due to high delays.")
            elif c_pct > 60 and d_pct < 10:
                st.success("✅ Strong delivery performance.")
            else:
                st.info("⚖️ Delivery is stable with mixed performance.")

            # ✅ KPI-aligned notes
            st.markdown(f"- ✅ Completed: {c_pct:.1f}%")
            st.markdown(f"- ⚠️ Delayed: {d_pct:.1f}%")
            st.markdown(f"- 🚀 Accelerated: {a_pct:.1f}%")

        st.markdown('</div>', unsafe_allow_html=True)
``