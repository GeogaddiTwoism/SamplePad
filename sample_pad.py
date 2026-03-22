import tkinter as tk
from tkinter import filedialog, ttk
import numpy as np
import soundfile as sf
import pygame
import os
import io
import threading
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# --- Constants ---
PAD_KEYS = [
    ["e", "r", "t", "y"],
    ["d", "f", "g", "h"],
    ["c", "v", "b", "n"],
]
PAD_COLORS = {
    "empty": "#2a2a2a",
    "loaded": "#3a5f3a",
    "selected": "#5a8f5a",
    "playing": "#ff8844",
}
BG_COLOR = "#1a1a1a"
TEXT_COLOR = "#cccccc"
ACCENT_COLOR = "#4a9eff"


class Pad:
    def __init__(self, key):
        self.key = key
        self.file_path = None
        self.audio_data = None
        self.sample_rate = None
        self.start = 0.0  # normalized 0-1
        self.end = 1.0    # normalized 0-1
        self.name = ""
        self.tune = 0.0   # semitones, -12 to +12

    @property
    def loaded(self):
        return self.audio_data is not None

    def load(self, path):
        data, sr = sf.read(path, dtype="float32", always_2d=True)
        # Mix to mono for display, keep original for playback
        self.audio_data = data
        self.sample_rate = sr
        self.file_path = path
        self.name = os.path.splitext(os.path.basename(path))[0]
        self.start = 0.0
        self.end = 1.0
        self.tune = 0.0

    def get_chopped(self):
        if self.audio_data is None:
            return None, None
        n = len(self.audio_data)
        s = int(self.start * n)
        e = int(self.end * n)
        if s >= e:
            e = min(s + 1, n)
        return self.audio_data[s:e], self.sample_rate

    def get_mono(self):
        if self.audio_data is None:
            return None
        return np.mean(self.audio_data, axis=1)


class SamplePadApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sample Pad")
        self.root.configure(bg=BG_COLOR)
        self.root.minsize(800, 700)

        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        # Reserve a dedicated channel per pad so retriggering stops previous playback
        pygame.mixer.set_num_channels(12)

        # Build pad data
        self.pads = {}
        self.pad_buttons = {}
        self.pad_channels = {}
        self.selected_key = None

        ch_index = 0
        for row in PAD_KEYS:
            for key in row:
                self.pads[key] = Pad(key)
                self.pad_channels[key] = pygame.mixer.Channel(ch_index)
                ch_index += 1

        self._build_ui()
        self._bind_keys()

        # Select first pad by default
        self._select_pad("e")

    # ---- UI ----
    def _build_ui(self):
        # Top label
        title = tk.Label(
            self.root, text="SAMPLE PAD", font=("Consolas", 18, "bold"),
            bg=BG_COLOR, fg=ACCENT_COLOR,
        )
        title.pack(pady=(10, 5))

        hint = tk.Label(
            self.root,
            text="Click a pad or press its key to play  |  Select + Enter to load a sample",
            font=("Consolas", 9), bg=BG_COLOR, fg="#666666",
        )
        hint.pack(pady=(0, 8))

        # Pad grid
        grid_frame = tk.Frame(self.root, bg=BG_COLOR)
        grid_frame.pack(pady=5)

        for r, row in enumerate(PAD_KEYS):
            for c, key in enumerate(row):
                # Wrap each button in a frame that acts as a visible selection border
                border = tk.Frame(
                    grid_frame, bg=BG_COLOR, bd=0,
                    highlightthickness=3, highlightbackground=BG_COLOR,
                )
                border.grid(row=r, column=c, padx=3, pady=3)
                btn = tk.Button(
                    border, text=key.upper(), width=10, height=3,
                    font=("Consolas", 14, "bold"),
                    bg=PAD_COLORS["empty"], fg=TEXT_COLOR,
                    activebackground="#444444", activeforeground="white",
                    relief="flat", bd=0,
                    command=lambda k=key: self._on_pad_click(k),
                )
                btn.pack()
                self.pad_buttons[key] = btn
                btn._border_frame = border  # store ref for selection styling

        # Waveform area
        wave_frame = tk.Frame(self.root, bg=BG_COLOR)
        wave_frame.pack(fill="both", expand=True, padx=15, pady=(10, 5))

        self.fig = Figure(figsize=(7, 2.2), dpi=100, facecolor=BG_COLOR)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor("#222222")
        self._style_axis()

        self.canvas = FigureCanvasTkAgg(self.fig, master=wave_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # Chop controls
        chop_frame = tk.Frame(self.root, bg=BG_COLOR)
        chop_frame.pack(fill="x", padx=20, pady=(0, 12))

        tk.Label(
            chop_frame, text="START", font=("Consolas", 9, "bold"),
            bg=BG_COLOR, fg=TEXT_COLOR,
        ).pack(side="left")

        self.start_var = tk.DoubleVar(value=0.0)
        self.start_slider = ttk.Scale(
            chop_frame, from_=0.0, to=1.0, variable=self.start_var,
            orient="horizontal", command=self._on_chop_change,
        )
        self.start_slider.pack(side="left", fill="x", expand=True, padx=(5, 15))

        tk.Label(
            chop_frame, text="END", font=("Consolas", 9, "bold"),
            bg=BG_COLOR, fg=TEXT_COLOR,
        ).pack(side="left")

        self.end_var = tk.DoubleVar(value=1.0)
        self.end_slider = ttk.Scale(
            chop_frame, from_=0.0, to=1.0, variable=self.end_var,
            orient="horizontal", command=self._on_chop_change,
        )
        self.end_slider.pack(side="left", fill="x", expand=True, padx=(5, 0))

        # Tune control
        tune_frame = tk.Frame(self.root, bg=BG_COLOR)
        tune_frame.pack(fill="x", padx=20, pady=(0, 8))

        tk.Label(
            tune_frame, text="TUNE", font=("Consolas", 9, "bold"),
            bg=BG_COLOR, fg=ACCENT_COLOR,
        ).pack(side="left")

        self.tune_var = tk.DoubleVar(value=0.0)
        self.tune_slider = ttk.Scale(
            tune_frame, from_=-12.0, to=12.0, variable=self.tune_var,
            orient="horizontal", command=self._on_tune_change,
        )
        self.tune_slider.pack(side="left", fill="x", expand=True, padx=(5, 10))

        self.tune_label = tk.Label(
            tune_frame, text="0.00 st", font=("Consolas", 10),
            bg=BG_COLOR, fg=ACCENT_COLOR, width=8, anchor="w",
        )
        self.tune_label.pack(side="left", padx=(0, 10))

        tk.Button(
            tune_frame, text="RESET", font=("Consolas", 8, "bold"),
            bg="#333333", fg=TEXT_COLOR, relief="flat", padx=6,
            command=self._reset_tune,
        ).pack(side="left")

        self.info_label = tk.Label(
            self.root, text="No pad selected", font=("Consolas", 9),
            bg=BG_COLOR, fg="#666666",
        )
        self.info_label.pack(pady=(0, 8))

    def _style_axis(self):
        self.ax.tick_params(colors="#555555", labelsize=7)
        for spine in self.ax.spines.values():
            spine.set_color("#333333")
        self.ax.set_xlabel("Time (s)", fontsize=8, color="#555555")
        self.ax.set_ylabel("Amplitude", fontsize=8, color="#555555")

    # ---- Key bindings ----
    def _bind_keys(self):
        for row in PAD_KEYS:
            for key in row:
                self.root.bind(f"<KeyPress-{key}>", lambda e, k=key: self._on_key_press(k))
                upper = key.upper()
                self.root.bind(f"<KeyPress-{upper}>", lambda e, k=key: self._on_key_press(k))
        self.root.bind("<Return>", self._on_enter)

    def _on_key_press(self, key):
        self._select_pad(key)
        self._play_pad(key)

    def _on_enter(self, event=None):
        if self.selected_key:
            self._load_sample(self.selected_key)

    def _on_pad_click(self, key):
        self._select_pad(key)
        self._play_pad(key)

    # ---- Pad selection ----
    def _select_pad(self, key):
        # Deselect previous
        if self.selected_key and self.selected_key in self.pad_buttons:
            pad = self.pads[self.selected_key]
            color = PAD_COLORS["loaded"] if pad.loaded else PAD_COLORS["empty"]
            btn = self.pad_buttons[self.selected_key]
            btn.configure(bg=color)
            btn._border_frame.configure(highlightbackground=BG_COLOR)

        self.selected_key = key
        self.pad_buttons[key]._border_frame.configure(highlightbackground=ACCENT_COLOR)
        self._update_selected_color()
        self._update_waveform()
        self._sync_sliders()
        self._update_info()

    def _update_selected_color(self):
        if self.selected_key:
            pad = self.pads[self.selected_key]
            color = PAD_COLORS["selected"] if pad.loaded else PAD_COLORS["empty"]
            self.pad_buttons[self.selected_key].configure(bg=color)

    # ---- Loading ----
    def _load_sample(self, key):
        path = filedialog.askopenfilename(
            title=f"Load sample for pad [{key.upper()}]",
            filetypes=[
                ("Audio files", "*.wav *.mp3 *.ogg *.flac *.aiff"),
                ("All files", "*.*"),
            ],
        )
        if not path:
            return

        try:
            self.pads[key].load(path)
        except Exception as e:
            self.info_label.configure(text=f"Error loading: {e}")
            return

        self._refresh_pad_button(key)
        if self.selected_key == key:
            self._update_waveform()
            self._sync_sliders()
            self._update_info()

    def _refresh_pad_button(self, key):
        pad = self.pads[key]
        label = f"{key.upper()}\n{pad.name[:8]}" if pad.loaded else key.upper()
        is_selected = self.selected_key == key
        if is_selected:
            color = PAD_COLORS["selected"] if pad.loaded else PAD_COLORS["empty"]
        else:
            color = PAD_COLORS["loaded"] if pad.loaded else PAD_COLORS["empty"]
        self.pad_buttons[key].configure(text=label, bg=color)

    # ---- Playback ----
    def _play_pad(self, key):
        pad = self.pads[key]
        if not pad.loaded:
            return

        # Flash the pad
        self.pad_buttons[key].configure(bg=PAD_COLORS["playing"])
        self.root.after(150, lambda: self._update_selected_color()
                        if key == self.selected_key
                        else self.pad_buttons[key].configure(
                            bg=PAD_COLORS["loaded"]))

        # Prepare audio in a thread, then play on dedicated channel
        threading.Thread(target=self._play_audio, args=(pad, key), daemon=True).start()

    def _play_audio(self, pad, key):
        chopped, sr = pad.get_chopped()
        if chopped is None:
            return

        # Apply pitch shift by resampling
        if pad.tune != 0.0:
            factor = 2.0 ** (-pad.tune / 12.0)
            n_samples = len(chopped)
            new_len = int(round(n_samples * factor))
            if new_len < 1:
                new_len = 1
            indices = np.linspace(0, n_samples - 1, new_len)
            resampled = np.zeros((new_len, chopped.shape[1]), dtype=np.float32)
            for ch in range(chopped.shape[1]):
                resampled[:, ch] = np.interp(indices, np.arange(n_samples), chopped[:, ch])
            chopped = resampled

        # Ensure stereo
        if chopped.ndim == 1:
            chopped = np.column_stack([chopped, chopped])
        elif chopped.shape[1] == 1:
            chopped = np.column_stack([chopped[:, 0], chopped[:, 0]])

        # Normalize to int16
        audio_int = (chopped * 32767).astype(np.int16)

        # Write to in-memory WAV via soundfile
        buf = io.BytesIO()
        sf.write(buf, audio_int, sr, format="WAV", subtype="PCM_16")
        buf.seek(0)

        try:
            sound = pygame.mixer.Sound(buf)
            channel = self.pad_channels[key]
            channel.stop()   # stop any previous playback on this pad
            channel.play(sound)
        except Exception:
            pass

    # ---- Waveform ----
    def _update_waveform(self):
        self.ax.clear()
        self._style_axis()

        if not self.selected_key:
            self.ax.set_title("No pad selected", color="#555555", fontsize=9)
            self.canvas.draw_idle()
            return

        pad = self.pads[self.selected_key]
        if not pad.loaded:
            self.ax.set_title(
                f"Pad [{self.selected_key.upper()}] — empty (press Enter to load)",
                color="#555555", fontsize=9,
            )
            self.canvas.draw_idle()
            return

        mono = pad.get_mono()
        n = len(mono)
        t = np.linspace(0, n / pad.sample_rate, n)

        # Draw full waveform dimmed
        self.ax.plot(t, mono, color="#334455", linewidth=0.4)

        # Draw chopped region bright
        s = int(pad.start * n)
        e = int(pad.end * n)
        if s < e:
            self.ax.plot(t[s:e], mono[s:e], color=ACCENT_COLOR, linewidth=0.5)

        # Draw start/end lines
        start_t = pad.start * (n / pad.sample_rate)
        end_t = pad.end * (n / pad.sample_rate)
        self.ax.axvline(start_t, color="#44ff44", linewidth=1, linestyle="--", alpha=0.7)
        self.ax.axvline(end_t, color="#ff4444", linewidth=1, linestyle="--", alpha=0.7)

        self.ax.set_title(
            f"Pad [{self.selected_key.upper()}] — {pad.name}",
            color=TEXT_COLOR, fontsize=9,
        )
        self.ax.set_xlim(0, n / pad.sample_rate)
        self.fig.tight_layout(pad=1.5)
        self.canvas.draw_idle()

    # ---- Chop sliders ----
    def _sync_sliders(self):
        if self.selected_key:
            pad = self.pads[self.selected_key]
            self.start_var.set(pad.start)
            self.end_var.set(pad.end)
            self.tune_var.set(pad.tune)
            self._update_tune_label()

    def _on_chop_change(self, _=None):
        if not self.selected_key:
            return
        pad = self.pads[self.selected_key]

        s = self.start_var.get()
        e = self.end_var.get()

        # Enforce start < end
        if s >= e:
            if s == pad.start:  # end was moved
                e = min(s + 0.01, 1.0)
                self.end_var.set(e)
            else:
                s = max(e - 0.01, 0.0)
                self.start_var.set(s)

        pad.start = s
        pad.end = e
        self._update_waveform()
        self._update_info()

    # ---- Tune ----
    def _on_tune_change(self, _=None):
        if not self.selected_key:
            return
        pad = self.pads[self.selected_key]
        pad.tune = round(self.tune_var.get(), 2)
        self._update_tune_label()
        self._update_info()

    def _reset_tune(self):
        if not self.selected_key:
            return
        pad = self.pads[self.selected_key]
        pad.tune = 0.0
        self.tune_var.set(0.0)
        self._update_tune_label()
        self._update_info()

    def _update_tune_label(self):
        val = self.tune_var.get()
        sign = "+" if val > 0 else ""
        self.tune_label.configure(text=f"{sign}{val:.2f} st")

    # ---- Info ----
    def _update_info(self):
        if not self.selected_key:
            self.info_label.configure(text="No pad selected")
            return
        pad = self.pads[self.selected_key]
        if not pad.loaded:
            self.info_label.configure(text=f"Pad [{self.selected_key.upper()}] — Press Enter to load a sample")
            return

        dur = len(pad.audio_data) / pad.sample_rate
        chop_dur = dur * (pad.end - pad.start)
        sign = "+" if pad.tune > 0 else ""
        self.info_label.configure(
            text=f"Pad [{self.selected_key.upper()}]  {pad.name}  |  "
                 f"{dur:.2f}s total  |  Chop: {chop_dur:.2f}s  "
                 f"({pad.start:.1%} → {pad.end:.1%})  |  {pad.sample_rate}Hz  |  "
                 f"Tune: {sign}{pad.tune:.2f}st"
        )


if __name__ == "__main__":
    root = tk.Tk()
    app = SamplePadApp(root)
    root.mainloop()
