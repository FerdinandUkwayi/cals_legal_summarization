import streamlit as st
import sys
import os
import base64
from datetime import datetime

# Adjust system path to import modules from parent directories (e.g., 'app.users', 'utils')
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

# Import user-defined functions for authentication and utility
from app.users.users import register_user, authenticate_user 
from app.users.db import initialize 
from utils.helpers import switch_page, init_session_keys 

# Initialize the database and session state keys on script run
initialize() 
init_session_keys()

# Function to apply custom CSS styling, including a background and a styled login box
def set_background(image_file):
    st.markdown(f"""
        <style>
        .stApp {{
            /* Dark gradient background for a professional look */
            background: linear-gradient(rgba(10, 20, 30, 0.9), rgba(5, 15, 25, 0.9)); 
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
            background-position: center;
        }}
        .login-box {{
            /* Styling for the central login/register containers */
            padding: 30px;
            border-radius: 15px;
            background-color: rgba(0, 0, 0, 0.85);
            box-shadow: 0 0 20px rgba(0,0,0,0.5);
            color: white; 
        }}
        .stButton>button {{
            /* Ensure buttons take full width for better mobile experience */
            width: 100%;
            margin-top: 10px;
        }}
        </style>
    """, unsafe_allow_html=True)

# Apply the custom background style
set_background(None) 

# Core function to handle user login attempt
def handle_login(username, password):
    # Call the backend function to verify credentials
    # Assumes authenticate_user returns (bool, user_record or error_message)
    success, result_or_record = authenticate_user(username, password)
    
    if success:
        # Authentication successful: parse user data and update session state
        user_id = result_or_record[0]
        user_name = result_or_record[1] 

        st.session_state["logged_in"] = True
        st.session_state["username"] = user_name
        st.session_state["user_id"] = user_id
        st.session_state["login_time"] = datetime.now()
        
        st.success(f"Welcome, {user_name}! Redirecting...")

        # Switch to the main application page
        st.switch_page("home.py") 
    else:
        # Authentication failed: display the error message
        st.error(result_or_record) 

# Main layout structure: centering the content
col_header, col_main = st.columns([1, 4])
with col_main:
    # Display the application title
    st.markdown("<h1 style='text-align:center; color:#FFD700;'>⚖️ CALS System Access</h1>", unsafe_allow_html=True)
    
    # Check if the user is already logged in via session state
    if st.session_state.get("logged_in"):
        st.info(f"You are already logged in as **{st.session_state.get('username')}**.")
        
        # Button to navigate to the main summarizer page (Page 2)
        st.button("Continue to Summarizer", 
                  on_click=lambda: st.switch_page("pages/2_Summarizer.py"))
        
        # Logout logic: clear session state flags
        if st.button("Logout"):
            st.session_state["logged_in"] = False
            st.session_state["username"] = None
            st.session_state["user_id"] = None
        
        # Stop execution to prevent rendering the login/register forms below
        st.stop()

    # Create tabs for Login and Register forms
    tab1, tab2 = st.tabs(["🔒 Login", "✍️ Register"])

    with tab1:
        st.markdown("<div class='login-box'>", unsafe_allow_html=True)
        with st.form("login_form"):
            # Login input fields
            login_username = st.text_input("Username", key="login_user")
            login_password = st.text_input("Password", type="password", key="login_pass")
            submitted = st.form_submit_button("Login to CALS", type="primary")

            if submitted:
                # Validation and calling the login handler
                if not login_username or not login_password:
                    st.error("Please enter both username and password.")
                else:
                    handle_login(login_username, login_password)
        st.markdown("</div>", unsafe_allow_html=True)


    with tab2:
        st.markdown("<div class='login-box'>", unsafe_allow_html=True)
        with st.form("register_form"):
            # Registration input fields
            reg_username = st.text_input("Username (Case Insensitive)", key="reg_user")
            reg_password = st.text_input("Password (Min 6 chars)", type="password", key="reg_pass")
            reg_email = st.text_input("Email", key="reg_email")
            reg_submitted = st.form_submit_button("Register Account", type="secondary")

            if reg_submitted:
                # Call backend function to register the user
                result = register_user(reg_username, reg_password, reg_email)
                if result is True:
                    st.success("✅ Registration successful! Please log in above.")
                else:
                    st.error(f"Registration failed: {result}")
        st.markdown("</div>", unsafe_allow_html=True)