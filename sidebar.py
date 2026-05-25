import streamlit as stimport stream64
import os

# ✅ IMPORT LOADERS
from loaders.ferry_loader import load_ferry
from loaders.flass_loader import load_flass
from loaders.rossall_loader import load_rossall

# ✅ IMPORT PIE CARDS
from cards.pie_card_ferry import render_pie_ferry
from cards.pie_card_flass import render_pie_flass
from cards.pie_card_rossall import render_pie_rossall


# =========================
# ✅ LOAD LOGO
# =========================
def get_base64_image(path):
    if not os.path.exists(path):
        return ""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


# =========================
# ✅ SIDEBAR (SELF-CONTAINED)
# =========================
def render_sidebar():

    # ✅ Load data INSIDE sidebar
    df_ferry = load_ferry()
    df_flass = load_flass()
    df_rossall = load_rossall()

    logo = get_base64_image("assets/logo.png")

    with st.sidebar:

        # ✅ LOGO
        if logo:
            st.markdown(f"""
            <div style="text-align:center;">
                <img src="data:image/png;base64,{logo}" width="100">
            </div>
            """, unsafe_allow_html=True)

        # ✅ PROJECT SELECTOR
        st.title("Projects")

        project = st.radio(
            "",
            ["Ferry PS", "Rossall Outfall", "Flass Lane"]
        )

        # =========================
        # ✅ PROGRAMME STATUS (Pies)
        # =========================
        st.markdown("---")
        st.markdown("## 📊 Programme Status")

        st.markdown("### 🚢 Ferry")
        if df_ferry is not None and not df_ferry.empty:
            render_pie_ferry(df_ferry, st.sidebar)
        else:
            st.caption("No data")

        st.markdown("### 🏗️ Flass")
        if df_flass is not None and not df_flass.empty:
            render_pie_flass(df_flass, st.sidebar)
        else:
            st.caption("No data")

        st.markdown("### 🌊 Rossall")
        if df_rossall is not None and not df_rossall.empty:
            render_pie_rossall(df_rossall, st.sidebar)
        else:
            st.caption("No data")

    # ✅ Return project for main page logic
    return project
``
