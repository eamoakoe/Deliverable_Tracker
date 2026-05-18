import streamlit as st


def render_deliverables_table(df):

    # =========================
    # COLOUR CHANGE TYPES
    # =========================
    def colour_change(val):
        if val == "DELAYED":
            return "background-color:#fdecea; color:#b71c1c; font-weight:600"
        elif val == "EARLY":
            return "background-color:#e8f5e9; color:#1b5e20; font-weight:600"
        elif val == "NEW":
            return "background-color:#e3f2fd; color:#0d47a1; font-weight:600"
        elif val == "REMOVED":
            return "background-color:#f3e5f5; color:#6a1b9a; font-weight:600"
        else:
            return ""

    # =========================
    # DELTA COLOUR (NUMERIC)
    # =========================
    def colour_delta(val):
        if pd.isna(val):
            return ""
        elif val > 0:
            return "color:#d32f2f; font-weight:600"   # red delay
        elif val < 0:
            return "color:#2e7d32; font-weight:600"  # green early
        else:
            return "color:#616161"

    # =========================
    # ROW STRIPING
    # =========================
    def stripe_rows(row):
        return [
            "background-color:#ffffff" if row.name % 2 == 0 else "background-color:#f7f9fc"
        ] * len(row)

    # =========================
    # TABLE STYLE
    # =========================
    styled = (
        df.style

        .set_table_styles([
            {
                "selector": "th",
                "props": [
                    ("background-color", "#1e3a8a"),
                    ("color", "white"),
                    ("font-size", "12.5px"),
                    ("font-weight", "700"),
                    ("text-transform", "uppercase"),
                    ("letter-spacing", "0.6px"),
                    ("padding", "10px 8px"),
                    ("border-bottom", "3px solid #3b82f6")
                ]
            },
            {
                "selector": "td",
                "props": [
                    ("padding", "8px"),
                    ("color", "#1f2a44"),
                    ("border-bottom", "1px solid #e5e7eb")
                ]
            },
            {
                "selector": "table",
                "props": [
                    ("border-collapse", "collapse"),
                    ("width", "100%"),
                    ("background-color", "white"),
                    ("border-radius", "8px"),
                    ("overflow", "hidden"),
                    ("box-shadow", "0 1px 3px rgba(0,0,0,0.08)")
                ]
            }
        ])

        # Row striping
        .apply(stripe_rows, axis=1)

        # Highlight change types
        .map(colour_change, subset=["Change Type"])

        # Highlight delta column
        .map(colour_delta, subset=["Delta (Days)"])

        # Alignment
        .set_properties(subset=["Deliverable"], **{"text-align": "left"})
        .set_properties(subset=["CL31 Finish", "CL32 Finish"], **{"text-align": "center"})
        .set_properties(subset=["Delta (Days)", "Change Type"], **{"text-align": "center"})
        .set_properties(subset=["Status / Comment"], **{"text-align": "left"})
    )

    # =========================
    # KPI SUMMARY
    # =========================
    total = len(df)
    delayed = (df["Change Type"] == "DELAYED").sum()
    new = (df["Change Type"] == "NEW").sum()
    removed = (df["Change Type"] == "REMOVED").sum()

    st.markdown(
        f"""
        <span style='font-weight:600'>
            🔴 {delayed} Delayed &nbsp;&nbsp;|
            🟢 {total - delayed - new - removed} Stable &nbsp;&nbsp;|
            🔵 {new} New &nbsp;&nbsp;|
            🟣 {removed} Removed
        </span>
        """,
        unsafe_allow_html=True
    )

    # =========================
    # RENDER
    # =========================
    st.write(styled)
