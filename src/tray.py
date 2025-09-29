import tkinter as tk
from tkinter import ttk
import threading
import pystray
from PIL import Image
from paths import TRAY_ICON
from logger import logger
from settings_manager import save_settings

class TrayController:
    def __init__(self, app):
        """
        app: reference to your main SpanishWidgetApp
        """
        self.app = app
        self.icon = pystray.Icon("SpanishWidget", Image.open(TRAY_ICON), "Spanish Widget")
        self.menu = pystray.Menu(
            pystray.MenuItem("Settings", self.open_settings),
            pystray.MenuItem("Quit", self.quit_app)
        )
        self.icon.menu = self.menu

    def start(self):
        # Run tray in a background thread
        thread = threading.Thread(target=self.icon.run, daemon=True)
        thread.start()
    
    def toggle_quiz(self, icon, item):
        self.app.toggle_quiz()  # delegate to app

    def set_interval(self, icon, item):
        def ask():
            import tkinter.simpledialog as simpledialog
            interval = simpledialog.askinteger(
                "Quiz Interval",
                "Enter interval in seconds:",  # seconds for easier testing
                initialvalue=self.app.quiz_interval
            )
            if interval and interval > 0:
                self.app.quiz_interval = interval
                today = self.app.manager.get_today()
                if today:
                    self.app.schedule_quiz(today["noun"])
    
        # Run on Tk main thread
        self.app.root.after(0, ask)

    def open_settings(self, icon, item):
        def show():
            if hasattr(self, "_settings_win") and self._settings_win.winfo_exists():
                self._settings_win.lift()
                return

            win = tk.Toplevel(self.app.root)
            win.title("Spanish Widget Settings")
            win.geometry("300x180")
            win.resizable(False, False)
            self._settings_win = win

            container = ttk.Frame(win, padding=15)
            container.pack(fill="both", expand=True)

            # Title
            ttk.Label(container, text="Settings", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0, 10))

            # Quiz enabled checkbox
            quiz_var = tk.BooleanVar(value=self.app.quiz_enabled)
            chk = ttk.Checkbutton(
                container, text="Enable Quizzes", variable=quiz_var
            )
            chk.pack(anchor="w", pady=5)

            # Interval row
            interval_frame = ttk.Frame(container)
            interval_frame.pack(anchor="w", pady=10, fill="x")

            ttk.Label(interval_frame, text="Quiz Interval (seconds):").pack(side="left")
            interval_var = tk.IntVar(value=self.app.quiz_interval)
            spin = ttk.Spinbox(interval_frame, from_=1, to=3600, textvariable=interval_var, width=6)
            spin.pack(side="left", padx=(10, 0))

            # Buttons row
            btn_frame = ttk.Frame(container)
            btn_frame.pack(side="bottom", fill="x", pady=(15, 0))

            def save_and_close():
                quiz_enabled = quiz_var.get()
                quiz_interval = interval_var.get()
                self.app.set_quiz_interval(quiz_interval)
                self.app.set_quiz_enabled(quiz_enabled)
                save_settings(quiz_enabled, quiz_interval)
                win.destroy()

            ttk.Button(btn_frame, text="Save & Close", command=save_and_close).pack(side="right")

        self.app.root.after(0, show)


    def quit_app(self, icon, item):
        logger.info("Quitting the app")
        self.icon.stop()
        self.app.quit()
