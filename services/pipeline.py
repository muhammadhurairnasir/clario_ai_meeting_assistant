"""
services/pipeline.py
---------------------
Master Clario pipeline:
  audio / text  →  transcript  →  summary  →  tasks  →  graph  →  DB

Public API
----------
    results = run_clario_pipeline(
        audio_path  = "/path/to/recording.mp3",   # or None
        text_input  = "Raw transcript text …",     # or None
        meeting_id  = 7,                           # pre-created DB row
        user_id     = 3,
        db_path     = "/path/to/clario.db",
        graph_dir   = "/path/to/graphs/",
    )
"""

import os
from datetime import datetime
from typing import Any, Dict, Optional

from config import (
    DB_PATH, GRAPH_DIR,
    WHISPER_MODEL, BART_MODEL, SPACY_MODEL,
    SUMMARY_MAX_LENGTH, SUMMARY_MIN_LENGTH,
)
import pathlib


# ── Lazy model cache ───────────────────────────────────────────────────────────
_whisper_model    = None
_summariser       = None
_nlp              = None


def _get_whisper():
    global _whisper_model
    if _whisper_model is None:
        from services.transcription import load_whisper
        _whisper_model = load_whisper(WHISPER_MODEL)
    return _whisper_model


def _get_summariser():
    global _summariser
    if _summariser is None:
        from services.summarization import load_summarizer
        _summariser = load_summarizer(BART_MODEL)
    return _summariser


def _get_nlp():
    global _nlp
    if _nlp is None:
        from services.task_detection import load_nlp
        _nlp = load_nlp(SPACY_MODEL)
    return _nlp


# ── Main pipeline ──────────────────────────────────────────────────────────────

def run_clario_pipeline(
    audio_path: Optional[str]  = None,
    text_input: Optional[str]  = None,
    meeting_id: Optional[int]  = None,
    user_id:    Optional[int]  = None,
    db_path:    str            = DB_PATH,
    graph_dir:  str            = GRAPH_DIR,
) -> Optional[Dict[str, Any]]:
    """
    Run the full Clario AI pipeline and persist results.

    Parameters
    ----------
    audio_path  : Path to an audio file (if provided, Whisper is used).
    text_input  : Raw transcript text (used if no audio_path or as fallback).
    meeting_id  : Pre-created meeting row id in the DB.
    user_id     : Authenticated user id (stored for graph naming).
    db_path     : SQLite database path.
    graph_dir   : Directory where the knowledge graph PNG will be saved.

    Returns
    -------
    dict with keys: transcript, summary, tasks, graph_path, stats
    None if no usable input was provided.
    """

    from models.database import (
        insert_transcript, insert_summary,
        insert_tasks, set_meeting_graph,
    )
    from services.transcription import transcribe_audio
    from services.summarization import summarize_text
    from services.task_detection import detect_tasks

    # ── 1. Transcription ───────────────────────────────────────────────────────
    if audio_path and os.path.exists(audio_path):
        print(" Transcribing audio …")
        try:
            transcript = transcribe_audio(audio_path, model=_get_whisper())
        except Exception as exc:
            print(f"️  Whisper failed: {exc}. Falling back to text_input.")
            transcript = text_input or ""
    elif text_input:
        transcript = text_input
    else:
        print(" No audio file or text input provided.")
        return None

    if not transcript.strip():
        print(" Empty transcript — cannot proceed.")
        return None

    print(f" Transcript length: {len(transcript)} chars")

    # ── 2. Summarisation ───────────────────────────────────────────────────────
    print(" Summarising …")
    try:
        summary = summarize_text(
            transcript,
            summariser  = _get_summariser(),
            max_length  = SUMMARY_MAX_LENGTH,
            min_length  = SUMMARY_MIN_LENGTH,
        )
    except Exception as exc:
        print(f"️  Summarisation failed: {exc}")
        summary = transcript[:500]          # graceful degradation

    print(f" Summary length: {len(summary)} chars")

    # ── 3. Task detection ──────────────────────────────────────────────────────
    print(" Detecting tasks …")
    try:
        tasks = detect_tasks(transcript, nlp=_get_nlp())
    except Exception as exc:
        print(f"️  Task detection failed: {exc}")
        tasks = []

    print(f" {len(tasks)} task(s) detected")

    # ── 4. Persist to DB ───────────────────────────────────────────────────────
    graph_path = ""
    if meeting_id is not None:
        try:
            insert_transcript(meeting_id, transcript, db_path)
            insert_summary(meeting_id,    summary,    db_path)
            if tasks:
                insert_tasks(meeting_id, tasks, db_path)
            print(f" Results saved to DB (meeting_id={meeting_id})")
        except Exception as exc:
            print(f"️  DB save failed: {exc}")

        # ── 5. Knowledge graph ─────────────────────────────────────────────────
        try:
            from utils.visualization import build_knowledge_graph
            # Save inside static/graphs/ so Flask can serve via url_for('static')
            app_root = pathlib.Path(__file__).resolve().parent.parent
            static_graph_dir = app_root / "static" / "graphs"
            static_graph_dir.mkdir(parents=True, exist_ok=True)
            graph_filename = f"graph_m{meeting_id}.png"
            graph_path_abs = static_graph_dir / graph_filename
            # Attach sequential id to each task dict for graph node IDs
            tasks_for_graph = [dict(t, id=i+1) for i, t in enumerate(tasks)]
            build_knowledge_graph(tasks_for_graph, output_path=str(graph_path_abs))
            # Store only the static-relative path (e.g. "graphs/graph_m7.png")
            graph_path = f"graphs/{graph_filename}"
            set_meeting_graph(meeting_id, graph_path, db_path)
            print(f"  Knowledge graph saved: {graph_path_abs}")
        except Exception as exc:
            print(f"  Knowledge graph failed: {exc}")

    return {
        "transcript": transcript,
        "summary":    summary,
        "tasks":      tasks,
        "graph_path": graph_path,
        "stats": {
            "meeting_id":   meeting_id,
            "task_count":   len(tasks),
            "summary_len":  len(summary),
            "transcript_len": len(transcript),
            "processed_at": datetime.now().isoformat(timespec="seconds"),
        },
    }
