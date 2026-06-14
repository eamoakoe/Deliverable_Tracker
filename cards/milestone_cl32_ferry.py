import streamlit as st
import pandas as pd
import re
from datetime import datetime


# =========================
# EXTRACT DATE FROM FILE NAME
# =========================
def extract_cl32_date(file_name):

    match = re.search(
        r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[^\d]*(\d{4})",
        file_name,
        re.IGNORECASE
    )

    if not match:
        return None

    month, year = match.groups()
    month = month[:3].title()

    return datetime.strptime(f"{month} {year}", "%b %Y")


# =========================
# PREP DATA
# =========================
def _prepare(df):

    df = df.copy()
    df.columns = df.columns.astype(str).str.strip()

    df["Activity ID"] = df["Activity ID"].astype(str).str.strip()

    df["Finish"] = (
        df["Finish"]
        .astype(str)
        .str.replace(r"[A\*]", "", regex=True)
        .str.strip()
    )

    df["Finish"] = pd.to_datetime(df["Finish"], errors="coerce")

    return df


# =========================
# DELIVERABLE MAP
# =========================
FERRY_DELIVERABLES = {
    "Design Freeze – Scope Locked": ["FER-PD-1010"],
    "Design Freeze – Client Approved": ["FER-REV-1030"],
    "Concept Design Submission": ["FER-PD-1000"],
    "Full Outline Design Submission": ["FER-PD-1020"],
    "Project Completion": ["FER-PD-1030"],
    "Outline Design Pack Submission": ["FER-REV-1000"],
    "Detailed Design Submission": ["FER-REV-1020"],
    "Final Submission": ["FER-REV-1050"],
    "Geotechnical Report (GDR)": ["FER-GEO-1010"],
    "HAZOP Closeout": ["FER-PRO-1040"],
    "Concept Drawing Issue": ["FER-CSD-1060"],
    "Pile Design Complete": ["FER-CSD-1070"],
    "Civils Design Complete": ["FER-CIV-1070", "FER-CIV-1110", "FER-CIV-1150"],
    "Mechanical Design Complete": ["FER-MEC-1030", "FER-MEC-1040", "FER-MEC-1050"],
    "Mechanical Drawings Issued": ["FER-MEC-1060", "FER-MEC-1110"],
    "Process Design Complete": ["FER-PRO-1010", "FER-PRO-1000", "FER-PRO-1020"],
    "EICA Design Complete": ["FER-EICA-1000", "FER-EICA-1040", "FER-EICA-1070"],
}


# =========================
# EXTRACT DELIVERABLES
# =========================
def extract_milestones(df):

    df = _prepare(df)
    milestones = []

    for name, activity_ids in FERRY_DELIVERABLES.items():

        filtered = df[
            df["Activity ID"].str.contains("|".join(activity_ids), na=False)
        ].copy()

        if filtered.empty:
            continue

        filtered = filtered.sort_values("Finish")
        row = filtered.iloc[-1]

        milestones.append({
            "Deliverable": name,
            "Source Activity": row["Activity Name"],
            "Finish": row["Finish"]
        })

    return pd.DataFrame(milestones)


# =========================
# DETECT NEW DELIVERABLES
# =========================
def detect_new_deliverables(df):

    df = _prepare(df)

    mapped_ids = "|".join(
        [item for sublist in FERRY_DELIVERABLES.values() for item in sublist]
    )

    df_unmapped = df[
        ~df["Activity ID"].str.contains(mapped_ids, na=False)
    ].copy()

    keywords = ["design", "submission", "report", "drawing", "assessment"]

    mask = df_unmapped["Activity Name"].str.lower().str.contains(
        "|".join(keywords), na=False
    )

    return df_unmapped[mask][["Activity ID", "Activity Name", "Finish"]]


# =========================
# STREAMLIT APP
# =========================
st.set_page_config(layout="wide")

st.title("CL32 Deliverables Performance Tracker")

uploaded_files = st.file_uploader(
    "Upload CL32 Programmes",
    type=["xlsx"],
    accept_multiple_files=True
)

if not uploaded_files:
    st.stop()


# =========================
# READ + SORT FILES
# =========================
file_data = []

for file in uploaded_files:

    date = extract_cl32_date(file.name)

    if date is None:
        continue

    df = pd.read_excel(file)

    file_data.append({
        "date": date,
        "df": df
    })

if not file_data:
    st.error("Fix file naming e.g. CL32-June-2026.xlsx")
    st.stop()


file_data = sorted(file_data, key=lambda x: x["date"])

baseline_file = file_data[0]
current_file = file_data[-1]

baseline_label = baseline_file["date"].strftime("CL32_%b_%Y")
current_label = current_file["date"].strftime("CL32_%b_%Y")

st.markdown(f"**Baseline:** {baseline_label} | **Current:** {current_label}")


# =========================
# BUILD TABLE
# =========================
baseline_df = extract_milestones(baseline_file["df"])
current_df = extract_milestones(current_file["df"])

baseline_df = baseline_df.rename(columns={
    "Finish": f"Baseline Finish ({baseline_label})"
})

current_df = current_df.rename(columns={
    "Finish": f"Forecast Finish ({current_label})"
})

table = pd.merge(
    baseline_df,
    current_df,
    on=["Deliverable", "Source Activity"],
    how="outer"
)


# =========================
# DELTA + STATUS
# =========================
def calc_delta(row):

    base = row[f"Baseline Finish ({baseline_label})"]
    curr = row[f"Forecast Finish ({current_label})"]

    if pd.isna(base) or pd.isna(curr):
        return None

    return (curr - base).days


table["Δ vs Baseline (days)"] = table.apply(calc_delta, axis=1)


def status(row):

    base = row[f"Baseline Finish ({baseline_label})"]
    curr = row[f"Forecast Finish ({current_label})"]

    if pd.isna(base) and pd.notna(curr):
        return "New Deliverable"

    if pd.notna(base) and pd.isna(curr):
        return "Removed"

    delta = row["Δ vs Baseline (days)"]

    if pd.isna(delta):
        return "No Data"
    elif delta > 5:
        return "Delayed vs Baseline"
    elif delta < -5:
        return "Ahead of Baseline"
    return "Tracking Baseline"


table["Status"] = table.apply(status, axis=1)


# =========================
# FORMAT DATES
# =========================
for col in table.columns:
    if "CL32" in col:
        table[col] = pd.to_datetime(table[col]).dt.strftime("%d-%b-%Y")


# =========================
# KPIs
# =========================
col1, col2, col3 = st.columns(3)

col1.metric("Delayed", (table["Status"] == "Delayed vs Baseline").sum())
col2.metric("New", (table["Status"] == "New Deliverable").sum())
col3.metric("Removed", (table["Status"] == "Removed").sum())


# =========================
# STYLING
# =========================
def colour_status(val):

    if val == "Delayed vs Baseline":
        return "background-color:#b00020;color:white"
    elif val == "Tracking Baseline":
        return "background-color:#ff9800;color:black"
    elif val == "Ahead of Baseline":
        return "background-color:#1e7e34;color:white"
    elif val == "New Deliverable":
        return "background-color:#1e88e5;color:white"
    elif val == "Removed":
        return "background-color:#6b7280;color:white"
    return ""


styled = table.style.map(colour_status, subset=["Status"])

st.markdown("### Deliverables vs Baseline (Finish Date Comparison)")
st.markdown(styled.to_html(), unsafe_allow_html=True)


# =========================
# NEW DELIVERABLES
# =========================
st.markdown("### Additional Deliverables Introduced")

new_items = detect_new_deliverables(current_file["df"])

if new_items.empty:

    st.success("No new deliverables detected")

else:

    new_items["Finish"] = pd.to_datetime(new_items["Finish"]).dt.strftime("%d-%b-%Y")

    new_items = new_items.rename(columns={
        "Activity ID": "Activity",
        "Activity Name": "Description",
        "Finish": f"Forecast Finish ({current_label})"
    })

    st.dataframe(new_items, use_container_width=True)