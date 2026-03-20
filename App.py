import tkinter as tk
import ttkbootstrap as ttk
from tkinter import messagebox, filedialog
import time
import os
import platform
import subprocess
from datetime import datetime
from zoneinfo import available_timezones, ZoneInfo
from tzlocal import get_localzone_name
import math

# Sound Player
class SoundPlayer:
    def __init__(self):
        self.system = platform.system()
        self.mode = "beep"
        self.custom_path = None

    def set_mode(self, mode: str):
        self.mode = mode

    def set_custom_path(self, path: str):
        self.custom_path = path

    def play(self):
        try:
            if self.mode == "beep":
                if self.system == "Windows":
                    import winsound
                    winsound.MessageBeep(winsound.MB_OK)
                elif self.system == "Darwin":
                    subprocess.run(["osascript", "-e", "beep"], check=False)
                else:
                    print("\a", end="", flush=True)

            elif self.mode == "custom":
                if self.custom_path and os.path.exists(self.custom_path):
                    if self.system == "Windows":
                        import winsound
                        winsound.PlaySound(self.custom_path, winsound.SND_FILENAME)
                    elif self.system == "Darwin":
                        subprocess.run(["afplay", self.custom_path], check=False)
                    else:
                        subprocess.run(["aplay", self.custom_path], check=False)
                else:
                    raise FileNotFoundError("Custom sound not found.")
            else:
                raise ValueError("Unknown sound mode.")
        except Exception as e:
            print("Sound failed:", e)

# Stopwatch
class Stopwatch:
    def __init__(self):
        self._start_time = None
        self._elapsed = 0.0
        self._running = False

    def start(self):
        if not self._running:
            self._start_time = time.perf_counter()
            self._running = True

    def stop(self):
        if self._running:
            self._elapsed += time.perf_counter() - self._start_time
            self._running = False

    def reset(self):
        self._start_time = None
        self._elapsed = 0.0
        self._running = False

    def elapsed(self):
        if self._running:
            return self._elapsed + (time.perf_counter() - self._start_time)
        return self._elapsed

    @staticmethod
    def format_time(seconds: float) -> str:
        millis = int((seconds - int(seconds)) * 100)
        minutes, sec = divmod(int(seconds), 60)
        hours, minutes = divmod(minutes, 60)
        return f"{hours:02d}:{minutes:02d}:{sec:02d}.{millis:02d}"

# Timer
class Timer:
    def __init__(self):
        self._total_seconds = 0
        self._remaining = 0
        self._running = False
        self._end_time = None

    def set(self, seconds: int):
        self._total_seconds = seconds
        self._remaining = seconds
        self._running = False

    def start(self):
        if self._remaining > 0 and not self._running:
            self._end_time = time.perf_counter() + self._remaining
            self._running = True

    def pause(self):
        if self._running:
            self._remaining = max(0, self._end_time - time.perf_counter())
            self._running = False

    def reset(self):
        self._remaining = self._total_seconds
        self._running = False

    def tick(self):
        if self._running:
            self._remaining = max(0, self._end_time - time.perf_counter())
            if self._remaining <= 0:
                self._running = False
                return False
        return True

    def remaining(self):
        return self._remaining

    @staticmethod
    def format_time(seconds: float) -> str:
        minutes, sec = divmod(int(seconds), 60)
        hours, minutes = divmod(minutes, 60)
        return f"{hours:02d}:{minutes:02d}:{sec:02d}"

# 24h Analog Clock Widget
class AnalogClockWidget(ttk.Frame):
    def __init__(self, parent, tz_name=None):
        super().__init__(parent)
        self.tz_name = tz_name

        self.canvas = tk.Canvas(self, width=220, height=220, bg="white")
        self.canvas.pack()
        self.label = ttk.Label(self, text="", font=("Arial", 12))
        self.label.pack()

        self.center_x = 110
        self.center_y = 110
        self.radius = 100

        self._draw_clock_face()
        self._update_clock()

    def _draw_clock_face(self):
        self.canvas.create_oval(
            self.center_x - self.radius,
            self.center_y - self.radius,
            self.center_x + self.radius,
            self.center_y + self.radius,
            width=3
        )

        for hour in range(24):
            angle = math.radians((hour / 24) * 360 - 90)
            x1 = self.center_x + (self.radius - 5) * math.cos(angle)
            y1 = self.center_y + (self.radius - 5) * math.sin(angle)
            x2 = self.center_x + (self.radius - 20) * math.cos(angle)
            y2 = self.center_y + (self.radius - 20) * math.sin(angle)
            self.canvas.create_line(x1, y1, x2, y2, width=2)

            if hour % 3 == 0:
                lx = self.center_x + (self.radius - 30) * math.cos(angle)
                ly = self.center_y + (self.radius - 30) * math.sin(angle)
                self.canvas.create_text(lx, ly, text=str(hour), font=("Arial", 10))

    def _update_clock(self):
        self.canvas.delete("hands")

        if self.tz_name:
            tzinfo = ZoneInfo(self.tz_name)
            now = datetime.now(tzinfo)
        else:
            now = datetime.now()

        hour = now.hour
        minute = now.minute
        second = now.second

        self.label.config(
            text=now.strftime("%H:%M:%S") if not self.tz_name else f"{self.tz_name}\n{now.strftime('%H:%M:%S')}"
        )

        hour_angle = math.radians((hour / 24) * 360 - 90 + (minute / 60) * (360 / 24))
        minute_angle = math.radians((minute / 60) * 360 - 90)
        second_angle = math.radians((second / 60) * 360 - 90)

        hx = self.center_x + (self.radius - 50) * math.cos(hour_angle)
        hy = self.center_y + (self.radius - 50) * math.sin(hour_angle)
        self.canvas.create_line(self.center_x, self.center_y, hx, hy, width=4, fill="white", tags="hands")

        mx = self.center_x + (self.radius - 35) * math.cos(minute_angle)
        my = self.center_y + (self.radius - 35) * math.sin(minute_angle)
        self.canvas.create_line(self.center_x, self.center_y, mx, my, width=3, tags="hands", fill="white")

        sx = self.center_x + (self.radius - 20) * math.cos(second_angle)
        sy = self.center_y + (self.radius - 20) * math.sin(second_angle)
        self.canvas.create_line(self.center_x, self.center_y, sx, sy, width=3, fill="red", tags="hands")

        self.after(1000, self._update_clock)

# Clock Tile (fixed size container + X button)
class ClockTile(ttk.Frame):
    def __init__(self, parent, tz_name=None, click_callback=None, remove_callback=None, allow_remove=True):
        super().__init__(parent, width=260, height=260, relief="raised", borderwidth=2)
        self.pack_propagate(False)

        self.tz_name = tz_name
        self.clock = AnalogClockWidget(self, tz_name=tz_name)
        self.clock.pack(expand=True)

        self.remove_callback = remove_callback

        # X button only if allowed
        self.close_btn = None
        if allow_remove:
            # smaller and perfectly inside
            self.close_btn = ttk.Button(self, text="✕", width=1, command=self._remove)
            self.close_btn.place(x=214, y=4)

        self.click_callback = click_callback
        self.bind("<Button-1>", self._on_click)
        self.clock.bind("<Button-1>", self._on_click)
        self.clock.canvas.bind("<Button-1>", self._on_click)
        self.clock.label.bind("<Button-1>", self._on_click)

    def _remove(self):
        if self.remove_callback:
            self.remove_callback(self)

    def _on_click(self, event):
        if self.click_callback:
            self.click_callback(self)

# Clock Grid + Click-to-Swap (Cross-Platform)
class ClockGrid(ttk.Frame):
    def __init__(self, parent, local_tz):
        super().__init__(parent)

        self.cols = 5
        self.clock_tiles = []
        self.selected_index = None
        self.local_tz = local_tz

        self.grid_frame = ttk.Frame(self)
        self.grid_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Local clock is fixed (not removable)
        self.add_clock(local_tz, allow_remove=False)

    def add_clock(self, tz_name, allow_remove=True) -> None:
        if tz_name and any(tile.tz_name == tz_name for tile in self.clock_tiles):
            return

        tile = ClockTile(
            self.grid_frame,
            tz_name=tz_name,
            click_callback=self._on_click_tile,
            remove_callback=self._remove_tile,
            allow_remove=allow_remove
        )
        self.clock_tiles.append(tile)
        self._regrid_clocks()

    def remove_clock(self, tz_name) -> None:
        for i, tile in enumerate(self.clock_tiles):
            if tile.tz_name == tz_name:
                tile.destroy()
                self.clock_tiles.pop(i)
                break
        self._regrid_clocks()

    def _remove_tile(self, tile) -> None:
        if tile.tz_name == self.local_tz:
            return  # cannot remove local clock

        if tile.tz_name:
            self.master.master.tz_fav.discard(tile.tz_name)

        tile.destroy()
        self.clock_tiles.remove(tile)
        self._regrid_clocks()

    def _regrid_clocks(self):
        for i, tile in enumerate(self.clock_tiles):
            row = i // self.cols
            col = i % self.cols
            tile.grid(row=row, column=col, padx=10, pady=10)

    def _on_click_tile(self, tile):
        idx = self.clock_tiles.index(tile)

        if self.selected_index is None:
            self.selected_index = idx
            tile.config(style="info.TFrame")
            return

        if idx != self.selected_index:
            self.clock_tiles[self.selected_index], self.clock_tiles[idx] = (
                self.clock_tiles[idx],
                self.clock_tiles[self.selected_index],
            )

        # REMOVE highlight from ALL tiles
        for t in self.clock_tiles:
            t.config(style="TFrame")

        self.selected_index = None
        self._regrid_clocks()

# Main App
class StopwatchTimerApp(ttk.Window):
    def __init__(self):
        super().__init__(themename="darkly")
        self.title("Stopwatch and Clock App")
        self.geometry("1920x1080")
        self.resizable(True, True)

        self.sound = SoundPlayer()
        self.stopwatch = Stopwatch()
        self.local_tz = get_localzone_name()
        self.pinned_timezones = set()

        self._build_ui()

    def _build_ui(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill="both")

        self.sw_tab = ttk.Frame(self.notebook)
        self.tm_tab = ttk.Frame(self.notebook)
        self.clock_tab = ClockGrid(self.notebook, local_tz=self.local_tz)
        self.tz_tab = ttk.Frame(self.notebook)
        self.sound_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.sw_tab, text="Stopwatch")
        self.notebook.add(self.tm_tab, text="Timers")
        self.notebook.add(self.clock_tab, text="Clock")
        self.notebook.add(self.tz_tab, text="Timezones")
        self.notebook.add(self.sound_tab, text="Sounds")

        self._build_stopwatch_tab()
        self._build_timers_tab()
        self._build_timezones_tab()
        self._build_sounds_tab()

        self.bind("<space>", lambda e: self._sw_start() if self.notebook.index("current") == 0 else None)
        self.bind("<Escape>", lambda e: self._sw_stop() if self.notebook.index("current") == 0 else None)

    # Stopwatch Tab
    def _build_stopwatch_tab(self):
        self.sw_time = ttk.Label(self.sw_tab, text="00:00:00.00", font=("Arial", 36))
        self.sw_time.pack(pady=20)

        self.sw_laps = tk.Listbox(self.sw_tab, height=8)
        self.sw_laps.pack(fill="x", padx=20, pady=10)

        sw_controls = ttk.Frame(self.sw_tab)
        sw_controls.pack()

        ttk.Button(sw_controls, text="Start", command=self._sw_start, bootstyle="success").pack(side="left", padx=5)
        ttk.Button(sw_controls, text="Stop", command=self._sw_stop, bootstyle="warning").pack(side="left", padx=5)
        ttk.Button(sw_controls, text="Lap", command=self._sw_lap, bootstyle="info").pack(side="left", padx=5)
        ttk.Button(sw_controls, text="Reset", command=self._sw_reset, bootstyle="danger").pack(side="left", padx=5)

    def _sw_start(self):
        self.stopwatch.start()
        self._update_stopwatch()

    def _sw_stop(self):
        self.stopwatch.stop()

    def _sw_reset(self):
        self.stopwatch.reset()
        self.sw_time.config(text="00:00:00.00")
        self.sw_laps.delete(0, tk.END)

    def _sw_lap(self):
        lap = self.stopwatch.elapsed()
        lap_str = Stopwatch.format_time(lap)
        self.sw_laps.insert(tk.END, lap_str)

    def _update_stopwatch(self):
        if self.stopwatch._running:
            self.sw_time.config(text=Stopwatch.format_time(self.stopwatch.elapsed()))
            self.after(50, self._update_stopwatch)

    # Timers Tab
    def _build_timers_tab(self):
        top_frame = ttk.Frame(self.tm_tab)
        top_frame.pack(fill="x", pady=10)

        ttk.Button(top_frame, text="Add Timer", command=self._add_timer, bootstyle="primary").pack(side="left", padx=10)
        ttk.Button(top_frame, text="Clear All Timers", command=self._clear_all_timers, bootstyle="danger").pack(side="left", padx=10)

        self.timer_list_frame = ttk.Frame(self.tm_tab)
        self.timer_list_frame.pack(fill="both", expand=True)

        self.timers = []
        self.after(50, self._update_all_timers)

    def _add_timer(self):
        timer_ui = {}
        timer_ui["timer"] = Timer()

        frame = ttk.Frame(self.timer_list_frame, relief="raised", borderwidth=2)
        frame.pack(fill="x", padx=10, pady=5)

        timer_ui["duration_var"] = tk.StringVar(value="00:00")
        duration_entry = ttk.Entry(frame, textvariable=timer_ui["duration_var"], width=8)
        duration_entry.pack(side="left", padx=5)

        timer_ui["label"] = ttk.Label(frame, text="00:00:00", font=("Arial", 18))
        timer_ui["label"].pack(side="left", padx=10)

        timer_ui["progress"] = ttk.Progressbar(frame, maximum=100, length=200)
        timer_ui["progress"].pack(side="left", padx=10)

        timer_ui["progress_target"] = 0

        ttk.Button(frame, text="Start", command=lambda t=timer_ui: self._start_timer(t), bootstyle="success").pack(side="left", padx=5)
        ttk.Button(frame, text="Pause", command=lambda t=timer_ui: self._pause_timer(t), bootstyle="warning").pack(side="left", padx=5)
        ttk.Button(frame, text="Reset", command=lambda t=timer_ui: self._reset_timer(t), bootstyle="danger").pack(side="left", padx=5)
        ttk.Button(frame, text="Remove", command=lambda t=timer_ui: self._remove_timer(t), bootstyle="outline-danger").pack(side="left", padx=5)

        timer_ui["frame"] = frame
        self.timers.append(timer_ui)

    def _start_timer(self, timer_ui):
        timer = timer_ui["timer"]

        if timer._total_seconds == 0 and timer.remaining() == 0:
            try:
                mins, secs = map(int, timer_ui["duration_var"].get().split(":"))
                total = mins * 60 + secs
                timer.set(total)
            except Exception:
                messagebox.showerror("Invalid Duration", "Use MM:SS format")
                return

        timer.start()

    def _pause_timer(self, timer_ui):
        timer_ui["timer"].pause()

    def _reset_timer(self, timer_ui):
        timer = timer_ui["timer"]
        timer.reset()
        timer_ui["label"].config(text="00:00:00")
        timer_ui["progress"]["value"] = 0
        timer_ui["progress_target"] = 0

    def _remove_timer(self, timer_ui):
        timer_ui["frame"].destroy()
        self.timers.remove(timer_ui)

    def _clear_all_timers(self):
        for t in self.timers[:]:
            t["frame"].destroy()
            self.timers.remove(t)

    def _update_all_timers(self):
        for timer_ui in self.timers:
            timer = timer_ui["timer"]

            if timer.tick() is False:
                timer_ui["label"].config(text="00:00:00")
                timer_ui["progress_target"] = 100
                self.sound.play()
                continue

            remaining = timer.remaining()
            timer_ui["label"].config(text=Timer.format_time(remaining))

            if timer._total_seconds > 0:
                target = (1 - remaining / timer._total_seconds) * 100
                timer_ui["progress_target"] = target

            current = timer_ui["progress"]["value"]
            target = timer_ui["progress_target"]
            step = 1.5

            if abs(current - target) > step:
                if current < target:
                    current += step
                else:
                    current -= step
                timer_ui["progress"]["value"] = current
            else:
                timer_ui["progress"]["value"] = target

        self.after(50, self._update_all_timers)

    # Timezones Tab
    def _build_timezones_tab(self) -> None:
        top_frame = ttk.Frame(self.tz_tab)
        top_frame.pack(fill="x", pady=5)

        self.tz_search = tk.StringVar()
        search_entry = ttk.Entry(top_frame, textvariable=self.tz_search)
        search_entry.pack(side="left", fill="x", expand=True, padx=10)
        search_entry.bind("<KeyRelease>", self._update_timezone_list)

        self.tz_fav = set()
        self.tz_local = self.local_tz

        self.tz_canvas = tk.Canvas(self.tz_tab)
        self.tz_scroll = ttk.Scrollbar(self.tz_tab, orient="vertical", command=self.tz_canvas.yview)
        self.tz_scroll.pack(side="right", fill="y")
        self.tz_canvas.pack(side="left", fill="both", expand=True)

        self.tz_canvas.configure(yscrollcommand=self.tz_scroll.set)
        self.tz_canvas.bind('<Configure>', lambda e: self.tz_canvas.configure(scrollregion=self.tz_canvas.bbox("all")))

        self.tz_frame = ttk.Frame(self.tz_canvas)
        self.tz_canvas.create_window((0, 0), window=self.tz_frame, anchor="nw")

        self.timezones = sorted(list(available_timezones()))
        self.tz_labels = {}

        self._build_timezone_rows()
        self._update_timezone_clock()

    def _build_timezone_rows(self):
        for widget in self.tz_frame.winfo_children():
            widget.destroy()

        for tz in self.timezones:
            row = ttk.Frame(self.tz_frame)
            row.pack(fill="x", pady=2, padx=5)

            fav_btn = ttk.Checkbutton(row, text="", bootstyle="success-round-toggle")
            fav_btn.pack(side="left")
            fav_btn.var = tk.BooleanVar(value=(tz in self.tz_fav))
            fav_btn.config(variable=fav_btn.var)
            fav_btn.var.trace_add("write", lambda *a, tz=tz, var=fav_btn.var: self._toggle_fav(tz, var))

            label = ttk.Label(row, text=tz, width=45, anchor="w")
            label.pack(side="left")

            time_label = ttk.Label(row, text="", width=12, anchor="w")
            time_label.pack(side="left")

            if tz == self.tz_local:
                label.config(text=f"{tz} (Local)")
                fav_btn.state(["disabled"])

            self.tz_labels[tz] = time_label

    def _toggle_fav(self, tz, var):
        if var.get():
            self.tz_fav.add(tz)
            self.clock_tab.add_clock(tz)
        else:
            self.tz_fav.discard(tz)
            self.clock_tab.remove_clock(tz)

    def _update_timezone_list(self, event=None):
        query = self.tz_search.get().lower()
        self.timezones = sorted([tz for tz in available_timezones() if query in tz.lower()])
        self._build_timezone_rows()

    def _update_timezone_clock(self):
        for tz, label in self.tz_labels.items():
            tzinfo = ZoneInfo(tz)
            now = datetime.now(tzinfo)
            label.config(text=now.strftime("%H:%M:%S"))

        self.after(1000, self._update_timezone_clock)

    # Sound Tab
    def _build_sounds_tab(self):
        frame = ttk.Frame(self.sound_tab)
        frame.pack(pady=20, padx=20)

        self.sound_mode = tk.StringVar(value=self.sound.mode)

        ttk.Radiobutton(frame, text="System Beep", variable=self.sound_mode, value="beep").pack(anchor="w")
        ttk.Radiobutton(frame, text="Custom Sound", variable=self.sound_mode, value="custom").pack(anchor="w")

        ttk.Button(frame, text="Select Custom Sound", command=self._choose_custom_sound).pack(pady=10)
        ttk.Button(frame, text="Play Test Sound", command=self.sound.play).pack(pady=10)
        ttk.Button(frame, text="Save Settings", command=self._save_sound_settings).pack(pady=10)

    def _choose_custom_sound(self):
        path = filedialog.askopenfilename(
            title="Select Sound File",
            filetypes=[("Audio Files", "*.wav *.mp3 *.m4a *.aiff *,mp4")]
        )
        if path:
            self.sound.set_custom_path(path)
            messagebox.showinfo("Sound Set", f"Custom sound selected:\n{path}")

    def _save_sound_settings(self):
        self.sound.set_mode(self.sound_mode.get())
        messagebox.showinfo("Saved", "Sound settings saved.")

if __name__ == "__main__":
    app = StopwatchTimerApp()
    app.mainloop()