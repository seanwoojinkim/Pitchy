"""Pitchy - A lightweight melody transcription tool."""

from .transcriber import transcribe, TranscriptionResult
from .note_converter import Note, freq_to_note, freq_to_note_name
from .pitch_detection import load_audio, detect_pitches
from .visualization import (
    create_piano_roll,
    create_pitch_contour,
    create_note_sequence_display,
    create_combined_visualization,
)
from .gui import run_gui

__version__ = "0.1.0"
__all__ = [
    "transcribe",
    "TranscriptionResult",
    "Note",
    "freq_to_note",
    "freq_to_note_name",
    "load_audio",
    "detect_pitches",
    "create_piano_roll",
    "create_pitch_contour",
    "create_note_sequence_display",
    "create_combined_visualization",
    "run_gui",
]
