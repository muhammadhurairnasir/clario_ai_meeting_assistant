"""
config.py
---------
Centralised configuration for the Clario Flask project.

All hard-coded Google Drive paths from the original notebook are replaced
by configurable defaults that can be overridden via environment variables.
"""

import os

# ── Project root ───────────────────────────────────────────────────────────────
# Resolve the directory that contains THIS file (i.e. the project root).
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


def _env(name: str, default: str) -> str:
    """Return os.environ[name] if set, otherwise *default*."""
    return os.environ.get(name, default)


# ── Data directories ───────────────────────────────────────────────────────────
DATA_DIR        = _env("CLARIO_DATA_DIR",        os.path.join(ROOT_DIR, "data"))
TRANSCRIPT_DIR  = _env("CLARIO_TRANSCRIPT_DIR",  os.path.join(DATA_DIR, "transcripts"))
SUMMARY_DIR     = _env("CLARIO_SUMMARY_DIR",     os.path.join(DATA_DIR, "summaries"))
GRAPH_DIR       = _env("CLARIO_GRAPH_DIR",       os.path.join(DATA_DIR, "graphs"))
EVAL_DIR        = _env("CLARIO_EVAL_DIR",        os.path.join(DATA_DIR, "evaluation"))

# ── Database ───────────────────────────────────────────────────────────────────
DB_PATH         = _env("CLARIO_DB_PATH",         os.path.join(DATA_DIR, "database", "clario.db"))

# ── Upload directory (for audio files) ────────────────────────────────────────
UPLOAD_DIR      = _env("CLARIO_UPLOAD_DIR",      os.path.join(ROOT_DIR, "uploads"))

# ── Model settings ─────────────────────────────────────────────────────────────
WHISPER_MODEL   = _env("CLARIO_WHISPER_MODEL",   "base")
BART_MODEL      = _env("CLARIO_BART_MODEL",      "facebook/bart-large-cnn")
SPACY_MODEL     = _env("CLARIO_SPACY_MODEL",     "en_core_web_sm")

# ── Summarisation settings ─────────────────────────────────────────────────────
SUMMARY_MAX_LENGTH      = int(_env("CLARIO_SUMMARY_MAX_LENGTH",     "150"))
SUMMARY_MIN_LENGTH      = int(_env("CLARIO_SUMMARY_MIN_LENGTH",      "50"))
SUMMARY_MAX_INPUT_CHARS = int(_env("CLARIO_SUMMARY_MAX_INPUT_CHARS", "1000"))

# ── Flask settings ─────────────────────────────────────────────────────────────
SECRET_KEY      = _env("CLARIO_SECRET_KEY",      "change-me-in-production")
DEBUG           = _env("CLARIO_DEBUG",            "True").lower() in ("1", "true", "yes")
PORT            = int(_env("CLARIO_PORT",         "5000"))

# ── Derived file paths (convenience) ──────────────────────────────────────────
TRANSCRIPT_FILE = os.path.join(TRANSCRIPT_DIR, "meeting_transcript.txt")
SUMMARY_FILE    = os.path.join(SUMMARY_DIR,    "meeting_summary.txt")
TASKS_JSON_FILE = os.path.join(TRANSCRIPT_DIR, "detected_tasks.json")
GRAPH_FILE      = os.path.join(GRAPH_DIR,      "knowledge_graph.png")
ROUGE_JSON_FILE = os.path.join(EVAL_DIR,       "rouge_scores.json")
F1_JSON_FILE    = os.path.join(EVAL_DIR,       "f1_scores.json")
