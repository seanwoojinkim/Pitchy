"""Main melody transcription module."""

import numpy as np
from dataclasses import dataclass, field

from .pitch_detection import load_audio, detect_pitches, get_stable_pitches
from .note_converter import freq_to_note, Note


@dataclass
class TranscriptionResult:
    """Result of melody transcription."""

    notes: list[Note]
    unique_notes: list[str]
    raw_frequencies: np.ndarray = field(repr=False)

    def get_note_sequence(self, include_octave: bool = True) -> list[str]:
        """Get the sequence of note names."""
        if include_octave:
            return [n.full_name for n in self.notes]
        return [n.name for n in self.notes]

    def get_note_sequence_string(self, include_octave: bool = True) -> str:
        """Get notes as a comma-separated string."""
        return ", ".join(self.get_note_sequence(include_octave))


def transcribe(
    audio_path: str,
    min_confidence: float = 0.8,
    min_note_duration_ms: float = 50.0,
    sample_rate: int = 22050,
    hop_length: int = 512,
) -> TranscriptionResult:
    """
    Transcribe a melody from an audio file.

    Args:
        audio_path: Path to the audio file (WAV, MP3, etc.)
        min_confidence: Minimum confidence for pitch detection (0-1)
        min_note_duration_ms: Minimum duration for a note to be included (ms)
        sample_rate: Sample rate for audio processing
        hop_length: Hop length for pitch detection

    Returns:
        TranscriptionResult containing detected notes
    """
    # Load audio
    y, sr = load_audio(audio_path, sr=sample_rate)

    # Detect pitches
    frequencies, voiced_flags, voiced_probs = detect_pitches(
        y, sr, hop_length=hop_length
    )

    # Filter by confidence
    stable_freqs = get_stable_pitches(frequencies, voiced_probs, min_confidence)

    # Convert to notes and remove consecutive duplicates
    notes = _frequencies_to_notes(stable_freqs, sr, hop_length, min_note_duration_ms)

    # Get unique notes (preserving order of first occurrence)
    seen = set()
    unique_notes = []
    for note in notes:
        if note.full_name not in seen:
            seen.add(note.full_name)
            unique_notes.append(note.full_name)

    return TranscriptionResult(
        notes=notes,
        unique_notes=unique_notes,
        raw_frequencies=stable_freqs,
    )


def _frequencies_to_notes(
    frequencies: np.ndarray,
    sr: int,
    hop_length: int,
    min_duration_ms: float,
) -> list[Note]:
    """
    Convert frequency array to a list of notes, merging consecutive same notes.

    Args:
        frequencies: Array of detected frequencies
        sr: Sample rate
        hop_length: Hop length used in pitch detection
        min_duration_ms: Minimum note duration in milliseconds

    Returns:
        List of Note objects
    """
    # Calculate frame duration
    frame_duration_ms = (hop_length / sr) * 1000
    min_frames = max(1, int(min_duration_ms / frame_duration_ms))

    notes = []
    current_note = None
    current_count = 0

    for freq in frequencies:
        note = freq_to_note(freq)

        if note is None:
            # End of a note
            if current_note is not None and current_count >= min_frames:
                notes.append(current_note)
            current_note = None
            current_count = 0
        elif current_note is None:
            # Start of a new note
            current_note = note
            current_count = 1
        elif note.full_name == current_note.full_name:
            # Same note continues
            current_count += 1
        else:
            # Different note
            if current_count >= min_frames:
                notes.append(current_note)
            current_note = note
            current_count = 1

    # Don't forget the last note
    if current_note is not None and current_count >= min_frames:
        notes.append(current_note)

    return notes
