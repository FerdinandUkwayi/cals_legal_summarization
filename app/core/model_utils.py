import torch
from transformers import AutoTokenizer, T5ForConditionalGeneration 
from pathlib import Path
import streamlit as st
import warnings
import gc # Gcollector
# from .cals_tokens import ALL_CONTROL_TOKENS 

# Configuration
# Path is set to the locally renamed model directory
CALS_MODEL_DIR = "./app/models/cals_legalbert" 
# Use strict device detection
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# We use session state for caching to bypass Streamlit's problematic @st.cache_resource
MODEL_KEY = 'cals_inf_model'
TOKENIZER_KEY = 'cals_inf_tokenizer'

def load_cals_model():
    """
    Loads the fine-tuned CALS model using the specific T5 class and session state caching.
    Includes aggressive cleanup to stabilize GPU usage.
    """
    # Check Session State Cache first 
    if MODEL_KEY in st.session_state and TOKENIZER_KEY in st.session_state:
        # st.info("Loading model from session state cache.")
        return st.session_state[TOKENIZER_KEY], st.session_state[MODEL_KEY]

    model_path = Path(CALS_MODEL_DIR)
    
    # Suppress non-critical Hugging Face UserWarnings during loading
    warnings.filterwarnings("ignore", category=UserWarning)
    
    if not model_path.is_dir():
        st.error(f"Error: CALS Model deployment directory not found at {CALS_MODEL_DIR}.")
        return None, None

    try:
        # Load AutoTokenizer
        tokenizer = AutoTokenizer.from_pretrained(str(model_path), use_fast=False)
        
        # Load Model: Use the specific T5ForConditionalGeneration class
        model = T5ForConditionalGeneration.from_pretrained(str(model_path))
        
        # Move model to device and set eval mode
        model.to(DEVICE).eval()
        
        # AGGRESSIVE CLEANUP BEFORE CACHING
        if DEVICE == 'cuda':
            torch.cuda.empty_cache()
        gc.collect()

        # Store loaded objects in session state
        st.session_state[TOKENIZER_KEY] = tokenizer
        st.session_state[MODEL_KEY] = model
        
        st.success(f"CALS Model loaded successfully on device: {DEVICE}.")
        return tokenizer, model
        
    except ImportError as ie:
        if 'SentencePiece' in str(ie):
            st.error(
                "**CRITICAL DEPENDENCY MISSING:** The tokenizer requires the **`sentencepiece`** Python library. "
                "Please ensure it is installed."
            )
            return None, None
        raise ie
        
    except Exception as e:
        st.error(f"Failed to load the CALS model. Detailed Error: {e}")
        return None, None