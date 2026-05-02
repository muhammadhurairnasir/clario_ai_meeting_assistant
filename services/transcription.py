"""
services/transcription.py
--------------------------
Whisper-based audio-to-text transcription service.
Extracted from Clario Project notebook (cells 105, 107, 113-114).
"""

import os

# Module-level model cache (loaded once per process)
_whisper_model = None


def load_whisper(model_size: str = "base"):
    """
    Load (or return cached) Whisper model.

    Parameters
    ----------
    model_size : One of 'tiny', 'base', 'small', 'medium', 'large'.
                 'base' is a good balance of speed and accuracy.

    Returns
    -------
    whisper.model.Whisper
    """
    global _whisper_model
    if _whisper_model is None:
        import whisper
        print(f"Loading Whisper '{model_size}' model ...")
        _whisper_model = whisper.load_model(model_size)
        print("Whisper model loaded.")
    return _whisper_model


def transcribe_audio(audio_path: str,
                     model_size: str = "base",
                     model=None) -> str:
    """
    Transcribe an audio file to text using Whisper.

    Parameters
    ----------
    audio_path : Absolute path to the audio file (mp3, wav, m4a, ...).
    model_size : Whisper model variant (used only if *model* is None).
    model      : Pre-loaded Whisper model instance (optional).
                 Pass this to avoid reloading the model on every call.

    Returns
    -------
    str - Transcribed text.

    Raises
    ------
    FileNotFoundError if *audio_path* does not exist.
    """
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    if model is None:
        model = load_whisper(model_size)

    print(f"Transcribing: {audio_path}")
    result = model.transcribe(audio_path)
    transcript = result["text"].strip()
    print(f"Transcription complete ({len(transcript)} chars).")
    return transcript


def save_transcript(transcript: str, output_path: str) -> None:
    """
    Persist a transcript string to a plain-text file.

    Parameters
    ----------
    transcript  : The transcribed text to save.
    output_path : Destination file path.
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as fh:
        fh.write(transcript)
    print(f"Transcript saved to: {output_path}")


def load_transcript(transcript_path: str) -> str:
    """
    Load a previously-saved transcript from disk.

    Parameters
    ----------
    transcript_path : Path to the .txt file.

    Returns
    -------
    str
    """
    with open(transcript_path, "r", encoding="utf-8") as fh:
        return fh.read()
