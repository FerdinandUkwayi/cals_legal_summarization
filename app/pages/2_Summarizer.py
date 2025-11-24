import streamlit as st
import sys
import os
import base64

# Path Setup
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from app.core.summarize import summarize
from app.core.metrics import evaluate_rouge
from app.core.extract import extract_text as extract_text_from_upload

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

# Sidebar
with st.sidebar:
    st.markdown("---")
    if st.button("🚪 Logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.success("You have been logged out.")
        st.switch_page("home.py")

# Custom Styles
st.markdown("""
    <style>
    .block-container {
        max-width: 800px;
        margin: auto;
        padding: 2rem;
        background-color: rgba(0, 0, 0,0.8);
        border-radius: 20px;
        box-shadow: 0 0 15px rgba(0,0,0,0.3);
        color: white;
    }
    h1, h2, h3 {
        font-family: 'Segoe UI', sans-serif;
        font-weight: bold;
        color: #FFD700;
    }
    .stButton > button {
        background-color: #FFB000;
        color: black;
        font-weight: bold;
        border-radius: 8px;
        padding: 0.6em 1.2em;
    }
    .stTextInput > div > div > input,
    .stTextArea textarea {
        background-color: #222;
        color: white;
        border-radius: 5px;
    }
    .stSlider > div {
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# Session State Init
if "summary_generated" not in st.session_state:
    st.session_state["summary_generated"] = False
if "final_summary_text" not in st.session_state:
    st.session_state["final_summary_text"] = ""

# Page Header
st.markdown("<h2 style='text-align:center; color:white;'>🧾 CALS Legal Document Summarizer</h2>", unsafe_allow_html=True)

# Input Form
if not st.session_state["summary_generated"]:
    with st.container():
        st.markdown("<div class='form-box'>", unsafe_allow_html=True)

        input_mode = st.radio("Choose input method:", ["📤 Upload file", "📝 Paste text"], horizontal=True)

        if input_mode == "📤 Upload file":
            uploaded_file = st.file_uploader("Upload PDF, DOCX, or TXT", type=["pdf", "docx", "txt"])
            extracted_text = extract_text_from_upload(uploaded_file) if uploaded_file else ""
        else:
            uploaded_file = None
            extracted_text = st.text_area("Paste your legal text here", height=200)

        st.markdown("---")
        st.markdown("#### ⚖️ Define Contextual Goal")
        col1, col2, col3 = st.columns(3)
        with col1:
            doc_type = st.selectbox("Document Type", ["judicial_opinion", "contract", "statute"])
        with col2:
            jurisdiction = st.selectbox("Jurisdiction", ["us", "uk", "eu"])
        with col3:
            goal = st.selectbox("Summarization Goal", ["summarize_for_plaintiff", "summarize_for_defendant", "identify_risks", "general_briefing"])

        summary_length = st.slider("📝 Desired summary length (tokens)", 100, 200, 200)

        if st.button("🧠 Generate Summary (Automatic Chunking)", type="primary", use_container_width=True):
            if not extracted_text.strip():
                st.warning("Please provide adequate text content to generate a summary.")
                st.stop()

            with st.spinner("Generating summary using CALS..."):
                user = st.session_state.get("username", "anonymous")
                filename = uploaded_file.name if uploaded_file else "pasted_text"

                result = summarize(
                    user=user,
                    text=extracted_text.strip(),
                    summary_length=summary_length,
                    filename=filename,
                    context_doc_type=doc_type,
                    context_jurisdiction=jurisdiction,
                    context_goal=goal,
                )

                if "❌ Error" in result['summary_text']:
                    st.error(result['summary_text'])
                else:
                    st.session_state["final_summary_text"] = result["summary_text"]
                    st.session_state["extracted_text"] = extracted_text
                    st.session_state["context"] = {
                        "doc_type": doc_type,
                        "jurisdiction": jurisdiction,
                        "goal": goal,
                        "tokenizer": result["tokenizer"]
                    }
                    st.session_state["summary_length"] = summary_length
                    st.session_state["summary_generated"] = True

                    # Show immediate feedback before rerun
                    st.success("✅ Summary generated, refreshing view...")
                    st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

# Results View
if st.session_state["summary_generated"]:
    st.success("✅ Context-Aware Summary Generated")

    final_summary_text = st.session_state["final_summary_text"]

    st.subheader("📋 Generated Summary")
    st.text_area("Summary Output", final_summary_text, height=200)

    st.download_button("📥 Download Summary", final_summary_text, file_name="legal_summary.txt")

    st.markdown("---")
    st.subheader("📊 ROUGE Evaluation")
    ref = st.text_area("Paste a *Reference Summary* to evaluate against", height=150)

    if ref and st.button("Calculate ROUGE Score"):
        try:
            scores = evaluate_rouge(
                generated_summary=st.session_state["final_summary_text"],
                reference_summary=ref
            )
            st.markdown("**Evaluation Results:**")
            st.write(f"*ROUGE-1 F1-Score:* `{scores['ROUGE-1']:.2f}`")
            st.write(f"*ROUGE-2 F1-Score:* `{scores['ROUGE-2']:.2f}`")
            st.write(f"*ROUGE-L F1-Score:* `{scores['ROUGE-L']:.2f}`")
        except Exception as e:
            st.error(f"Could not calculate ROUGE. Error: {e}")

    if st.button("🔁 Start New Summary"):
        for key in ["final_summary_text", "summary_generated", "extracted_text", "context", "summary_length"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()
