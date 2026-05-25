import streamlit as st
import base64
import pandas as pd
import datetime
import os

# ✅ IMPORT CORRECT FUNCTIONS
from cards.pie_card_ferry import render_pie_ferry
from cards.pie_card_flass import render_pie_flass
from cards.pie_card_rossall import render_pie_rossall


def get_base64_image(path):
    if not os.path.exists(path):
        return ""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def render_sidebar(df_ferry, df_flass, df_rossall):

    logo = get_base64_image("assets/logo.png")

    with st.sidebar:

        if logo:
            st.image(f"data:image/png;base64,{logo}")

        st.title("Projects")

        project = st.radio(
            "",
            ["Ferry PS", "Rossall Outfall", "Flass Lane"]
        )

        # ✅ PROGRAMME STATUS
        st.markdown("---")
        st.markdown("## 📊 Programme Status")

        st.markdown("### 🚢 Ferry")
        render_pie_ferry(df_ferry, st.sidebar)

        st.markdown("### 🏗️ Flass")
        render_pie_flass(df_flass, st.sidebar)

        st.markdown("### 🌊 Rossall")
        render_pie_rossall(df_rossall, st.sidebar)

    return project