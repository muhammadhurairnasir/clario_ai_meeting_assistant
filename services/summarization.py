"""
services/summarization.py
--------------------------
BART-based meeting summarization service.
Extracted from Clario Project notebook (cells 108-109, 113-114, 120).
"""

import os

# Module-level model cache
_summarizer = None


def load_summarizer(model_name: str = "facebook/bart-large-cnn", device: int = -1):
    """
    Load (or return cached) HuggingFace summarization pipeline.

    Parameters
    ----------
    model_name : HuggingFace model identifier.
    device     : -1 = CPU, 0 = first GPU.

    Returns
    -------
    transformers.Pipeline
    """
    global _summarizer
    if _summarizer is None:
        from transformers import pipeline as hf_pipeline
        print(f"Loading BART summarizer ('{model_name}') ...")
        _summarizer = hf_pipeline(
            "summarization",
            model=model_name,
            device=device,
        )
        print("BART summarizer loaded.")
    return _summarizer


def summarize_text(
    text: str,
    max_length: int = 150,
    min_length: int = 50,
    model_name: str = "facebook/bart-large-cnn",
    device: int = -1,
    max_input_chars: int = 1000,
    summariser=None,
) -> str:
    """
    Summarize *text* using BART.

    Parameters
    ----------
    text            : Source text to summarise.
    max_length      : Maximum token length for the summary.
    min_length      : Minimum token length for the summary.
    model_name      : HuggingFace model identifier.
    device          : -1 = CPU, 0 = first GPU.
    max_input_chars : BART has a token limit; we truncate input to this many
                      characters as a safe heuristic.
    summariser      : Pre-loaded HuggingFace pipeline instance (optional).
                      Pass this to avoid reloading on every call.

    Returns
    -------
    str - Generated summary.
    """
    if summariser is None:
        summariser = load_summarizer(model_name, device)

    # BART has an input token limit; truncate conservatively
    text_to_summarize = text[:max_input_chars]

    # Dynamic length bounds: prevent BART from echoing short inputs
    # Rough heuristic: ~0.75 chars per token
    approx_input_tokens = len(text_to_summarize) // 4

    if approx_input_tokens <= 30:
        # Text is too short to meaningfully summarize — return as-is
        print(f"Input too short ({approx_input_tokens} est. tokens) — returning as-is.")
        return text_to_summarize.strip()

    # Cap max_length to half the input so we actually compress
    safe_max = min(max_length, max(30, approx_input_tokens // 2))
    safe_min = min(min_length, max(10, safe_max // 3))

    result = summariser(
        text_to_summarize,
        max_length=safe_max,
        min_length=safe_min,
        do_sample=False,
    )
    summary = result[0]["summary_text"]
    print(f"Summary generated ({len(summary)} chars, max_len={safe_max}, min_len={safe_min}).")
    return summary


def save_summary(summary: str, output_path: str) -> None:
    """
    Save a summary string to a plain-text file.

    Parameters
    ----------
    summary     : Summary text.
    output_path : Destination file path.
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as fh:
        fh.write(summary)
    print(f"Summary saved to: {output_path}")


def load_summary(summary_path: str) -> str:
    """Load a previously-saved summary from disk."""
    with open(summary_path, "r", encoding="utf-8") as fh:
        return fh.read()
