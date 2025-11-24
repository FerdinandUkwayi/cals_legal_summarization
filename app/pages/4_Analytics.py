import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from app.users.db import DB_PATH, get_summaries_for_analytics
from utils.helpers import init_session_keys

# INIT SESSION
init_session_keys()
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.warning("🚫 Please log in to access the dashboard.")
    st.stop()

st.set_page_config(page_title="Analytics", layout="wide")
st.title("📊 CALS Analytics Dashboard")

# LOAD DATA
@st.cache_data
def load_all_summaries():
    """Loads all generated summaries for analytics."""
    try:
        df = get_summaries_for_analytics()
        if 'username' in df.columns and 'user' not in df.columns:
            df.rename(columns={'username': 'user'}, inplace=True)
        return df
    except Exception as e:
        st.error(f"Database error: {e}")
        return pd.DataFrame()

df = load_all_summaries()

if df.empty:
    st.warning("⚠️ No summaries found in the database. Generate a summary first.")
    st.text(f"Database path: {DB_PATH}")
    st.stop()

# PREPROCESS
df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")
df["date"] = df["created_at"].dt.date

# METRICS
st.subheader("📈 Summary Activity")
col1, col2, col3 = st.columns(3)
col1.metric("Total Summaries", len(df))
col2.metric("Unique Users", df["user"].nunique())
col3.metric("Avg Summary Length", int(df["summary_length"].mean()))

# CHARTS 
st.markdown("---")

# 1️⃣ Summaries Over Time
st.markdown("### 🗓 Summaries Over Time")
time_chart = px.histogram(df, x="date", nbins=30, title="Summaries per Day")
st.plotly_chart(time_chart, use_container_width=True)

# 2️⃣ Summaries by Document Type
st.markdown("### 🗂 Summaries by Document Type")
if "context_doc_type" in df.columns:
    doc_chart = px.pie(df, names="context_doc_type", title="Document Type Distribution")
    st.plotly_chart(doc_chart, use_container_width=True)
else:
    st.info("No document type data found.")

# 3️⃣ Summaries by Jurisdiction
st.markdown("### 🌍 Summaries by Jurisdiction")
if "context_jurisdiction" in df.columns:
    df_jur_counts = df["context_jurisdiction"].value_counts().reset_index()
    df_jur_counts.columns = ["Jurisdiction", "Count"]
    jur_chart = px.bar(df_jur_counts, x="Jurisdiction", y="Count", title="Jurisdiction Breakdown")
    st.plotly_chart(jur_chart, use_container_width=True)

# 4️⃣ Summaries by Goal
st.markdown("### 🎯 Summaries by Goal")
if "context_goal" in df.columns:
    goal_chart = px.pie(df, names="context_goal", title="Summarization Goal Distribution")
    st.plotly_chart(goal_chart, use_container_width=True)

# 5️⃣ User Activity
st.markdown("### 👤 User Activity")
df_user_counts = df["user"].value_counts().reset_index()
df_user_counts.columns = ["User", "Summaries"]
user_chart = px.bar(df_user_counts, x="User", y="Summaries", title="Top Users")
st.plotly_chart(user_chart, use_container_width=True)
