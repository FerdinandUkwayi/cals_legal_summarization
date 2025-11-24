import streamlit as st
import sys
import os
import base64

# Path Setup
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from utils.helpers import init_session_keys

# Initialize Session Keys
init_session_keys()

# Redirect if not logged in
if not st.session_state.get("logged_in", False):
    st.switch_page("pages/1_Login_page.py")

# Background Styling
def set_background(image_file):
    with open(image_file, "rb") as f:
        data_url = base64.b64encode(f.read()).decode()
    st.markdown(f"""
        <style>
        .stApp {{
            background-image: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.7)), 
                             url("data:image/png;base64,{data_url}");
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
            background-position: center;
        }}
        </style>
    """, unsafe_allow_html=True)

set_background("app/assets/bg.jpeg")

# Prevent Scroll
st.markdown("""
    <style>
    html, body, .stApp {
        height: 100%;
        overflow: hidden; /* Disable scrolling */
    }
    .block-container {
        padding-top: 0rem;
        padding-bottom: 0rem;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar Navigation
with st.sidebar:
    # st.markdown("### Navigation")
    # st.page_link("pages/2_summarizer.py", label="🧾 Summarizer (General Use)")
    # st.page_link("pages/5_Evaluator.py", label="🧑‍⚖️ Qualitative Evaluation")
    # st.page_link("pages/3_dashboard.py", label="📊 Dashboard")
    # st.page_link("pages/4_analytics.py", label="📈 Analytics")
    st.markdown("---")
    if st.button("🚪 Logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.success("You have been logged out.")
        st.switch_page("home.py")

# Hide Sidebar Pages
st.markdown("""
    <style>
    /* Hiding the old, incorrect page indices */
    section[data-testid="stSidebarNav"] li:nth-child(4) {display: none;}
    section[data-testid="stSidebarNav"] li:nth-child(5) {display: none;}
    </style>
""", unsafe_allow_html=True)

# App Header
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("<h1 style='text-align:center; color:white;'>⚖️ Legal AI Document Summarizer</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#eee;'>An NLP-powered tool to summarize lengthy legal documents with support for PDF, DOCX, TXT, chunking, ROUGE scoring, and analytics.</p>", unsafe_allow_html=True)

# Role Greeting 
# role = st.session_state.get("user_role", None)
# if role:
#     st.markdown(f"<p style='text-align:center; color:#ccc;'>Welcome, <b>{role.title()}</b> user!</p>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
with st.container():
    st.markdown("<div class='home-box'>", unsafe_allow_html=True)

    if st.button("🚀 Get Started"):
        st.switch_page("pages/2_summarizer.py")

    st.write("Use the sidebar to:")
    # Call-to-action list 
    st.markdown("""
    - 🧾 *Summarize* your document using AI (General Use)  
    - 📊 *View Analytics* in the Dashboard   
    - 📈 *Evaluate summaries* with ROUGE scoring
    """)
    st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#aaa;'>CALS Prototype v1.0 | Built by Temmytope</p>", unsafe_allow_html=True)