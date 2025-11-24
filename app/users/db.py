import os
import sys
import sqlite3
import pandas as pd
from datetime import datetime
import streamlit as st  

# PATH SETUP 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

# DATABASE DIRECTORY 
DB_DIR = "database"
os.makedirs(DB_DIR, exist_ok=True)
DB_PATH = os.path.join(DB_DIR, "legal_summaries.db")

# USER LOOKUP
def get_user_id_from_username(username):
    """Retrieve the primary key (user_id) from the username."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

#  DATABASE INITIALIZATION
def init_db():
    """Create all required tables for summaries and evaluations."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        # Users Table (if not already created elsewhere)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT,
                email TEXT,
                created_at TEXT
            )
        """)

        # Summaries Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS summaries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                filename TEXT,
                method TEXT,
                summary TEXT,
                summary_length INTEGER,
                created_at TEXT,
                full_text TEXT,
                context_doc_type TEXT,
                context_jurisdiction TEXT,
                context_goal TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)

        # Evaluation Ratings Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS evaluation_ratings (
                rating_id INTEGER PRIMARY KEY AUTOINCREMENT,
                summary_id INTEGER,
                evaluator_user TEXT,
                target_context_goal TEXT,
                rating_accuracy INTEGER,
                rating_relevance INTEGER,
                rating_coherence INTEGER,
                rating_utility INTEGER,
                comments TEXT,
                rated_at TEXT
            )
        """)

        conn.commit()

def save_summary(user, filename, method, summary, summary_length, full_text, created_at,
                 context_doc_type, context_jurisdiction, context_goal):
    """
    Saves a generated summary with contextual details.
    """
    user_id = get_user_id_from_username(user)
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO summaries (
                user_id, filename, method, summary, summary_length, created_at,
                full_text, context_doc_type, context_jurisdiction, context_goal
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id, filename, method, summary, summary_length, created_at,
            full_text, context_doc_type, context_jurisdiction, context_goal
        ))
        conn.commit()

# RETRIEVE SUMMARIES
def get_all_summaries():
    """Fetch all summaries with related user info."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                s.id, 
                s.filename, 
                s.method, 
                s.summary_length, 
                s.created_at, 
                s.context_doc_type, 
                s.context_jurisdiction, 
                s.context_goal, 
                u.username
            FROM summaries s
            LEFT JOIN users u ON s.user_id = u.id
            ORDER BY s.created_at DESC
        """)
        return cursor.fetchall()

def get_summary_by_id(summary_id):
    """Fetch a single summary with all fields and username."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                s.id,
                s.filename,
                u.username,
                s.method,
                s.summary,
                s.summary_length,
                s.created_at,
                s.full_text,
                s.context_doc_type,
                s.context_jurisdiction,
                s.context_goal
            FROM summaries s
            LEFT JOIN users u ON s.user_id = u.id
            WHERE s.id = ?
        """, (summary_id,))
        return cursor.fetchone()

@st.cache_data
def load_user_summaries(user_id):
    """Return a DataFrame of all summaries for a given user."""
    query = """
        SELECT 
            s.id, s.filename, s.method, s.summary_length, s.created_at,
            s.context_doc_type, s.context_jurisdiction, s.context_goal, s.summary,
            u.username
        FROM summaries s
        LEFT JOIN users u ON s.user_id = u.id
        WHERE s.user_id = ?
        ORDER BY s.created_at DESC
    """
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query(query, conn, params=(user_id,))

# ANALYTICS SUPPORT
def get_summaries_for_analytics():
    """Fetch all summaries for analytics dashboard."""
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query("""
            SELECT 
                u.username AS user,
                s.filename,
                s.method,
                s.summary_length,
                s.created_at,
                s.context_doc_type,
                s.context_jurisdiction,
                s.context_goal
            FROM summaries s
            LEFT JOIN users u ON s.user_id = u.id
            ORDER BY s.created_at DESC
        """, conn)

# PASSWORD RESET
def init_password_reset_db():
    """Create password reset table."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS password_resets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                token TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

# INITIALIZE EVERYTHING

def initialize():
    """
    Initialize all required tables (users, summaries, evaluation_ratings, password_resets).
    """
    try:
        init_db()
        init_password_reset_db()
        print("✅ Database initialized successfully.")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
