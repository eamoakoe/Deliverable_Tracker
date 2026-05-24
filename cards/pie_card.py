import pandas as pd
import streamlit as st


def render_pie(df):
    try:
        if df is None or df.empty:
            st.warning("No data available")
            return

        # Ensure columns exist
        if "Finish" not in df.columns:
            df["Finish"] = pd.NaT

        if "Remaining Duration" not in df.columns:
            df["Remaining Duration"] = "0.00d"

        df["Finish"] = pd.to_datetime(df["Finish"], errors="coerce")

        today = pd.Timestamp.today().normalize()

        def classify(row):
            try:
                remaining = float(str(row["Remaining Duration"]).replace("d", "").strip())
            except:
                remaining = None

            if remaining == 0:
                return "Completed"

            if pd.notna(row["Finish"]) and row["Finish"] < today:
                return "Delayed"

            return "On Track"

        df["Status"] = df.apply(classify, axis=1)

        summary = df["Status"].value_counts()

        st.subheader("Programme Status")
        st.dataframe(summary.rename("Count"))
        st.bar_chart(summary)

    except Exception as e:
        st.error(f"Pie chart failed: {e}")