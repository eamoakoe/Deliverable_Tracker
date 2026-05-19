import streamlit as st
import base64
import os
import pandas as pd


# =========================
# LOAD LOGO
# =========================
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()


# =========================
# SIDEBAR
# =========================
def render_sidebar():

    logo_base64 = get_base64_image("assets/logo.png")

    # =========================
    # STYLE
    # =========================
    st.markdown("""
    <style>
        [data-testid="stSidebarNav"] {display:none;}
        [data-testid="stSidebarNavItems"] {display:none;}

        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #08111f 0%, #0b1a2f 100%);
        }

        .section-title {
            color:#b8b8d1;
            font-size:12px;
            margin-top:15px;
            margin-bottom:5px;
        }
    </style>
    """, unsafe_allow_html=True)

    with st.sidebar:

        # =========================
        # LOGO
        # =========================
        st.markdown(f"""
        <div style="text-align:center; padding:10px 0 20px 0;">
            <img src="data:image/png;base64,{logo_base64}" width="80">
        </div>
        """, unsafe_allow_html=True)

        # =========================
        # PROJECT LIST ✅
        # =========================
        st.markdown('<div class="section-title">PROJECT</div>', unsafe_allow_html=True)

        project = st.radio(
            "",
            ["Ferry PS", "Rossall Outfall", "Flass Lane"]
        )

        # =========================
        # MAP PROJECT → PATH ✅
        # =========================
        project_map = {
            "Ferry PS": ("data/Ferry/", "", ""),
            "Rossall Outfall": ("data/Rossall/", "CL31-RO", "CL32-RO"),
            "Flass Lane": ("data/Flass/", "CL31-FL", "CL32-FL"),
        }

        base_path, cl31_prefix, cl32_prefix = project_map[project]

        # Ferry uses standard naming
        if project == "Ferry PS":
            cl31_prefix = "CL31"
            cl32_prefix = "CL32"

        # =========================
        # GET FILES
        # =========================
        files = [f for f in os.listdir(base_path) if f.endswith(".xlsx")]

        cl31_files = sorted([f for f in files if f.startswith(cl31_prefix)])
        cl32_files = sorted([f for f in files if f.startswith(cl32_prefix)])

        # =========================
        # CL31 SELECT
        # =========================
        st.markdown('<div class="section-title">CL31 BASELINE</div>', unsafe_allow_html=True)

        selected_cl31 = st.selectbox(
            "",
            cl31_files,
            index=len(cl31_files) - 1 if cl31_files else 0
        )

        # =========================
        # CL32 SELECT
        # =========================
        st.markdown('<div class="section-title">CL32 CURRENT</div>', unsafe_allow_html=True)

        selected_cl32 = st.selectbox(
            "",
            cl32_files,
            index=len(cl32_files) - 1 if cl32_files else 0
        )

        # =========================
        # LOAD DATA
        # =========================
        cl31 = pd.read_excel(os.path.join(base_path, selected_cl31))
        cl32 = pd.read_excel(os.path.join(base_path, selected_cl32))

        # =========================
        # FILTER (optional)
        # =========================
        st.markdown('<div class="section-title">FILTER</div>', unsafe_allow_html=True)

        filter_text = st.text_input("Search Activity")

        if filter_text and "Activity Name" in cl32.columns:
            cl32 = cl32[
                cl32["Activity Name"].astype(str).str.contains(filter_text, case=False, na=False)
            ]

        return project, cl31, cl32

