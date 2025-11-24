import streamlit as st

# Hardcoded user credentials 
USERS = {
    "admin@example.com": "admin123",
    "user@example.com": "password"
}

def login_user(email, password):
    return USERS.get(email) == password

def is_logged_in():
    return st.session_state.get("logged_in", False)

def logout():
    st.session_state["logged_in"] = False
    st.session_state["user_email"] = None
