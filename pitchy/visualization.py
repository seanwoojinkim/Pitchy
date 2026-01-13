"""Visualization module for melody transcription results."""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.figure import Figure
from matplotlib.axes import Axes

from .note_converter import NOTE_NAMES, freq_to_midi
from .transcriber import TranscriptionResult


def create_piano_roll(
    result: TranscriptionResult,
    figsize: tuple[int, int] = (12, 6),
) -> tuple[Figure, Axes]:
    """
    Create a piano roll visualization of detected notes.

    Args:
        result: TranscriptionResult from transcription
        figsize: Figure size (width, height)

    Returns:
        Tuple of (Figure, Axes)
    """
    fig, ax = plt.subplots(figsize=figsize)

    if not result.notes:
        ax.text(
            0.5, 0.5, "No notes detected",
            ha="center", va="center", fontsize=14,
            transform=ax.transAxes
        )
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        return fig, ax

    # Get MIDI numbers for y-axis positioning
    midi_numbers = [freq_to_midi(n.frequency) for n in result.notes]
    min_midi = int(min(midi_numbers)) - 2
    max_midi = int(max(midi_numbers)) + 2

    # Color palette for notes
    colors = plt.cm.Set3(np.linspace(0, 1, 12))

    # Draw note rectangles
    for i, note in enumerate(result.notes):
        midi_num = round(freq_to_midi(note.frequency))
        note_color = colors[midi_num % 12]

        rect = Rectangle(
            (i, midi_num - 0.4),
            width=0.8,
            height=0.8,
            facecolor=note_color,
            edgecolor="black",
            linewidth=1,
        )
        ax.add_patch(rect)

        # Add note label
        ax.text(
            i + 0.4, midi_num,
            note.full_name,
            ha="center", va="center",
            fontsize=9, fontweight="bold",
        )

    # Configure axes
    ax.set_xlim(-0.5, len(result.notes) - 0.5)
    ax.set_ylim(min_midi, max_midi)

    ax.set_xlabel("Note Sequence", fontsize=12)
    ax.set_ylabel("Pitch", fontsize=12)
    ax.set_title("Detected Melody - Piano Roll View", fontsize=14, fontweight="bold")

    # Create y-axis labels with note names
    y_ticks = range(min_midi, max_midi + 1)
    y_labels = []
    for midi in y_ticks:
        note_name = NOTE_NAMES[midi % 12]
        octave = (midi // 12) - 1
        y_labels.append(f"{note_name}{octave}")

    ax.set_yticks(list(y_ticks))
    ax.set_yticklabels(y_labels)

    # Add grid
    ax.grid(True, axis="y", alpha=0.3, linestyle="--")
    ax.set_axisbelow(True)

    plt.tight_layout()
    return fig, ax


def create_pitch_contour(
    result: TranscriptionResult,
    sr: int = 22050,
    hop_length: int = 512,
    figsize: tuple[int, int] = (12, 4),
) -> tuple[Figure, Axes]:
    """
    Create a pitch contour visualization showing frequencies over time.

    Args:
        result: TranscriptionResult from transcription
        sr: Sample rate used in analysis
        hop_length: Hop length used in analysis
        figsize: Figure size (width, height)

    Returns:
        Tuple of (Figure, Axes)
    """
    fig, ax = plt.subplots(figsize=figsize)

    frequencies = result.raw_frequencies
    if len(frequencies) == 0:
        ax.text(
            0.5, 0.5, "No pitch data",
            ha="center", va="center", fontsize=14,
            transform=ax.transAxes
        )
        return fig, ax

    # Calculate time axis
    times = np.arange(len(frequencies)) * hop_length / sr

    # Plot the pitch contour
    ax.plot(times, frequencies, "b-", linewidth=1.5, alpha=0.7, label="Detected pitch")

    # Mark detected notes
    valid_freqs = frequencies[~np.isnan(frequencies)]
    if len(valid_freqs) > 0:
        ax.scatter(
            times[~np.isnan(frequencies)],
            valid_freqs,
            c="blue", s=10, alpha=0.5,
        )

    ax.set_xlabel("Time (seconds)", fontsize=12)
    ax.set_ylabel("Frequency (Hz)", fontsize=12)
    ax.set_title("Pitch Contour", fontsize=14, fontweight="bold")

    # Add reference lines for detected notes
    if result.notes:
        unique_freqs = sorted(set(n.frequency for n in result.notes))
        for freq in unique_freqs:
            note = next(n for n in result.notes if n.frequency == freq)
            ax.axhline(y=freq, color="red", linestyle="--", alpha=0.3)
            ax.text(
                times[-1] * 1.01, freq, note.full_name,
                va="center", fontsize=9, color="red",
            )

    ax.set_xlim(0, times[-1] if len(times) > 0 else 1)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    return fig, ax


def create_note_sequence_display(
    result: TranscriptionResult,
    figsize: tuple[int, int] = (12, 2),
) -> tuple[Figure, Axes]:
    """
    Create a simple horizontal display of the note sequence.

    Args:
        result: TranscriptionResult from transcription
        figsize: Figure size (width, height)

    Returns:
        Tuple of (Figure, Axes)
    """
    fig, ax = plt.subplots(figsize=figsize)

    if not result.notes:
        ax.text(
            0.5, 0.5, "No notes detected",
            ha="center", va="center", fontsize=14,
            transform=ax.transAxes
        )
        ax.axis("off")
        return fig, ax

    # Color palette
    colors = plt.cm.Set3(np.linspace(0, 1, 12))

    n_notes = len(result.notes)
    box_width = 1.0

    for i, note in enumerate(result.notes):
        midi_num = round(freq_to_midi(note.frequency))
        note_color = colors[midi_num % 12]

        rect = Rectangle(
            (i * box_width, 0),
            width=box_width * 0.9,
            height=1,
            facecolor=note_color,
            edgecolor="black",
            linewidth=1,
        )
        ax.add_patch(rect)

        ax.text(
            i * box_width + box_width * 0.45, 0.5,
            note.full_name,
            ha="center", va="center",
            fontsize=10, fontweight="bold",
        )

    ax.set_xlim(-0.2, n_notes * box_width + 0.2)
    ax.set_ylim(-0.2, 1.2)
    ax.axis("off")
    ax.set_title(
        f"Note Sequence ({n_notes} notes)",
        fontsize=12, fontweight="bold", pad=10,
    )

    plt.tight_layout()
    return fig, ax


def create_combined_visualization(
    result: TranscriptionResult,
    sr: int = 22050,
    hop_length: int = 512,
    figsize: tuple[int, int] = (14, 10),
) -> tuple[Figure, list[Axes]]:
    """
    Create a combined visualization with piano roll and pitch contour.

    Args:
        result: TranscriptionResult from transcription
        sr: Sample rate used in analysis
        hop_length: Hop length used in analysis
        figsize: Figure size (width, height)

    Returns:
        Tuple of (Figure, list of Axes)
    """
    fig = plt.figure(figsize=figsize)

    # Create grid layout
    gs = fig.add_gridspec(3, 1, height_ratios=[1, 2, 2], hspace=0.3)

    # Note sequence (top)
    ax1 = fig.add_subplot(gs[0])
    _draw_note_sequence(ax1, result)

    # Piano roll (middle)
    ax2 = fig.add_subplot(gs[1])
    _draw_piano_roll(ax2, result)

    # Pitch contour (bottom)
    ax3 = fig.add_subplot(gs[2])
    _draw_pitch_contour(ax3, result, sr, hop_length)

    plt.tight_layout()
    return fig, [ax1, ax2, ax3]


def _draw_note_sequence(ax: Axes, result: TranscriptionResult) -> None:
    """Draw note sequence on given axes."""
    if not result.notes:
        ax.text(0.5, 0.5, "No notes detected", ha="center", va="center", fontsize=14, transform=ax.transAxes)
        ax.axis("off")
        return

    colors = plt.cm.Set3(np.linspace(0, 1, 12))
    n_notes = len(result.notes)

    for i, note in enumerate(result.notes):
        midi_num = round(freq_to_midi(note.frequency))
        rect = Rectangle((i, 0), 0.9, 1, facecolor=colors[midi_num % 12], edgecolor="black")
        ax.add_patch(rect)
        ax.text(i + 0.45, 0.5, note.full_name, ha="center", va="center", fontsize=9, fontweight="bold")

    ax.set_xlim(-0.2, n_notes + 0.2)
    ax.set_ylim(-0.1, 1.1)
    ax.axis("off")
    ax.set_title(f"Note Sequence ({n_notes} notes)", fontsize=11, fontweight="bold")


def _draw_piano_roll(ax: Axes, result: TranscriptionResult) -> None:
    """Draw piano roll on given axes."""
    if not result.notes:
        ax.text(0.5, 0.5, "No notes detected", ha="center", va="center", fontsize=14, transform=ax.transAxes)
        return

    midi_numbers = [freq_to_midi(n.frequency) for n in result.notes]
    min_midi = int(min(midi_numbers)) - 2
    max_midi = int(max(midi_numbers)) + 2
    colors = plt.cm.Set3(np.linspace(0, 1, 12))

    for i, note in enumerate(result.notes):
        midi_num = round(freq_to_midi(note.frequency))
        rect = Rectangle((i, midi_num - 0.4), 0.8, 0.8, facecolor=colors[midi_num % 12], edgecolor="black")
        ax.add_patch(rect)
        ax.text(i + 0.4, midi_num, note.full_name, ha="center", va="center", fontsize=8, fontweight="bold")

    ax.set_xlim(-0.5, len(result.notes) - 0.5)
    ax.set_ylim(min_midi, max_midi)
    ax.set_xlabel("Note Sequence")
    ax.set_ylabel("Pitch")
    ax.set_title("Piano Roll View", fontsize=11, fontweight="bold")

    y_ticks = range(min_midi, max_midi + 1)
    ax.set_yticks(list(y_ticks))
    ax.set_yticklabels([f"{NOTE_NAMES[m % 12]}{(m // 12) - 1}" for m in y_ticks])
    ax.grid(True, axis="y", alpha=0.3, linestyle="--")


def _draw_pitch_contour(ax: Axes, result: TranscriptionResult, sr: int, hop_length: int) -> None:
    """Draw pitch contour on given axes."""
    frequencies = result.raw_frequencies
    if len(frequencies) == 0:
        ax.text(0.5, 0.5, "No pitch data", ha="center", va="center", fontsize=14, transform=ax.transAxes)
        return

    times = np.arange(len(frequencies)) * hop_length / sr
    ax.plot(times, frequencies, "b-", linewidth=1.5, alpha=0.7)

    valid_mask = ~np.isnan(frequencies)
    if np.any(valid_mask):
        ax.scatter(times[valid_mask], frequencies[valid_mask], c="blue", s=8, alpha=0.4)

    ax.set_xlabel("Time (seconds)")
    ax.set_ylabel("Frequency (Hz)")
    ax.set_title("Pitch Contour", fontsize=11, fontweight="bold")
    ax.set_xlim(0, times[-1] if len(times) > 0 else 1)
    ax.grid(True, alpha=0.3)
