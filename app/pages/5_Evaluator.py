import streamlit as st
import pandas as pd
import sqlite3
from app.users.db import DB_PATH, get_all_summaries, get_summary_by_id
from utils.helpers import init_session_keys

# Initialize session
init_session_keys()
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.warning("🚫 Please log in to access the Expert Evaluator.")
    st.stop()

st.set_page_config(page_title="CALS Evaluator", layout="wide")
st.title("👨‍⚖️ CALS Expert Evaluator")
st.markdown("---")
st.markdown(
    "Use this interface to perform the **Qualitative Human Evaluation** (Chapter 4.8), "
    "assessing generated summaries against a specific contextual goal."
)

# Initialize Expert Ratings Table
def init_evaluation_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expert_ratings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            summary_id INTEGER,
            evaluator_user TEXT,
            target_context_goal TEXT,
            rating_accuracy INTEGER,
            rating_relevance INTEGER,
            rating_coherence INTEGER,
            rating_utility INTEGER,
            comments TEXT,
            FOREIGN KEY (summary_id) REFERENCES summaries(id)
        )
    """)
    conn.commit()
    conn.close()

def log_evaluation(summary_id, evaluator_user, target_context_goal, ratings, comments):
    """Logs the expert's qualitative rating."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO expert_ratings (
            summary_id, evaluator_user, target_context_goal, 
            rating_accuracy, rating_relevance, rating_coherence, rating_utility, comments
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        summary_id, evaluator_user, target_context_goal,
        ratings['Accuracy'], ratings['Relevance'], ratings['Coherence'], ratings['Utility'], comments
    ))
    conn.commit()
    conn.close()

# Initialize Expert Ratings Table
init_evaluation_db()

# Load Summaries
try:
    # get_all_summaries() returns rows: (id, filename, method, summary_length, created_at,
    # context_doc_type, context_jurisdiction, context_goal, username)
    all_summaries_raw = get_all_summaries()
    columns = [
        "id", "filename", "method", "summary_length", "created_at",
        "context_doc_type", "context_jurisdiction", "context_goal", "user"
    ]
    df_meta = pd.DataFrame(all_summaries_raw, columns=columns)

    if df_meta.empty:
        st.info("No summaries available for evaluation. Please generate a summary first.")
        st.stop()

    # Prepare display string showing readable summary info including username
    df_meta['display'] = df_meta.apply(
        lambda row: f"ID {row['id']} | {row['filename']} ({row['context_jurisdiction']}/{row['context_goal']}) | {row['created_at']} | User: {row['user']}",
        axis=1
    )

except Exception as e:
    st.error(f"Could not load summaries from the database. Error: {e}")
    st.stop()

# Select Summary 
st.subheader("1. Select Summary to Evaluate (Summary A)")
selected_display = st.selectbox("Choose a generated summary:", df_meta['display'].tolist(), index=0)

# Get selected id
try:
    selected_row = df_meta[df_meta['display'] == selected_display]
    if selected_row.empty:
        st.error("Selected summary not found in the dataset.")
        st.stop()
    selected_id = int(selected_row['id'].iloc[0])
except Exception as e:
    st.error(f"Error selecting summary ID: {e}")
    st.stop()

# Get summary details
summary_details = get_summary_by_id(selected_id)
if not summary_details:
    st.error("Error retrieving summary details from the database. (No record found for the selected ID.)")
    st.stop()

# Unpack summary_details according to get_summary_by_id() SELECT order:
# (id, filename, username, method, summary, summary_length, created_at, full_text, context_doc_type, context_jurisdiction, context_goal)
(
    summary_id, filename, username, method, summary_text, summary_length,
    created_at, full_text, used_doc_type, used_jurisdiction, used_goal
) = summary_details

# Display Summary and Context
st.markdown("---")
st.subheader(f"2. Evaluation Context: ID {summary_id} by {username}")

col_info, col_rating = st.columns([1, 1.5])

with col_info:
    st.markdown("#### Source Document Preview")
    source_preview = full_text[:5000] if full_text else "(No full text saved)"
    st.text_area("First 5000 characters of Source Text:", source_preview, height=300, disabled=True)

    st.markdown("#### Generated Summary (Summary A)")
    st.text_area("Summary Text:", summary_text or "(No summary text)", height=200, disabled=True)

    st.markdown(
        f"**Context Used for Generation:** "
        f"`{used_jurisdiction.upper()} / {used_doc_type} / {used_goal.replace('_', ' ').title()}`"
    )

with col_rating:
    st.markdown("#### Target Context & Rating")
    target_goal = st.selectbox(
        "Target Goal for Relevance Assessment:",
        ["summarize_for_plaintiff", "summarize_for_defendant", "identify_risks", "general_briefing"],
        key="target_goal_select"
    )
    st.warning(f"Judging summary utility for goal: **{target_goal.replace('_', ' ').title()}**")

    st.markdown("##### 5-Point Likert Rating (1=Poor, 5=Excellent)")
    rating_accuracy = st.slider("1. Factual Accuracy:", 1, 5, 3, key="acc")
    rating_relevance = st.slider("2. Relevance to Target Goal:", 1, 5, 3, key="rel")
    rating_coherence = st.slider("3. Coherence & Fluency:", 1, 5, 3, key="coh")
    rating_utility = st.slider("4. Practical Utility:", 1, 5, 3, key="util")
    comments = st.text_area("Optional Comments on Assessment:")

    if st.button("Submit Expert Rating", type="primary"):
        ratings = {
            "Accuracy": rating_accuracy,
            "Relevance": rating_relevance,
            "Coherence": rating_coherence,
            "Utility": rating_utility
        }
        try:
            log_evaluation(
                summary_id=selected_id,
                evaluator_user=st.session_state.get("username", "anonymous"),
                target_context_goal=target_goal,
                ratings=ratings,
                comments=comments
            )
            st.success(f"✅ Rating for Summary ID {selected_id} submitted successfully!")
            st.balloons()
        except Exception as e:
            st.error(f"Failed to submit rating: {e}")
