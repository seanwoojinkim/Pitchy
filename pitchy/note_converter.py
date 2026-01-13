"""Convert frequencies to musical note names."""

import math
from dataclasses import dataclass

# A4 = 440 Hz is the standard reference pitch
A4_FREQ = 440.0
A4_MIDI = 69

# Note names in chromatic order
NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


@dataclass
class Note:
    """Represents a musical note."""

    name: str
    octave: int
    frequency: float
    cents_deviation: float

    def __str__(self) -> str:
        return f"{self.name}{self.octave}"

    @property
    def full_name(self) -> str:
        """Return note name with octave."""
        return f"{self.name}{self.octave}"

    @property
    def with_cents(self) -> str:
        """Return note name with cents deviation."""
        sign = "+" if self.cents_deviation >= 0 else ""
        return f"{self.name}{self.octave} ({sign}{self.cents_deviation:.0f}c)"


def freq_to_midi(freq: float) -> float:
    """
    Convert frequency in Hz to MIDI note number.

    Args:
        freq: Frequency in Hz

    Returns:
        MIDI note number (can be fractional)
    """
    if freq <= 0:
        return float("nan")
    return 12 * math.log2(freq / A4_FREQ) + A4_MIDI


def midi_to_note(midi_num: float) -> Note | None:
    """
    Convert MIDI note number to Note object.

    Args:
        midi_num: MIDI note number (can be fractional)

    Returns:
        Note object or None if invalid
    """
    if math.isnan(midi_num):
        return None

    # Round to nearest semitone
    rounded_midi = round(midi_num)
    cents_deviation = (midi_num - rounded_midi) * 100

    # Calculate note name and octave
    note_index = rounded_midi % 12
    octave = (rounded_midi // 12) - 1

    # Calculate the exact frequency of the rounded note
    exact_freq = A4_FREQ * (2 ** ((rounded_midi - A4_MIDI) / 12))

    return Note(
        name=NOTE_NAMES[note_index],
        octave=octave,
        frequency=exact_freq,
        cents_deviation=cents_deviation,
    )


def freq_to_note(freq: float) -> Note | None:
    """
    Convert frequency in Hz to a Note object.

    Args:
        freq: Frequency in Hz

    Returns:
        Note object or None if frequency is invalid
    """
    if freq <= 0 or math.isnan(freq):
        return None
    midi_num = freq_to_midi(freq)
    return midi_to_note(midi_num)


def freq_to_note_name(freq: float, include_octave: bool = True) -> str | None:
    """
    Convert frequency in Hz to note name string.

    Args:
        freq: Frequency in Hz
        include_octave: Whether to include octave number

    Returns:
        Note name string (e.g., "C4", "F#5") or None if invalid
    """
    note = freq_to_note(freq)
    if note is None:
        return None
    return note.full_name if include_octave else note.name
