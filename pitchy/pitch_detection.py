"""Pitch detection module using librosa."""

import numpy as np
import librosa


def load_audio(file_path: str, sr: int = 22050) -> tuple[np.ndarray, int]:
    """
    Load an audio file.

    Args:
        file_path: Path to the audio file (WAV, MP3, etc.)
        sr: Target sample rate (default 22050 Hz)

    Returns:
        Tuple of (audio samples, sample rate)
    """
    y, sr = librosa.load(file_path, sr=sr)
    return y, sr


def detect_pitches(
    y: np.ndarray,
    sr: int,
    fmin: float = 65.0,
    fmax: float = 1000.0,
    frame_length: int = 2048,
    hop_length: int = 512,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Detect pitches in audio using the pyin algorithm.

    The pyin algorithm is well-suited for monophonic pitch tracking,
    making it ideal for sung melodies.

    Args:
        y: Audio time series
        sr: Sample rate
        fmin: Minimum frequency to detect (default 65 Hz, ~C2)
        fmax: Maximum frequency to detect (default 1000 Hz, ~B5)
        frame_length: Length of the analysis frame
        hop_length: Number of samples between frames

    Returns:
        Tuple of (frequencies, voiced_flags, voiced_probabilities)
        - frequencies: Estimated fundamental frequencies (Hz), NaN for unvoiced
        - voiced_flags: Boolean array indicating voiced frames
        - voiced_probs: Probability of each frame being voiced
    """
    f0, voiced_flag, voiced_probs = librosa.pyin(
        y,
        sr=sr,
        fmin=fmin,
        fmax=fmax,
        frame_length=frame_length,
        hop_length=hop_length,
    )
    return f0, voiced_flag, voiced_probs


def get_stable_pitches(
    frequencies: np.ndarray,
    voiced_probs: np.ndarray,
    min_confidence: float = 0.8,
) -> np.ndarray:
    """
    Filter pitches to only include confident detections.

    Args:
        frequencies: Array of detected frequencies
        voiced_probs: Probability of each frame being voiced
        min_confidence: Minimum confidence threshold (0-1)

    Returns:
        Filtered frequencies array (low confidence replaced with NaN)
    """
    filtered = frequencies.copy()
    filtered[voiced_probs < min_confidence] = np.nan
    return filtered
