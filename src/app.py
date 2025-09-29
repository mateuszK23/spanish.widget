import tkinter as tk
import ctypes
from data_manager import DailyDataManager
from quiz import QuizDialog
from tray import TrayController
from logger import logger
from datetime import date
from utils import format_seconds
from settings_manager import load_settings

BG_COLOR = "#2e2e2e"
TEXT_COLOR = "#f9f9f9"
FRAME_COLOR = "#2e2e2e"
SEPARATOR_COLOR = "black"

class SpanishWidgetApp:
    def __init__(self):
        logger.info("Starting the app")
        self.manager = DailyDataManager()
        self.root = tk.Tk()
        self.root.title("Spanish Widget")
        self.root.overrideredirect(True)
        self.root.config(bg="white")

        # Quiz
        settings = load_settings()
        self.quiz_enabled = settings['quiz_enabled']
        self.quiz_interval = settings['quiz_interval']
        self._quiz_job = None  # handle for root.after

        logger.info(f"\n\nConfig values: \nquiz_enabled = {self.quiz_enabled}\nquiz_interval = {self.quiz_interval}\n")
        self.tray = TrayController(self)
        self.tray.start()

        # Position top-right
        w, h = 650, 500
        x = self.root.winfo_screenwidth() - w - 10
        self.root.geometry(f"{w}x{h}+{x}+10")

        self.main_frame = tk.Frame(self.root, bg="white")
        self.main_frame.pack(padx=5, pady=5)

        # Windows click-through
        hwnd = ctypes.windll.user32.FindWindowW(None, self.root.title())
        ctypes.windll.user32.SetWindowLongW(hwnd, -20, 0x80000 | 0x20)
        self.root.attributes("-transparentcolor", "white")
        self.root.attributes("-topmost", False)

        # Get today's data
        logger.info(f"Checking if there is an entry for {str(date.today())}")
        data = self.manager.get_today()
        if data:
            logger.info(f"Data found: noun {data['noun']}, verb: {data['verb']}")
        if not data:
            logger.info(f"Data not found, generating")
            noun = self.manager.random_noun()
            verb = self.manager.random_verb()
            conj = self.manager.conjugation(verb.spanish)
            data = {"noun": noun.__dict__, "verb": verb.__dict__, "conjugation": conj}
            self.manager.save_today(noun, verb, conj)

        self.display_data(data)
        self.schedule_quiz(data["noun"])

    def display_data(self, data):
        for w in self.main_frame.winfo_children():
            w.destroy()

        def build_frame(title, content_top, content_bottom):
            f = tk.Frame(self.main_frame, bg=FRAME_COLOR, bd=2, relief="ridge", padx=10, pady=5)
            tk.Label(f, text=title, font=("Arial", 13, "bold"), bg=FRAME_COLOR, fg=TEXT_COLOR).pack(anchor="w")
            tk.Frame(f, height=1, bg=SEPARATOR_COLOR).pack(fill="x", pady=4)
            tk.Label(f, text=content_top, font=("Arial", 12), bg=FRAME_COLOR, fg=TEXT_COLOR).pack(anchor="w")
            tk.Frame(f, height=1, bg=SEPARATOR_COLOR).pack(fill="x", pady=4)
            tk.Label(f, text=content_bottom, font=("Arial", 11), bg=FRAME_COLOR, fg=TEXT_COLOR).pack(anchor="w")
            f.pack(fill="x", padx=10, pady=5)

        build_frame("Random noun", data["noun"]["spanish"].upper(), data["noun"]["english"])
        build_frame("Random verb", data["verb"]["spanish"].upper(), data["verb"]["english"])

        # Conjugation table
        conj_frame = tk.Frame(self.main_frame, bg=BG_COLOR, bd=2, relief="ridge", padx=5, pady=5)
        tk.Label(conj_frame, text="Conjugation", font=("Arial", 13, "bold"),
                 bg=BG_COLOR, fg=TEXT_COLOR).grid(row=0, column=0, columnspan=len(data["conjugation"][0]), pady=(0, 5))
        for i, row in enumerate(data["conjugation"][:10]):
            for j, cell in enumerate(row):
                tk.Label(conj_frame, text=cell, font=("Courier", 10),
                         bg=BG_COLOR, fg=TEXT_COLOR, borderwidth=1, relief="solid",
                         padx=5, pady=2).grid(row=i+1, column=j, sticky="nsew")
                conj_frame.grid_columnconfigure(j, weight=1)
        conj_frame.pack(fill="x", padx=10, pady=5)

    def schedule_quiz(self, noun):
        """Schedule or cancel the quiz depending on quiz_enabled."""
        # Cancel any existing scheduled quiz
        if self._quiz_job:
            self.root.after_cancel(self._quiz_job)
            self._quiz_job = None

        if not self.quiz_enabled:
            return  # don’t reschedule if disabled

        # Reschedule new quiz
        self._quiz_job = self.root.after(
            self.quiz_interval * 1000,
            lambda: (QuizDialog(self.root, noun), self.schedule_quiz(noun))
        )

    def set_quiz_enabled(self, enabled: bool):
        """Enable or disable quizzes and reschedule accordingly."""
        if enabled:
            logger.info("Toggling on the quiz")
        else:
            logger.info("Toggling off the quiz")

        self.quiz_enabled = enabled
        today = self.manager.get_today()
        if today:
            self.schedule_quiz(today["noun"])

    def set_quiz_interval(self, seconds: int):
        """Update quiz interval (in seconds) and reschedule."""
        logger.info(f"Updating quiz interval to: {seconds}s, which is {format_seconds(seconds)}")
        self.quiz_interval = seconds
        today = self.manager.get_today()
        if today:
            self.schedule_quiz(today["noun"])

    def quit(self):
        self.root.quit()
        self.root.destroy()

    def run(self):
        self.root.mainloop()
