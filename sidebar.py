import streamlit as st
import base64


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

        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #08111f 0%, #0b1a2f 100%);
        }
    </style>
    """, unsafe_allow_html=True)

    with st.sidebar:

        # =========================
        # LOGO ✅
        # =========================
        st.markdown(f"""
        <div style="text-align:center; padding:10px 0 20px 0;">
            <img src="data:image/png;base64,{logo_base64}" width="80">
        </div>
        """, unsafe_allow_html=True)

        # =========================
        # PROJECTS ONLY ✅
        # =========================
        st.title("Projects")

        project = st.radio(
            "",
            ["Ferry PS", "Rossall Outfall", "Flass Lane"]
        )

    return project