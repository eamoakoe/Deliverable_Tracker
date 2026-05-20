import streamlit as st
import plotly.graph_objects as go
import pandas as pd


# =========================
# LOAD CL32 ONLY (FIXED PATH)
# =========================
def load_cl32():
    file_path = "data/Ferry/CL32-May.xlsx"
    return pd.read_excel(file_path, engine="openpyxl")


# =========================
# PREP DATA
# =========================
def prepare(df):
    df = df.copy()

    # Clean column names
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
    )

    # Ensure column exists
    if "Activity % Complete" not in df.columns:
        st.error(f"Missing 'Activity % Complete'. Found: {list(df.columns)}")
        return df

    # Dates
    df["Finish"] = pd.to_datetime(df.get("Finish"), errors="coerce")

    # Clean %
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
# PIE
# =========================
def render_pie(df):

    df = prepare(df)
    today = pd.Timestamp.today()

    # ✅ STATUS LOGIC
    df["Status"] = "On Track"

    # 🔴 Delayed
    df.loc[
        (df["Finish"] < today) &
        (df["Activity % Complete"] < 100),
        "Status"
    ] = "Delayed"

    # 🟢 Completed
    df.loc[
        df["Activity % Complete"] >= 100,
        "Status"
    ] = "Completed"

    # =========================
    # SUMMARY
    # =========================
    order = ["On Track", "Delayed", "Completed"]

    summary = df["Status"].value_counts().reindex(order, fill_value=0)

    colors = {
        "On Track": "#FFD700",
        "Delayed": "#FF3B30",
        "Completed": "#00C853"
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
            texttemplate="%{value}<br>(%{percent})",
            marker=dict(colors=[colors[k] for k in summary.index])
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
    col1, col2 = st.columns([2.1, 1])

    with col1:
        st.plotly_chart(fig, use_container_width=True)

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

        st.markdown("---")
        st.caption(
            "🔴 Delayed: past finish date & incomplete\n"
            "🟢 Completed: 100% complete (from CL32)\n"
            "🟡 On Track: not started or in progress"
        )


# =========================
# MAIN
# =========================
st.title("Ferry Tracker (CL32 Only)")

# ✅ Force refresh
st.cache_data.clear()

df = load_cl32()

st.write("Rows loaded:", len(df))  # debug

render_pie(df)