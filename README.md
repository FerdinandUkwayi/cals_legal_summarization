# Context-Aware Legal Summarizer (CALS) Prototype

## Overview

CALS (Context-Aware Legal Summarizer) is a specialized NLP system developed as part of a Master's dissertation on legal technology. Unlike generic summarization tools, CALS allows users to define the specific context in which a summary is required.

By integrating user constraints—Jurisdiction, Document Type, and User Goal—CALS generates summaries tailored for specific legal stakeholders (e.g., Plaintiffs, Defendants, or Risk Compliance Officers).

## Key Features

1. **Context-Driven Generation:** Generates summaries based on specific legal contexts:

   -  Jurisdiction (e.g., US, UK, Nigeria)

   -  Document Type (e.g., Contract, Case Law, Statute)

   -  User Goal (e.g., Compliance, Brief, Analysis)

2. **Recursive Chunking:** Automatically splits long documents into semantic chunks, summarizes them individually, and recursively combines them into a final cohesive summary
3. **Asynchronous Processing:** Uses ProcessPoolExecutor to run heavy model inference without freezing the Streamlit interface.
4. **Custom Tokenizer Handling:** robustly handles special tokens (control codes) to prevent generation artifacts.'Long
5. **Document Support:** Implements a recursive "Map-Reduce" chunking strategy to handle lengthy legal texts beyond standard token limits.
6. **Expert Evaluation Module:** Includes a dedicated interface for legal professionals to rate summaries on Accuracy, Relevance, and Utility.

## Architecture

1. CALS moves beyond standard fine-tuning by implementing a Hybrid Context-Injection mechanism.
2. **Token Signal:** Injects learned control codes (e.g., <goal:plaintiff>) to trigger domain-specific weights.
3. **Semantic Signal:** Wraps input in natural language instructions to guide the model's attention heads.


Supported Contexts

Dimension

Options

Jurisdiction

US, UK, EU

Document Type

Judicial Opinion, Contract, Statute

Goal

Plaintiff Summary, Defendant Summary, Risk Analysis, General Briefing

## Installation

##### Prerequisites
-  Python 3.9 or higher
-  pip (Python Package Manager)

1. **Clone the Repository**
```
git clone [https://github.com/FerdinandUkwayi/cals_legal_summarization](https://github.com/yourusername/legal-summarizerhttps://github.com/FerdinandUkwayi/cals_legal_summarization.git)
cd legal-summarizer
```

2. **Install Dependencies**
```python
pip install -r requirements.txt
```

**Note:** Ensure sentencepiece and torch are installed correctly for your environment.

3. Database Initialization

The system uses SQLite. The database initializes automatically on the first run, but you can force a reset if needed:
```
python app/users/db.py
```

## Usage

### Running the Application

Launch the Streamlit interface:
```
streamlit run Home.py
```

## Workflow

1. **Login/Register:** Create an account to track your summaries.
2. Upload: Upload a legal document (PDF, DOCX, or TXT)
3. **Configure Context:** Select the Jurisdiction, Document Type, and your Goal.
4. **Generate:** Click "Summarize". The system handles chunking and context injection automatically.
5. **Evaluate:** (Optional) Use the "Expert Evaluator" page to rate the output quality.

📂 Project Structure
```
legal_summarizer/
├── app/
│   ├── core/
│   │   ├── summarize.py       # Main inference and chunking logic
│   │   ├── model_utils.py     # Model loading and fallback mechanisms
│   │   └── cals_tokens.py     # Custom control tokens definition
│   ├── pages/
│   │   ├── 1_Login_page.py    # Authentication UI
│   │   ├── 2_Summarizer.py    # Main tool interface
│   │   └── 5_Evaluator.py     # Qualitative evaluation interface
│   └── users/
│       └── db.py              # SQLite database manager (Users, Summaries, Ratings)
├── models/                    # Directory for fine-tuned model artifacts
├── utils/
│   └── helpers.py             # UI helpers and session management
├── Home.py                    # Application Entry Point
├── requirements.txt           # Project dependencies
└── README.md                  # Project documentation
```

## Technology Stack
```
Frontend: Streamlit (Python-based UI)

Model: Google FLAN-T5 (Fine-tuned on Legal Corpora)

Backend Logic: PyTorch, Hugging Face Transformers

Database: SQLite3

Text Processing: NLTK, PyMuPDF (Fitz)
```
## Academic Context

This project investigates the hypothesis that user-driven context significantly improves the utility of legal summaries. It serves as the technical artifact for the dissertation "Context-Aware Summarization for Legal Documents Using NLP."

## Evaluation Methodology
The system includes a built-in **"Expert Evaluator"** module designed to facilitate the Human-in-the-Loop evaluation methodology outlined in Chapter 3 of the thesis. Legal experts can blindly rate summaries
