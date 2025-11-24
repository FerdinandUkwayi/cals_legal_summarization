import streamlit as st
from rouge_score import rouge_scorer
import matplotlib.pyplot as plt

# ROUGE Evaluation
def evaluate_rouge(generated_summary, reference_summary):
    """
    Compares generated vs reference summaries using ROUGE metrics.

    Args:
        generated_summary (str): The summary produced by CALS.
        reference_summary (str): The human-written reference summary.

    Returns:
        dict: ROUGE-1, ROUGE-2, ROUGE-L scores (F1 measure).
    """
    scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
    scores = scorer.score(reference_summary, generated_summary)

    return {
        'ROUGE-1': round(scores['rouge1'].fmeasure, 2),
        'ROUGE-2': round(scores['rouge2'].fmeasure, 2),
        'ROUGE-L': round(scores['rougeL'].fmeasure, 2),
    }

# ROUGE Visualization
def plot_rouge_scores(scores_dict):
    """
    Displays ROUGE metrics as a bar chart.

    Args:
        scores_dict (dict): Dictionary of ROUGE scores.

    Returns:
        matplotlib.figure.Figure: Bar chart figure.
    """
    labels = list(scores_dict.keys())
    values = list(scores_dict.values())

    fig, ax = plt.subplots()
    ax.bar(labels, values, color=['#FFD700', '#FF8C00', '#20B2AA'])
    ax.set_ylim(0, 1)
    ax.set_ylabel("ROUGE Score")
    ax.set_title("ROUGE Evaluation")
    return fig
