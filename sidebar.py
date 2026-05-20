import streamlit as st
import base64


def get_base64_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def render_sidebar():
    logo = get_base64_image("assets/logo.png")

    # ✅ LIGHT GREEN SIDEBAR STYLE
    st.markdown("""
    <style>
        [data-testid="stSidebarNav"] {
            display: none;
        }

        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #d4f5d0 0%, #a8e6a3 100%);
        }

        /* Optional: Improve text visibility */
        section[data-testid="stSidebar"] .stRadio label {
            color: #0b3d0b;
            font-weight: 500;
        }

        section[data-testid="stSidebar"] h1 {
            color: #0b3d0b;
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