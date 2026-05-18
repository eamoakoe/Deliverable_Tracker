import streamlit as st


def render_table(df):
    df = df.copy()

    # SAFE DELIVERABLE REGISTER ONLY
    expected_cols = [
        "Deliverable",
        "CL31 Finish",
        "CL32 Finish",
        "Delta (Days)",
        "Change Type",
        "Status / Comment"
    ]

    cols = [c for c in expected_cols if c in df.columns]

    st.dataframe(
        df[cols],
        use_container_width=True,
        hide_index=True
    )