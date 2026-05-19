import streamlit as st
import base64


def get_base64_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def render_sidebar():
    logo = get_base64_image("assets/logo.png")

    st.markdown("""
    <style>
        [data-testid="stSidebarNav"] {display:none;}
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #08111f 0%, #0b1a2f 100%);
        }
    </style>
    """, unsafe_allow_html=True)

    with st.sidebar:

        st.markdown(f"""
        <div style="text-align:center; padding:10px 0 20px 0;">
            <img src="data:image/png;base64,{logo}" width="80">
        </div>
        """, unsafe_allow_html=True)

        st.title("Projects")

        project = st.radio(
            "",
            ["Ferry PS", "Rossall Outfall", "Flass Lane"]
        )

    return project
``