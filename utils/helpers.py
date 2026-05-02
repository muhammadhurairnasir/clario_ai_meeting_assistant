"""
utils/helpers.py
----------------
General-purpose utility helpers for the Clario project.
Extracted / adapted from Clario Project notebook (various cells).
"""

import json
import os
import re
from datetime import datetime
from typing import Any, Dict, List, Optional


# ── JSON helpers ───────────────────────────────────────────────────────────────

def save_json(data: Any, output_path: str, indent: int = 4) -> None:
    """
    Serialise *data* to a JSON file at *output_path*.

    Parent directories are created automatically.

    Parameters
    ----------
    data        : JSON-serialisable object.
    output_path : Destination file path.
    indent      : JSON indentation width.
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=indent, ensure_ascii=False)
    print(f" JSON saved to: {output_path}")


def load_json(input_path: str) -> Any:
    """
    Load and return the JSON content of *input_path*.

    Parameters
    ----------
    input_path : Source file path.

    Returns
    -------
    Parsed Python object.

    Raises
    ------
    FileNotFoundError if the file does not exist.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"JSON file not found: {input_path}")
    with open(input_path, "r", encoding="utf-8") as fh:
        return json.load(fh)


# ── Text helpers ───────────────────────────────────────────────────────────────

def clean_text(text: str) -> str:
    """
    Strip leading/trailing whitespace and collapse internal runs of whitespace
    (including newlines) to single spaces.

    Parameters
    ----------
    text : Raw input string.

    Returns
    -------
    Cleaned string.
    """
    return re.sub(r"\s+", " ", text).strip()


def chunk_text(text: str, max_chars: int = 1000) -> List[str]:
    """
    Split *text* into chunks of at most *max_chars* characters, trying to break
    on sentence boundaries (periods followed by whitespace).

    Parameters
    ----------
    text      : Input text.
    max_chars : Maximum characters per chunk.

    Returns
    -------
    List of text chunks.
    """
    sentences = re.split(r"(?<=\.)\s+", text)
    chunks: List[str] = []
    current = ""
    for sentence in sentences:
        if len(current) + len(sentence) + 1 <= max_chars:
            current = (current + " " + sentence).strip()
        else:
            if current:
                chunks.append(current)
            current = sentence
    if current:
        chunks.append(current)
    return chunks


# ── Date / timestamp helpers ───────────────────────────────────────────────────

def current_timestamp(fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Return the current local time as a formatted string."""
    return datetime.now().strftime(fmt)


def today_date(fmt: str = "%Y-%m-%d") -> str:
    """Return today's date as a formatted string."""
    return datetime.now().strftime(fmt)


# ── Directory helpers ──────────────────────────────────────────────────────────

def ensure_dir(path: str) -> str:
    """
    Create *path* (and any missing parent directories) if it does not exist.

    Parameters
    ----------
    path : Directory path to ensure.

    Returns
    -------
    Absolute path of the directory.
    """
    abs_path = os.path.abspath(path)
    os.makedirs(abs_path, exist_ok=True)
    return abs_path


def list_files(directory: str, extension: Optional[str] = None) -> List[str]:
    """
    Return a sorted list of file paths inside *directory*.

    Parameters
    ----------
    directory : Directory to scan.
    extension : If given (e.g. ``'.mp3'``), filter by file extension.

    Returns
    -------
    Sorted list of absolute file paths.
    """
    if not os.path.isdir(directory):
        return []
    files = [
        os.path.join(directory, f)
        for f in os.listdir(directory)
        if os.path.isfile(os.path.join(directory, f))
    ]
    if extension:
        ext = extension if extension.startswith(".") else f".{extension}"
        files = [f for f in files if f.lower().endswith(ext.lower())]
    return sorted(files)
