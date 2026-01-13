# Pitchy

A lightweight melody transcription tool that detects musical notes from sung melodies.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

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
