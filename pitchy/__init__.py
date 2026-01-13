"""Pitchy - A lightweight melody transcription tool."""

from .transcriber import transcribe, TranscriptionResult
from .note_converter import Note, freq_to_note, freq_to_note_name
from .pitch_detection import load_audio, detect_pitches

__version__ = "0.1.0"
__all__ = [
    "transcribe",
    "TranscriptionResult",
    "Note",
    "freq_to_note",
    "freq_to_note_name",
    "load_audio",
    "detect_pitches",
]
