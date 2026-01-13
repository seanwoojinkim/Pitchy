# Pitchy

A lightweight melody transcription tool that detects musical notes from sung melodies.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### GUI Application

Launch the graphical interface for easy file selection and visualization:

```bash
python pitchy_gui.py
```

The GUI provides:
- File browser for selecting audio files
- Adjustable confidence threshold and minimum note duration
- Visual output including:
  - Note sequence display
  - Piano roll visualization
  - Pitch contour graph
- Copy-to-clipboard functionality for detected notes

### Command Line

```bash
# Basic usage
python transcribe.py melody.wav

# Lower confidence threshold for noisier recordings
python transcribe.py recording.mp3 --confidence 0.7

# Show notes without octave numbers
python transcribe.py voice_memo.wav --no-octave

# Verbose output with cents deviation
python transcribe.py melody.wav -v

# Show unique notes used
python transcribe.py melody.wav --show-unique
```

### Python API

```python
from pitchy import transcribe

# Transcribe a melody
result = transcribe("melody.wav")

# Get the note sequence
print(result.get_note_sequence())  # ['C4', 'D4', 'E4', 'F4', 'G4']

# Get notes without octave
print(result.get_note_sequence(include_octave=False))  # ['C', 'D', 'E', 'F', 'G']

# Access individual notes
for note in result.notes:
    print(f"{note.full_name}: {note.frequency:.1f} Hz ({note.cents_deviation:+.0f} cents)")
```

## Options

| Option | Default | Description |
|--------|---------|-------------|
| `--confidence` | 0.8 | Minimum confidence threshold (0-1) |
| `--min-duration` | 50 | Minimum note duration in milliseconds |
| `--no-octave` | False | Omit octave numbers from output |
| `--show-unique` | False | Show unique notes used in the melody |
| `--verbose, -v` | False | Show detailed output with cents deviation |

## Supported Formats

- WAV
- MP3
- FLAC
- OGG
- And other formats supported by libsndfile

## Visualization API

Create visualizations programmatically:

```python
from pitchy import transcribe, create_piano_roll, create_pitch_contour, create_combined_visualization
import matplotlib.pyplot as plt

result = transcribe("melody.wav")

# Piano roll view
fig, ax = create_piano_roll(result)
plt.show()

# Pitch contour
fig, ax = create_pitch_contour(result)
plt.show()

# Combined visualization (note sequence + piano roll + pitch contour)
fig, axes = create_combined_visualization(result)
plt.show()
```
