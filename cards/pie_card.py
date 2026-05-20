import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import os


# =========================
# GET LATEST FILE (FIXED)
# =========================
def get_latest(folder, prefix):
    files = [
        os.path.join(folder, f)
        for f in os.listdir(folder)
        if f.startswith(prefix) and f.endswith(".xlsx")
    ]

    if not files:
        return None

    # ✅ Pick latest by modified time
    return max(files, key=os.path.getmtime)


# =========================
# LOAD DATA
# =========================
def load_ferry():
    base = "data/Ferry/"

    cl31_file = get_latest(base, "CL31")
    cl32_file = get_latest(base, "CL32")

    cl31 = pd.read_excel(cl31_file, engine="openpyxl") if cl31_file else pd.DataFrame()
    cl32 = pd.read_excel(cl32_file, engine="openpyxl") if cl32_file else pd.DataFrame()

    return cl31, cl32


# =========================
# DATA PREP
# =========================
def prepare(df):
    df = df.copy()
    df.columns = df.columns.astype(str).str.strip()

    df["Start"] = pd.to_datetime(df["Start"], errors="coerce")
    df["Finish"] = pd.to_datetime(df["Finish"], errors="coerce")

    # ✅ Clean percentage column
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
# PIE FUNCTION
# =========================
def render_pie(df):

    df = prepare(df)
    today = pd.Timestamp.today()

    # ✅ STATUS LOGIC (ORDER MATTERS)
    df["Status"] = "On Track"

    # 🔴 Delayed
    df.loc[
        (df["Finish"] < today) &
        (df["Activity % Complete"] < 100),
        "Status"
    ] = "Delayed"

    # 🟢 Completed (must be LAST)
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
    # UI
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
            "🟢 Completed: 100% complete\n"
            "🟡 On Track: not started or in progress"
        )


# =========================
# MAIN APP
# =========================
st.title("Project Status Tracker")

# ✅ Force fresh load (fix caching issue)
st.cache_data.clear()

cl31, cl32 = load_ferry()

# ✅ Dataset selector (helps debugging + usability)
dataset = st.selectbox("Select dataset", ["CL31", "CL32"])

if dataset == "CL31":
    df = cl31
else:
    df = cl32

# ✅ Debug (remove later)
st.write("Rows loaded:", len(df))

# ✅ Render pie
if not df.empty:
    render_pie(df)
else:
    st.warning("No data found.")
``