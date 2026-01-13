#!/usr/bin/env python3
"""CLI for Pitchy melody transcription tool."""

import argparse
import sys

from pitchy import transcribe


def main():
    parser = argparse.ArgumentParser(
        description="Transcribe a sung melody to musical notes.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python transcribe.py melody.wav
  python transcribe.py recording.mp3 --confidence 0.7
  python transcribe.py voice_memo.wav --no-octave
        """,
    )
    parser.add_argument(
        "audio_file",
        help="Path to the audio file (WAV, MP3, etc.)",
    )
    parser.add_argument(
        "--confidence",
        type=float,
        default=0.8,
        help="Minimum confidence threshold (0-1, default: 0.8)",
    )
    parser.add_argument(
        "--min-duration",
        type=float,
        default=50.0,
        help="Minimum note duration in milliseconds (default: 50)",
    )
    parser.add_argument(
        "--no-octave",
        action="store_true",
        help="Omit octave numbers from output",
    )
    parser.add_argument(
        "--show-unique",
        action="store_true",
        help="Also show unique notes used in the melody",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed output including cents deviation",
    )

    args = parser.parse_args()

    try:
        result = transcribe(
            args.audio_file,
            min_confidence=args.confidence,
            min_note_duration_ms=args.min_duration,
        )
    except FileNotFoundError:
        print(f"Error: File not found: {args.audio_file}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error processing audio: {e}", file=sys.stderr)
        sys.exit(1)

    if not result.notes:
        print("No notes detected. Try lowering the --confidence threshold.")
        sys.exit(0)

    include_octave = not args.no_octave

    print(f"Detected {len(result.notes)} notes:\n")

    if args.verbose:
        for i, note in enumerate(result.notes, 1):
            print(f"  {i:3d}. {note.with_cents}")
    else:
        note_sequence = result.get_note_sequence(include_octave)
        print("  " + ", ".join(note_sequence))

    if args.show_unique:
        print(f"\nUnique notes ({len(result.unique_notes)}):")
        print("  " + ", ".join(result.unique_notes))

    print()


if __name__ == "__main__":
    main()
