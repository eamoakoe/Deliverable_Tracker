# =========================
# LOOKAHEAD LOGIC (NOW 7 DAYS)
# =========================
def _get_next4weeks(df):   # ✅ KEEP NAME
    df = _prepare(df)

    today = pd.Timestamp.today().normalize()
    lookahead = today + pd.Timedelta(days=7)   # ✅ CHANGED FROM 28 → 7

    upcoming = df[
        (df["Start"].notna()) &
        (df["Finish"].notna()) &
        (df["Start"] <= lookahead) &
        (df["Finish"] >= today)
    ].copy()

    # ✅ ADD BASELINE + DELTA
    if "BL1 Finish" in upcoming.columns:
        upcoming["Delta (Days)"] = (
            upcoming["Finish"] - upcoming["BL1 Finish"]
        ).dt.days

    return upcoming.sort_values("Start", ascending=True)
