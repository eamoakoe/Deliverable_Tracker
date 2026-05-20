import streamlit as st
import plotly.graph_objects as go
import pandas as pd


# =========================
# LOAD CL32 ONLY
# =========================
def load_cl32():
    file_path = "data/Ferry/CL32-May.xlsx"
    return pd.read_excel(file_path, engine="openpyxl")


# =========================
# PREP DATA (FIXED CLEANING)
# =========================
def prepare(df):
    df = df.copy()

    # Clean column names
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
    )

    # Check column exists
    if "Activity % Complete" not in df.columns:
        st.error(f"Missing column. Found: {list(df.columns)}")
        return df

    # Convert Finish date
    df["Finish"] = pd.to_datetime(df.get("Finish"), errors="coerce")

    # ✅ ✅ CRITICAL FIX (handles hidden Excel characters)
    df["Activity % Complete"] = (
        df["Activity % Complete"]
        .astype(str)
        .str.replace(r"[^0-9.]", "", regex=True)  # removes %, spaces, hidden chars
    )

    df["Activity % Complete"] = pd.to_numeric(
        df["Activity % Complete"],
        errors="coerce"
    ).fillna(0)

    return df


# =========================
# PIE FUNCTION
# =========================
def render_pie(df):

    df = prepare(df)
    today = pd.Timestamp.today()

    # =========================
    # ✅ STATUS LOGIC
    # =========================
    df["Status"] = "On Track"

    # 🔴 Delayed
    df.loc[
        (df["Finish"] < today) &
        (df["Activity % Complete"] < 100),
        "Status"
    ] = "Delayed"

    # 🟢 Completed (now WILL work)
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
    # PIE
    # =========================
    fig = go.Figure(
        data=[go.Pie(
            labels=summary.index,
            values=summary.values,
            sort=False,
            texttemplate="%{value}<br>(%{percent})",
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
            "🟢 Completed: 100% complete (CL32)\n"
            "🟡 On Track: not started or in progress"
        )


# =========================
# MAIN APP
# =========================
st.title("Ferry Tracker (CL32 Only)")

# Force refresh
st.cache_data.clear()

df = load_cl32()

# ✅ DEBUG (remove after confirming)
st.write("Rows loaded:", len(df))
st.write("Sample cleaned values:", df["Activity % Complete"].head(10))

# Render
render_pie(df)
