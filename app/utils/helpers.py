import streamlit as st
import sys
import os

def switch_page(page_name):
    """
    Switches the current view to a different Streamlit page/file.
    
    Args:
        page_name (str): The name of the target page file (e.g., "app/pages/1_Summarizer.py").
    """
    if "pages" in st.__dict__:
        st.switch_page(page_name)
    else:
        st.error(f"Cannot switch page. Please update Streamlit or check page configuration. Attempted page: {page_name}")

def init_session_keys():
    """
    Initializes mandatory session state keys required across the application 
    for login status, user identity, and application state.
    """
    defaults = {
        "logged_in": False,
        "username": "",
        "summary_generated": False,
        "summary": "",
        "chunked": "",
        "login_time": None,
        "user_role": "",
        "doc_type": "",
        "jurisdiction": "",
        "goal": "",
        "reset_stage": "request",
        "reset_email": "",
        "reset_otp": ""
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value