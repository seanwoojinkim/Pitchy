"""GUI module for Pitchy melody transcription tool."""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from .transcriber import transcribe, TranscriptionResult
from .visualization import create_combined_visualization


class PitchyApp:
    """Main GUI application for Pitchy."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Pitchy - Melody Transcription Tool")
        self.root.geometry("1200x800")
        self.root.minsize(900, 600)

        self.audio_path: str | None = None
        self.result: TranscriptionResult | None = None

        self._setup_styles()
        self._create_widgets()

    def _setup_styles(self) -> None:
        """Configure ttk styles."""
        style = ttk.Style()
        style.configure("Header.TLabel", font=("Helvetica", 16, "bold"))
        style.configure("Status.TLabel", font=("Helvetica", 10))
        style.configure("Big.TButton", font=("Helvetica", 11), padding=10)

    def _create_widgets(self) -> None:
        """Create all GUI widgets."""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)

        # Header
        header = ttk.Label(
            main_frame,
            text="Pitchy - Melody Transcription",
            style="Header.TLabel",
        )
        header.grid(row=0, column=0, pady=(0, 10), sticky="w")

        # Control panel
        self._create_control_panel(main_frame)

        # Visualization area
        self._create_visualization_area(main_frame)

        # Results panel
        self._create_results_panel(main_frame)

    def _create_control_panel(self, parent: ttk.Frame) -> None:
        """Create the control panel with file selection and parameters."""
        control_frame = ttk.LabelFrame(parent, text="Controls", padding="10")
        control_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        control_frame.columnconfigure(1, weight=1)

        # File selection row
        ttk.Label(control_frame, text="Audio File:").grid(row=0, column=0, sticky="w", padx=(0, 10))

        self.file_var = tk.StringVar(value="No file selected")
        file_label = ttk.Label(control_frame, textvariable=self.file_var, width=50)
        file_label.grid(row=0, column=1, sticky="w")

        browse_btn = ttk.Button(control_frame, text="Browse...", command=self._browse_file)
        browse_btn.grid(row=0, column=2, padx=(10, 0))

        # Parameters row
        param_frame = ttk.Frame(control_frame)
        param_frame.grid(row=1, column=0, columnspan=3, sticky="w", pady=(15, 0))

        # Confidence slider
        ttk.Label(param_frame, text="Confidence:").grid(row=0, column=0, sticky="w")
        self.confidence_var = tk.DoubleVar(value=0.8)
        confidence_slider = ttk.Scale(
            param_frame,
            from_=0.3,
            to=1.0,
            variable=self.confidence_var,
            orient="horizontal",
            length=150,
        )
        confidence_slider.grid(row=0, column=1, padx=(5, 5))
        self.confidence_label = ttk.Label(param_frame, text="0.80")
        self.confidence_label.grid(row=0, column=2)
        confidence_slider.configure(command=self._update_confidence_label)

        # Min duration
        ttk.Label(param_frame, text="Min Duration (ms):").grid(row=0, column=3, sticky="w", padx=(30, 0))
        self.duration_var = tk.IntVar(value=50)
        duration_spin = ttk.Spinbox(
            param_frame,
            from_=10,
            to=500,
            textvariable=self.duration_var,
            width=6,
        )
        duration_spin.grid(row=0, column=4, padx=(5, 0))

        # Transcribe button
        self.transcribe_btn = ttk.Button(
            param_frame,
            text="Transcribe",
            style="Big.TButton",
            command=self._transcribe,
        )
        self.transcribe_btn.grid(row=0, column=5, padx=(40, 0))

        # Status
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(
            control_frame,
            textvariable=self.status_var,
            style="Status.TLabel",
        )
        status_label.grid(row=2, column=0, columnspan=3, sticky="w", pady=(10, 0))

    def _create_visualization_area(self, parent: ttk.Frame) -> None:
        """Create the matplotlib visualization area."""
        viz_frame = ttk.LabelFrame(parent, text="Visualization", padding="5")
        viz_frame.grid(row=2, column=0, sticky="nsew", pady=(0, 10))
        viz_frame.columnconfigure(0, weight=1)
        viz_frame.rowconfigure(0, weight=1)

        # Create initial empty figure
        self.figure = Figure(figsize=(12, 6), dpi=100)
        self.figure.text(
            0.5, 0.5,
            "Load an audio file and click Transcribe to see results",
            ha="center", va="center", fontsize=12, color="gray",
        )

        # Canvas for matplotlib
        self.canvas = FigureCanvasTkAgg(self.figure, master=viz_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")

        # Toolbar
        toolbar_frame = ttk.Frame(viz_frame)
        toolbar_frame.grid(row=1, column=0, sticky="ew")
        self.toolbar = NavigationToolbar2Tk(self.canvas, toolbar_frame)
        self.toolbar.update()

    def _create_results_panel(self, parent: ttk.Frame) -> None:
        """Create the results text panel."""
        results_frame = ttk.LabelFrame(parent, text="Detected Notes", padding="10")
        results_frame.grid(row=3, column=0, sticky="ew")
        results_frame.columnconfigure(0, weight=1)

        # Notes text display
        self.notes_text = tk.Text(
            results_frame,
            height=3,
            wrap="word",
            font=("Courier", 11),
        )
        self.notes_text.grid(row=0, column=0, sticky="ew")
        self.notes_text.insert("1.0", "Notes will appear here after transcription...")
        self.notes_text.configure(state="disabled")

        # Copy button
        copy_btn = ttk.Button(
            results_frame,
            text="Copy to Clipboard",
            command=self._copy_notes,
        )
        copy_btn.grid(row=0, column=1, padx=(10, 0), sticky="n")

    def _update_confidence_label(self, value: str) -> None:
        """Update confidence label when slider changes."""
        self.confidence_label.configure(text=f"{float(value):.2f}")

    def _browse_file(self) -> None:
        """Open file browser to select audio file."""
        filetypes = [
            ("Audio files", "*.wav *.mp3 *.flac *.ogg *.m4a"),
            ("WAV files", "*.wav"),
            ("MP3 files", "*.mp3"),
            ("All files", "*.*"),
        ]

        filepath = filedialog.askopenfilename(
            title="Select Audio File",
            filetypes=filetypes,
        )

        if filepath:
            self.audio_path = filepath
            filename = Path(filepath).name
            self.file_var.set(filename)
            self.status_var.set(f"Loaded: {filename}")

    def _transcribe(self) -> None:
        """Run transcription on the selected audio file."""
        if not self.audio_path:
            messagebox.showwarning("No File", "Please select an audio file first.")
            return

        self.status_var.set("Transcribing...")
        self.transcribe_btn.configure(state="disabled")
        self.root.update()

        try:
            self.result = transcribe(
                self.audio_path,
                min_confidence=self.confidence_var.get(),
                min_note_duration_ms=float(self.duration_var.get()),
            )

            self._update_visualization()
            self._update_notes_display()

            n_notes = len(self.result.notes)
            self.status_var.set(f"Transcription complete: {n_notes} notes detected")

        except Exception as e:
            messagebox.showerror("Error", f"Transcription failed:\n{str(e)}")
            self.status_var.set("Error during transcription")

        finally:
            self.transcribe_btn.configure(state="normal")

    def _update_visualization(self) -> None:
        """Update the visualization with transcription results."""
        if self.result is None:
            return

        # Clear old figure
        self.figure.clear()

        # Create new visualization
        fig, axes = create_combined_visualization(self.result, figsize=(12, 8))

        # Copy content to our figure
        self.figure.clear()
        for i, ax_src in enumerate(axes):
            ax_dst = self.figure.add_subplot(3, 1, i + 1)

            # Copy the axes content by recreating it
            if i == 0:
                self._redraw_note_sequence(ax_dst)
            elif i == 1:
                self._redraw_piano_roll(ax_dst)
            else:
                self._redraw_pitch_contour(ax_dst)

        plt.close(fig)  # Close the temporary figure

        self.figure.tight_layout()
        self.canvas.draw()

    def _redraw_note_sequence(self, ax) -> None:
        """Redraw note sequence on the given axes."""
        from .visualization import _draw_note_sequence
        _draw_note_sequence(ax, self.result)

    def _redraw_piano_roll(self, ax) -> None:
        """Redraw piano roll on the given axes."""
        from .visualization import _draw_piano_roll
        _draw_piano_roll(ax, self.result)

    def _redraw_pitch_contour(self, ax) -> None:
        """Redraw pitch contour on the given axes."""
        from .visualization import _draw_pitch_contour
        _draw_pitch_contour(ax, self.result, sr=22050, hop_length=512)

    def _update_notes_display(self) -> None:
        """Update the notes text display."""
        if self.result is None:
            return

        self.notes_text.configure(state="normal")
        self.notes_text.delete("1.0", "end")

        if self.result.notes:
            note_str = self.result.get_note_sequence_string(include_octave=True)
            self.notes_text.insert("1.0", note_str)
        else:
            self.notes_text.insert("1.0", "No notes detected. Try lowering the confidence threshold.")

        self.notes_text.configure(state="disabled")

    def _copy_notes(self) -> None:
        """Copy detected notes to clipboard."""
        if self.result is None or not self.result.notes:
            messagebox.showinfo("No Notes", "No notes to copy.")
            return

        note_str = self.result.get_note_sequence_string(include_octave=True)
        self.root.clipboard_clear()
        self.root.clipboard_append(note_str)
        self.status_var.set("Notes copied to clipboard!")


def run_gui() -> None:
    """Launch the Pitchy GUI application."""
    root = tk.Tk()
    app = PitchyApp(root)
    root.mainloop()


if __name__ == "__main__":
    run_gui()
