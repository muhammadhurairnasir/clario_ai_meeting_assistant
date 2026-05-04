"""
services/summarization.py
--------------------------
BART-based meeting summarization service.
Extracted from Clario Project notebook.
"""

import os

# Module-level model cache
_summarizer_model = None
_summarizer_tokenizer = None


def load_summarizer(model_name: str = "facebook/bart-large-cnn", device: int = -1):
    """
    Load (or return cached) HuggingFace summarizer model and tokenizer.
    """
    global _summarizer_model, _summarizer_tokenizer
    if _summarizer_model is None or _summarizer_tokenizer is None:
        from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
        import torch
        print(f"Loading BART tokenizer ('{model_name}') ...")
        _summarizer_tokenizer = AutoTokenizer.from_pretrained(model_name)
        print(f"Loading BART model ('{model_name}') ...")
        _summarizer_model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        if device == 0 and torch.cuda.is_available():
            _summarizer_model = _summarizer_model.cuda()
        print("BART summarizer loaded.")
    return _summarizer_model, _summarizer_tokenizer


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
    Summarize *text* using BART explicitly.
    """
    if not text.strip():
        return ""

    if summariser is None:
        model, tokenizer = load_summarizer(model_name, device)
    else:
        model, tokenizer = summariser

    # BART has an input token limit; truncate conservatively
    text_to_summarize = text[:max_input_chars]

    # Dynamic length bounds: prevent BART from echoing short inputs
    approx_input_tokens = len(text_to_summarize) // 4

    if approx_input_tokens <= 30:
        print(f"Input too short ({approx_input_tokens} est. tokens) — returning as-is.")
        return text_to_summarize.strip()

    safe_max = min(max_length, max(30, approx_input_tokens // 2))
    safe_min = min(min_length, max(10, safe_max // 3))

    print(f"Summarising text ({len(text_to_summarize)} chars input) ...")
    try:
        import torch
        inputs = tokenizer(text_to_summarize, return_tensors="pt", max_length=1024, truncation=True)
        
        if device == 0 and torch.cuda.is_available():
            inputs = {k: v.cuda() for k, v in inputs.items()}
            
        summary_ids = model.generate(
            inputs["input_ids"],
            max_length=safe_max,
            min_length=safe_min,
            num_beams=4,
            early_stopping=True
        )
        summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        print(f"Summary generated ({len(summary)} chars, max_len={safe_max}, min_len={safe_min}).")
        return summary
    except Exception as exc:
        print(f"️  Summarization failed: {exc}")
        return text


def save_summary(summary: str, output_path: str) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as fh:
        fh.write(summary)
    print(f"Summary saved to: {output_path}")


def load_summary(summary_path: str) -> str:
    with open(summary_path, "r", encoding="utf-8") as fh:
        return fh.read()
