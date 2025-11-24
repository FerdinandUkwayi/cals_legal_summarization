import fitz  
import tempfile
from docx import Document  
import streamlit as st
import os 

def extract_text(uploaded_file):
    """
    Extract plain text content from an uploaded file.

    Supported formats: PDF, Word Document (DOCX), and Text File (TXT).

    Args:
        uploaded_file (UploadedFile): File uploaded via Streamlit file_uploader.

    Returns:
        str: Extracted text content, or empty string if unsupported or on error.
    """
    if not uploaded_file:
        st.warning("⚠️ No file uploaded. Please provide a document.")
        return ""

    ext = uploaded_file.name.lower().split('.')[-1]
    extracted_text = ""
    tmp_path = None

    try:
        if ext == "pdf":
            # Save to a temp file so PyMuPDF can read it
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(uploaded_file.read())
                tmp.flush()
                tmp_path = tmp.name

            doc = fitz.open(tmp_path)
            extracted_text = "\n".join(page.get_text("text") for page in doc)
            doc.close()

        elif ext == "docx":
            document = Document(uploaded_file)
            extracted_text = "\n".join(p.text for p in document.paragraphs if p.text).strip()

        elif ext == "txt":
            # Decode the uploaded file content
            content = uploaded_file.read().decode("utf-8", errors="ignore")
            extracted_text = content.strip()

        else:
            st.warning(f"⚠️ Unsupported file format: .{ext}. Please upload PDF, DOCX, or TXT.")
            return ""

        # Reset the file pointer for potential reuse 
        uploaded_file.seek(0)
        return extracted_text.strip()

    except Exception as e:
        st.error(f"❌ Error extracting text from .{ext} file: {e}")
        return ""
        
    finally:
        # Clean up the temporary PDF file
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)