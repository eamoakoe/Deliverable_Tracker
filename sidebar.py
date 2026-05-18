import streamlit as st
import base64
import os


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

    BASE_PATH = "data/Ferry/"

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
        # PROJECT / DATASET
        # =========================
        st.markdown('<div class="section-title">PROJECT</div>', unsafe_allow_html=True)

        project = st.selectbox(
            "",
            ["Ferry"]   # scalable later
        )

        project_path = f"data/{project}/"

        # =========================
        # LOAD FILES
        # =========================
        files = [f for f in os.listdir(project_path) if f.endswith(".xlsx")]

        cl31_files = sorted([f for f in files if f.startswith("CL31")])
        cl32_files = sorted([f for f in files if f.startswith("CL32")])

        # =========================
        # SELECT CL31
        # =========================
        st.markdown('<div class="section-title">CL31 BASELINE</div>', unsafe_allow_html=True)

        selected_cl31 = st.selectbox(
            "",
            cl31_files,
            index=len(cl31_files) - 1 if cl31_files else 0
        )

        # =========================
        # SELECT CL32
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
        import pandas as pd

        cl31 = pd.read_excel(os.path.join(project_path, selected_cl31))
        cl32 = pd.read_excel(os.path.join(project_path, selected_cl32))

        # =========================
        # OPTIONAL FILTER (LIGHT)
        # =========================
        st.markdown('<div class="section-title">FILTER</div>', unsafe_allow_html=True)

        filter_text = st.text_input("Search Activity")

        if filter_text:
            cl32 = cl32[
                cl32["Activity Name"].astype(str).str.contains(filter_text, case=False, na=False)
            ]

        return project, cl31, cl32