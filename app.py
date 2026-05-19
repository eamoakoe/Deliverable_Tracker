import streamlit as st
import pandas as pd
import os
import re

from components.sidebar import render_sidebar
from components.header import render_header
from components.trend import render_trend
from components.outstanding import render_outstanding_line
from components.age_outstanding import render_age_outstanding


# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Asset TQ & RFI Tracker",
    layout="wide"
)


# =========================
# CLEAN COLUMNS
# =========================
def clean_columns(df):
    df = df.copy()

    df.columns = [
        re.sub(r"\s+", " ", str(c).replace("\n", " ").replace("\u00a0", " ")).strip()
        for c in df.columns
    ]

    df.columns = df.columns.str.strip().str.lower()

    return df


# =========================
# SAFE LOAD FUNCTION
# =========================
def safe_load(path):
    if os.path.exists(path):
        df = pd.read_excel(path, engine="openpyxl")
        return clean_columns(df)
    return None


# =========================
# GET LATEST FILE (GENERIC)
# =========================
def get_latest(base_path, prefix):
    if not os.path.exists(base_path):
        return None

    files = [
        f for f in os.listdir(base_path)
        if f.lower().startswith(prefix.lower()) and f.endswith(".xlsx")
    ]

    if not files:
        return None

    files.sort()
    return os.path.join(base_path, files[-1])


# =========================
# LOAD DATASETS (ALL IN ONE PLACE)
# =========================
@st.cache_data
def load_data():

    return {
        # =====================
        # FERRY (UNCHANGED LOGIC)
        # =====================
        "Ferry CL31": safe_load(get_latest("data/Ferry/", "CL31")),
        "Ferry CL32": safe_load(get_latest("data/Ferry/", "CL32")),

        # =====================
        # FLASS (NEW)
        # =====================
        "Flass CL31": safe_load(get_latest("data/Flass/", "CL31-FL")),
        "Flass CL32": safe_load(get_latest("data/Flass/", "CL32-FL")),

        # =====================
        # ROSSALL (NEW)
        # =====================
        "Rossall CL31": safe_load(get_latest("data/Rossall/", "CL31-RO")),
        "Rossall CL32": safe_load(get_latest("data/Rossall/", "CL32-RO")),
    }


datasets = load_data()


# =========================
# SIDEBAR
# =========================
asset, df, seq = render_sidebar(datasets)

render_header()


# =========================
# HANDLE MISSING DATA
# =========================
if df is None or df.empty:
    st.warning(f"No data available for {asset}")
    st.stop()


# =========================
# CLEAN DATE FIELDS
# =========================
df = df.copy()

df["date sent"] = pd.to_datetime(df.get("date sent"), errors="coerce")
df["reply date"] = pd.to_datetime(df.get("reply date"), errors="coerce")
df["required date"] = pd.to_datetime(df.get("required date"), errors="coerce")


# =========================
# DASHBOARD
# =========================
render_outstanding_line(df, total=len(df))

st.markdown("---")

col1, col2 = st.columns(2, gap="large")

with col1:
    render_trend(df)

with col2:
    render_age_outstanding(df)


# =========================
# ROW DETAILS
# =========================
if seq is not None:

    selected_df = df[df["seq no"] == seq]

    if not selected_df.empty:
        selected = selected_df.iloc[0]

        st.markdown("---")
        st.subheader(f"{selected.get('doc type', '')} - {selected.get('seq no', '')}")

        col1, col2 = st.columns(2)

        with col1:
            st.write("**Originator:**", selected.get("originator", "—"))
            st.write("**Sender:**", selected.get("sender", "—"))
            st.write("**Recipient:**", selected.get("recipient", "—"))

        with col2:
            st.write("**Date Sent:**", selected.get("date sent", "—"))
            st.write("**Required Date:**", selected.get("required date", "—"))
            st.write("**Reply Date:**", selected.get("reply date", "—"))

        st.write("**Subject:**", selected.get("subject", "—"))
        st.write("**Notes:**", selected.get("notes", "—"))
        st.write("**Status:**", selected.get("status", "—"))
