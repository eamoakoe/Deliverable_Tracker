import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import os


# =========================
# GET LATEST FILE
# =========================
def get_latest(folder, prefix):
    files = [
        os.path.join(folder, f)
        for f in os.listdir(folder)
        if f.startswith(prefix) and f.endswith(".xlsx")
    ]

    if not files:
        return None

    return max(files, key=os.path.getmtime)


# =========================
# LOAD DATA
# =========================
def load_ferry():
    base = "data/Ferry/"

    cl32_file = get_latest(base, "CL32")

    if cl32_file is None:
        return pd.DataFrame()

    return pd.read_excel(cl32_file, engine="openpyxl")


# =========================
# PREP DATA (CL32 ONLY)
# =========================
def prepare(df):
    df = df.copy()

    # Clean headers
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
    )

    # ✅ REQUIRED columns
    if "Activity % Complete" not in df.columns:
        st.error(f"Missing column: 'Activity % Complete'. Found: {list(df.columns)}")
        return df

    # Dates
    df["Finish"] = pd.to_datetime(df.get("Finish"), errors="coerce")

    # ✅ Clean % column
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
# PIE CHART (CL32 ONLY)
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

    # 🟢 Completed (ONLY from CL32 % column)
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
            "🟢 Completed (CL32): 100% complete\n"
            "🟡 On Track: not started or in progress"
        )


# =========================
# MAIN APP
# =========================
st.title("Ferry Project Tracker (CL32 Only)")

# ✅ force refresh (important)
st.cache_data.clear()

df_cl32 = load_ferry()

# ✅ debug (remove later)
st.write("Rows loaded (CL32):", len(df_cl32))

if not df_cl32.empty:
    render_pie(df_cl32)
else:
    st.warning("No CL32 data found.")