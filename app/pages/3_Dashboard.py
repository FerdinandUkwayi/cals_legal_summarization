# IMPORTS
import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta

from app.users.db import DB_PATH
from utils.helpers import init_session_keys


# INIT SESSION
init_session_keys()
SESSION_TIMEOUT_MINUTES = 120

if st.session_state.get("logged_in"):
    if st.session_state.get("login_time"):
        time_elapsed = datetime.now() - st.session_state["login_time"]
        if time_elapsed > timedelta(minutes=SESSION_TIMEOUT_MINUTES):
            st.warning("🔒 Session expired. Please log in again.")
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.stop()
else:
    st.warning("🚫 You must log in to access this page.")
    st.stop()


# PAGE SETUP
st.set_page_config(page_title="Dashboard", layout="centered")

st.markdown("""
    <style>
    .main-title { 
        font-size: 2rem; 
        font-weight: bold; 
        color: #FFD700; 
        text-align: center; 
        margin-top: 1rem; 
    }
    .summary-box { 
        background-color: rgba(255, 255, 255, 0.05); 
        border-radius: 12px; 
        padding: 1rem; 
        margin-top: 1rem; 
        color: white; 
    }
    .summary-title { 
        font-weight: bold; 
        font-size: 1.1rem; 
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">📊 Your Legal Summary Dashboard</div>', unsafe_allow_html=True)


# CHECK USER SESSION
user_id = st.session_state.get("user_id")
username = st.session_state.get("username")

if not user_id:
    st.warning("⚠️ User ID not found in session. Please log in again.")
    st.stop()


# FILTERS
st.sidebar.header("🔍 Filter by Context")
doc_type = st.sidebar.selectbox("Document Type", ["All", "statute", "contract", "judicial_opinion"])
jurisdiction = st.sidebar.selectbox("Jurisdiction", ["All", "us", "uk", "eu", "ng"])
goal = st.sidebar.selectbox("Summarization Goal", ["All", "general_briefing", "identify_risks", "summarize_for_plaintiff", "summarize_for_defendant"])


# LOAD DATA (CACHED) 
@st.cache_data
def load_user_summaries(user_id: int):
    """Load summaries for a given user_id, joining the users table."""
    query = """
        SELECT s.id, s.filename, s.method, s.summary_length, s.created_at,
               s.context_doc_type, s.context_jurisdiction, s.context_goal, s.summary,
               u.username
        FROM summaries s
        LEFT JOIN users u ON s.user_id = u.id
        WHERE s.user_id = ?
        ORDER BY s.created_at DESC
    """
    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql_query(query, conn, params=(user_id,))
    return df
df = load_user_summaries(user_id)


# FILTER LOGIC
def matches_context(row):
    db_goal = str(row["context_goal"]).replace(" ", "_")
    return (
        (doc_type == "All" or row["context_doc_type"] == doc_type)
        and (jurisdiction == "All" or row["context_jurisdiction"] == jurisdiction)
        and (goal == "All" or db_goal == goal)
    )


filtered_df = df[df.apply(matches_context, axis=1)]

# DISPLAY SUMMARIES
if filtered_df.empty:
    st.info("No summaries match the selected filters.")
else:
    for i, row in filtered_df.iterrows():
        title = row['filename'].split('.')[0].title() if row['filename'] else f"Summary {row['id']}"

        st.markdown(f"""
            <div class="summary-box">
                <div class="summary-title">📄 {title}</div>
                <div><b>Method:</b> {row['method'].title()} | <b>Length:</b> {row['summary_length']} tokens</div>
                <div><b>Created:</b> {row['created_at'].split('T')[0] if 'T' in row['created_at'] else row['created_at']}</div>
                <div><b>Context:</b> {row['context_doc_type'].upper()} | {row['context_jurisdiction'].upper()} | {row['context_goal'].replace('_', ' ').title()}</div>
                <div><b>Author:</b> {row['username']}</div>
            </div>
        """, unsafe_allow_html=True)

        st.text_area(f"Summary (ID: {row['id']})", row["summary"], height=150, key=f"summary_text_{i}")

        summary_text = f"""Filename: {row['filename']}
Method: {row['method']}
Date: {row['created_at']}
Context: {row['context_doc_type']} | {row['context_jurisdiction']} | {row['context_goal']}
Summary:
{row['summary']}
"""
        st.download_button(
            label="📥 Download Summary",
            data=summary_text,
            file_name=f"{row['filename']}_summary.txt",
            mime="text/plain",
            key=f"download_{i}"
        )
