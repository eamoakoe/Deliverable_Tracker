def render_programme_tracker():
    import pandas as pd
    import datetime
    import os

    file_path = "components/contract_submission_dates.xlsx"

    if not os.path.exists(file_path):
        st.sidebar.warning("Tracker file missing")
        return

    df = pd.read_excel(file_path)
    df.columns = df.columns.str.strip()

    today = datetime.datetime.today()
    month = today.strftime("%B")

    if month not in df.columns:
        st.sidebar.warning(f"{month} not in tracker")
        return

    current = df[["KEY", month]].dropna()

    # ✅ Title
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    <div style="
        background:#0b3d0b;
        padding:8px;
        border-radius:6px;
        text-align:center;
        color:white;
        font-weight:600;
        font-size:13px;
    ">
        📘 Contract Submission Dates 2026–2027
    </div>
    """, unsafe_allow_html=True)

    st.sidebar.markdown(f"**📅 {month} Programme**")

    # ✅ TABLE HEADER
    st.sidebar.markdown("""
    <div style="
        display:flex;
        justify-content:space-between;
        font-weight:600;
        padding:4px 6px;
        border-bottom:1px solid #ccc;
        font-size:12px;
    ">
        <span>Activity</span>
        <span>Date</span>
    </div>
    """, unsafe_allow_html=True)

    # ✅ ROWS (COLOUR MATCHED TO YOUR EXCEL)
    for _, row in current.iterrows():
        key = row["KEY"]
        day = int(row[month])

        if "Data date" in key:
            bg = "#d4f5d0"   # light green
            label = "Data date"

        elif "PFA" in key:
            bg = "#fff7cc"   # light amber
            label = "PFA submission"

        elif "submission to client" in key:
            bg = "#cfe8f6"   # light blue
            label = "Client submission"

        elif "accept / reject" in key:
            bg = "#ffd6d6"   # light red
            label = "Accept / Reject"

        else:
            bg = "#f2f2f2"
            label = key

        st.sidebar.markdown(f"""
        <div style="
            display:flex;
            justify-content:space-between;
            background:{bg};
            padding:6px;
            margin:2px 0;
            border-radius:4px;
            font-size:12px;
        ">
            <span>{label}</span>
            <span><b>{day}</b></span>
        </div>
        """, unsafe_allow_html=True)
``