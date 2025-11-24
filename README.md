Context-Aware Legal Summarizer (CALS) Prototype

Executive Summary

The Context-Aware Legal Summarizer (CALS) v10 is a research prototype developed to empirically test the feasibility of building dynamically adaptive NLP systems for the high-stakes legal domain.

Primary Goal: To investigate whether explicitly embedding user-defined adversarial context (e.g., Plaintiff vs. Defendant) into the summarization pipeline can produce demonstrably more relevant and higher-utility summaries than generalized models.

Core Finding: The final adversarial test revealed that standard Sequence-to-Sequence fine-tuning, even with aggressive data augmentation, failed to achieve semantic divergence between opposing goals. This finding serves as a critical empirical contribution, defining the methodological limitations of current NLP techniques when applied to adversarial legal subjectivity.


🔧 Technologies & Libraries Used:
- Python 3.10+
- Streamlit
- Hugging Face Transformers
- Hugging Face Datasets
- SQLite
- Pandas
- scikit-learn
- Matplotlib / Altair (for dashboard)
- bcrypt (for password hashing)

Model Details:
--------------------------------------------------------
1. Pretrained Model: facebook/bart-large-cnn
2. Fine-Tuned Version: Trained on a legal dataset using Hugging Face's Trainer API in Google Colab
3. Evaluation: ROUGE metrics (ROUGE-1, ROUGE-2, ROUGE-L)

--------------------------------------------------------
📁 Folder Structure:
--------------------------------------------------------

legal_summarizer/
│
├── app/
│   ├── assets/               → UI backgrounds, images
│   ├── models/               → fine-tuned model (finetuned_bart/)
│   ├── pages/
│   │   ├── 1_home.py         → Welcome page
│   │   ├── 2_summarizer.py   → Upload and summarize documents
│   │   └── 3_dashboard.py    → Visual analytics dashboard
│   ├── backend.py            → Summarization logic & pipeline
│   ├── db.py                 → Summary database logic (SQLite)
│   ├── users.py              → User authentication module
│   ├── utils.py              → Evaluation and helper functions
│   └── login_page.py         → Main app entry, Login/Register page
│
├── database/                 → Stores app.db (SQLite)
├── requirements.txt          → All dependencies
├── README.txt                → This file
└── finetuning_notebook.ipynb → Colab notebook for fine-tuning

--------------------------------------------------------
🚀 Features:
--------------------------------------------------------

✅ Upload and summarize PDF or text content  
✅ Chunking support for long legal texts  
✅ Option to use pretrained or fine-tuned model  
✅ ROUGE metric evaluation  
✅ SQLite-based history tracking  
✅ Dashboard with visual analytics (date, method, length, file)  
✅ Login/Register system with hashed passwords  
✅ Clean and professional UI  
✅ Easily deployable (local or cloud)

--------------------------------------------------------
🧪 Model Fine-Tuning (Colab Overview):
--------------------------------------------------------

Fine-tuned using Hugging Face's facebook/bart-large-cnn model on a custom legal dataset in Colab.  
Steps:
- Load & preprocess dataset (text, summary)
- Tokenize and train using Trainer API
- Save model and integrate into the Streamlit app

📌 Training parameters:
- Epochs: 2  
- Batch size: 2  
- Max length: 1024 tokens  
- Output: app/models/finetuned_bart/

--------------------------------------------------------
📦 Setup & Usage:
--------------------------------------------------------

1. Clone or extract the project
2. Create a virtual environment:
   python -m venv .venv
   .venv\Scripts\activate  (Windows)
3. Install dependencies:
   pip install -r requirements.txt
4. Run the app:
   streamlit run app/login_page.py

--------------------------------------------------------
📌 Additional Notes:
--------------------------------------------------------

- Users must register and log in to use the app
- Summaries are saved to the database with metadata
- Dashboard charts provide insights into usage
- Code is modular, clean, and fully commented


