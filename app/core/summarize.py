import torch
import os
import gc 
import warnings
from datetime import datetime
import time 
import cProfile, pstats 
import io

from app.users.db import save_summary
from .model_utils import load_cals_model
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import streamlit as st
import numpy as np 
import nltk
import re

# Ensure NLTK is loaded for sentence splitting
try:
    nltk.data.find('tokenizers/punkt')
except:
    nltk.download('punkt', quiet=True) 

# Configuration Constants
MAX_INPUT_LENGTH = 512
MAX_TARGET_LENGTH = 200 

# DEBUG FLAG
ENABLE_PROFILING = True 

# Safety Constants
MAX_RECURSION_DEPTH = 4 
MAX_PROCESSING_TIME = 120 
CHUNK_SUMMARY_LENGTH = 70

# Custom Chunking Function
# Reduce overlap significantly to reduce redundant inference time.
def get_recursive_chunks(text: str, max_tokens: int = 450, overlap_tokens: int = 30): 
    """Splits text into chunks by respecting sentence boundaries and token limits."""
    sentences = nltk.sent_tokenize(text.strip())
    
    chunks = []
    current_chunk = []
    
    max_words = max_tokens * 0.8 
    overlap_words = overlap_tokens * 0.2 
    current_chunk_words = 0
    
    for sentence in sentences:
        sentence_words = len(sentence.split())
        
        if current_chunk_words + sentence_words <= max_words:
            current_chunk.append(sentence)
            current_chunk_words += sentence_words
        else:
            if current_chunk:
                chunks.append(" ".join(current_chunk))
            
            num_overlap_sentences = 0
            temp_overlap_words = 0
            
            for s in reversed(current_chunk):
                temp_overlap_words += len(s.split())
                if temp_overlap_words > overlap_words and num_overlap_sentences > 0:
                    break
                num_overlap_sentences += 1

            current_chunk = current_chunk[-num_overlap_sentences:] if num_overlap_sentences > 0 else []
            current_chunk_words = sum(len(s.split()) for s in current_chunk)
            current_chunk.append(sentence)
            current_chunk_words += sentence_words
            
    if current_chunk:
        chunks.append(" ".join(current_chunk))
        
    return chunks

# BASE GENERATION FUNCTION 
def generate_single_pass_summary(
    document_text: str, 
    context_codes: str,
    tokenizer: AutoTokenizer,
    model, 
    max_target_length: int 
) -> str:
    """Base function for generating a summary on a single, short input or aggregated chunks."""
    
    input_text = f"{context_codes} {document_text}"
    input_ids = tokenizer(
        input_text, 
        return_tensors="pt", 
        max_length=MAX_INPUT_LENGTH, 
        truncation=True
    ).input_ids.to(model.device)

    with torch.no_grad():
        generated_ids = model.generate(
            input_ids,
            max_length=max_target_length, 
            num_beams=5,
            length_penalty=1.0, 
            early_stopping=True
        )
    summary = tokenizer.decode(generated_ids.squeeze(), skip_special_tokens=True)
    
    # AGGRESSIVE MEMORY CLEANUP
    del input_ids, generated_ids, input_text
    if model.device.type == 'cuda':
        torch.cuda.empty_cache()
    gc.collect()

    return summary


# RECURSIVE CHUNKING LOGIC
def recursive_chunk_summarize(
    document_text: str, 
    context_doc_type: str, 
    context_jurisdiction: str, 
    context_goal: str,
    tokenizer: AutoTokenizer,
    model,
    start_time: float, 
    recursion_depth: int = 0 
) -> str:
    """Implements the Map-Reduce recursive chunking strategy with memory safety and guards."""
    
    # 1. TIME AND DEPTH GUARDS
    if time.time() - start_time > MAX_PROCESSING_TIME:
        raise TimeoutError(f"Summarization exceeded maximum allowed time of {MAX_PROCESSING_TIME} seconds.")
    if recursion_depth >= MAX_RECURSION_DEPTH:
        raise RecursionError(f"Summarization exceeded maximum recursion depth of {MAX_RECURSION_DEPTH}.")

    context_codes = f"<jurisdiction:{context_jurisdiction}> <doc_type:{context_doc_type}> <goal:{context_goal}>"
    
    # 2. Check if Chunking is necessary
    token_count = len(tokenizer.encode(document_text))
    is_recursion_needed = token_count > MAX_INPUT_LENGTH

    if not is_recursion_needed:
        # Final pass: Use the long target length (MAX_TARGET_LENGTH)
        return generate_single_pass_summary(document_text, context_codes, tokenizer, model, MAX_TARGET_LENGTH)

    # Chunking needed - Map phase
    chunks = get_recursive_chunks(document_text, overlap_tokens=30) 
    chunk_summaries = []

    for i, chunk in enumerate(chunks):
        # Inner pass (CHUNK_SUMMARY_LENGTH = 70)
        summary = generate_single_pass_summary(chunk, context_codes, tokenizer, model, CHUNK_SUMMARY_LENGTH)
        chunk_summaries.append(summary)
        
    # Crucial cleanup BEFORE the next recursive step
    if model.device.type == 'cuda':
        torch.cuda.empty_cache()
    gc.collect()

    # Reduce: Concatenate and Recurse
    combined_summary_text = " ".join(chunk_summaries)
    
    # Recursion Check: Call function again if combined text is too long 
    return recursive_chunk_summarize(
        document_text=combined_summary_text,
        context_doc_type=context_doc_type,
        context_jurisdiction=context_jurisdiction,
        context_goal=context_goal,
        tokenizer=tokenizer,
        model=model,
        start_time=start_time, 
        recursion_depth=recursion_depth + 1 
    )

# MAIN EXPOSED FUNCTION (Called by the UI) 
def summarize(user, text, summary_length, filename,
              context_doc_type, context_jurisdiction, context_goal):
    
    # If profiling is enabled, run the profiler instead of the main function
    if ENABLE_PROFILING:
        # Wrapper function to profile the main logic cleanly
        def main_summarization_logic():
             # Re-run the main function body here
            start_time = time.time()
            tokenizer, model = load_cals_model() 
            if model is None: return {"summary_text": "❌ Error during summarization: Model failed to load.", "tokenizer": None}
            
            global MAX_TARGET_LENGTH 
            MAX_TARGET_LENGTH = summary_length 
            text_to_summarize = text.strip()

            if len(text_to_summarize.split()) < 20: return {"summary_text": "⚠️ Input too short to generate a meaningful summary. Please provide more content.", "tokenizer": tokenizer}

            try:
                final_summary = recursive_chunk_summarize(
                    document_text=text_to_summarize, context_doc_type=context_doc_type,
                    context_jurisdiction=context_jurisdiction, context_goal=context_goal,
                    tokenizer=tokenizer, model=model, start_time=start_time
                )
                
                # Skipping save_summary call during profiling to focus on inference
                
                return {"summary_text": final_summary, "tokenizer": tokenizer}

            except (TimeoutError, RecursionError) as e:
                return {"summary_text": f"❌ Profiling Halted Gracefully: {str(e)}", "tokenizer": tokenizer}
            except Exception as e:
                return {"summary_text": f"❌ Profiling Halted By Exception: {str(e)}", "tokenizer": tokenizer}

        pr = cProfile.Profile()
        pr.enable()
        result_dict = main_summarization_logic()
        pr.disable()

        s = io.StringIO() 
        ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
        ps.print_stats(30) # Print top 30 cumulative time consumers
        
        # Display the profiling report in Streamlit's console
        print("\n--- PERFORMANCE PROFILE REPORT (TOP 30 CUMULATIVE TIME CONSUMERS) ---")
        print(s.getvalue())
        print("-------------------------------------------------------------")
        st.info("Profiler report generated in the terminal console.")
        result_dict['summary_text'] = "Profiling complete. Check terminal console for resource usage report."
        return result_dict
    
    # --- NON-PROFILING LOGIC (The standard path) ---
    start_time = time.time() 
    
    tokenizer, model = load_cals_model() 
    
    if model is None:
        return {"summary_text": "❌ Error during summarization: Model failed to load.", "tokenizer": None}

    global MAX_TARGET_LENGTH 
    MAX_TARGET_LENGTH = summary_length 
    
    text_to_summarize = text.strip()

    if len(text_to_summarize.split()) < 20:
        return {"summary_text": "⚠️ Input too short to generate a meaningful summary. Please provide more content.", "tokenizer": tokenizer}
    
    try:
        final_summary = recursive_chunk_summarize(
            document_text=text_to_summarize,
            context_doc_type=context_doc_type,
            context_jurisdiction=context_jurisdiction,
            context_goal=context_goal,
            tokenizer=tokenizer,
            model=model,
            start_time=start_time # Pass the timer start
        )

        # Save summary metadata
        save_summary(
            user=user, filename=filename, method="recursive", summary=final_summary, 
            summary_length=len(final_summary.split()), full_text=text_to_summarize[:10000], 
            context_doc_type=context_doc_type, context_jurisdiction=context_jurisdiction, context_goal=context_goal
        )
        
        return {"summary_text": final_summary, "tokenizer": tokenizer}

    except (TimeoutError, RecursionError) as e:
        st.error(f"❌ Operation Failed Gracefully: {e}")
        return {"summary_text": f"❌ Operation Failed: {str(e)}", "tokenizer": tokenizer}
        
    except Exception as e:
        st.error(f"❌ Critical Error during recursive summarization: {e}")
        return {"summary_text": f"❌ Error during summarization: {str(e)}", "tokenizer": tokenizer} 