import tkinter as tk
import ctypes
from data_manager import DailyDataManager
from quiz import QuizDialog
from tray import TrayController
from logger import logger
from datetime import date
from settings_manager import load_settings


# === COLORS ===
BG_COLOR = "#2e2e2e"
TEXT_COLOR = "#f9f9f9"
FRAME_COLOR = "#2e2e2e"
SEPARATOR_COLOR = "black"
HIGHLIGHTED_CELL_COLOR = "#1A1A1A"
WINDOW_BG_COLOR = "white"

# === LAYOUT ===
WINDOW_MARGIN = 20
WINDOW_WIDTH = 850
WINDOW_HEIGHT = 500

FRAME_PADX = 10
FRAME_PADY = 5
FRAME_BORDER_WIDTH = 2
FRAME_RELIEF = "ridge"

CELL_WIDTH = 15
CELL_PADX = 5
CELL_PADY = 5
CELL_BORDER_WIDTH = 1
CELL_RELIEF = "solid"

SECTION_PADX = 10
SECTION_PADY = 5
SEPARATOR_HEIGHT = 1
SEPARATOR_PADY = 4

# === FONT ===
FONT_NAME = "DejaVu Sans Mono"
TITLE_SIZE = 13
SUBTITLE_SIZE = 12
CONTENT_SIZE = 11
HEADER_SIZE = 13
CELL_SIZE = 11

TITLE_FONT = (FONT_NAME, TITLE_SIZE, "bold")
SUBTITLE_FONT = (FONT_NAME, SUBTITLE_SIZE)
CONTENT_FONT = (FONT_NAME, CONTENT_SIZE)
CONJUGATION_HEADER_FONT = (FONT_NAME, HEADER_SIZE, "bold")
CONJUGATION_CELLS_FONT = (FONT_NAME, CELL_SIZE)

# === QUIZ ===
MS_IN_SECOND = 1000

# === WINDOW ===
WINDOW_OFFSET_X = -30  # manual adjustment for right margin


class SpanishWidgetApp:
    def __init__(self):
        logger.info("Starting the app")
        self.manager = DailyDataManager()
        self.root = tk.Tk()
        self._configure_root()

        # Quiz settings
        settings = load_settings()
        self.quiz_enabled = settings["quiz_enabled"]
        self.quiz_interval = settings["quiz_interval"]
        self._quiz_job = None

        logger.info(f"Config values: {settings}")
        self.tray = TrayController(self)
        self.tray.start()

        # Load data
        data = self._load_today_data()
        self.display_data(data)
        self.schedule_quiz(data["noun"])

    # === Root window setup ===
    def _configure_root(self):
        self.root.title("Spanish Widget")
        self.root.overrideredirect(True)
        self.root.config(bg=WINDOW_BG_COLOR)

        screen_w = self.root.winfo_screenwidth()
        x = screen_w - WINDOW_WIDTH + WINDOW_MARGIN + WINDOW_OFFSET_X
        y = WINDOW_MARGIN
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x}+{y}")

        self.main_frame = tk.Frame(self.root, bg=WINDOW_BG_COLOR)
        self.main_frame.pack(padx=FRAME_PADX, pady=FRAME_PADY)

        # Make window click-through (Windows only)
        hwnd = ctypes.windll.user32.FindWindowW(None, self.root.title())
        ctypes.windll.user32.SetWindowLongW(hwnd, -20, 0x80000 | 0x20)
        self.root.attributes("-transparentcolor", WINDOW_BG_COLOR)
        self.root.attributes("-topmost", False)

    # === Data loading ===
    def _load_today_data(self):
        logger.info(f"Checking if there is an entry for {str(date.today())}")
        data = self.manager.get_today()
        if data:
            logger.info(f"Data found: noun {data['noun']}, verb: {data['verb']}")
            return data

        logger.info("Data not found, generating new")
        noun = self.manager.random_noun()
        verb = self.manager.random_verb()
        conj = self.manager.conjugation(verb.spanish)
        data = {"noun": noun.__dict__, "verb": verb.__dict__, "conjugation": conj}
        self.manager.save_today(noun, verb, conj)
        return data

    # === Display ===
    def display_data(self, data):
        for w in self.main_frame.winfo_children():
            w.destroy()

        self._build_frame(
            "Random noun", data["noun"]["spanish"].upper(), data["noun"]["english"]
        )
        self._build_frame(
            "Random verb", data["verb"]["spanish"].upper(), data["verb"]["english"]
        )
        self._build_conjugation_table(data["conjugation"])

    def _build_frame(self, title, content_top, content_bottom):
        f = tk.Frame(
            self.main_frame,
            bg=FRAME_COLOR,
            bd=FRAME_BORDER_WIDTH,
            relief=FRAME_RELIEF,
            padx=FRAME_PADX,
            pady=FRAME_PADY,
        )
        tk.Label(f, text=title, font=TITLE_FONT, bg=FRAME_COLOR, fg=TEXT_COLOR).pack(
            anchor="w"
        )
        tk.Frame(f, height=SEPARATOR_HEIGHT, bg=SEPARATOR_COLOR).pack(
            fill="x", pady=SEPARATOR_PADY
        )
        tk.Label(
            f, text=content_top, font=SUBTITLE_FONT, bg=FRAME_COLOR, fg=TEXT_COLOR
        ).pack(anchor="w")
        tk.Frame(f, height=SEPARATOR_HEIGHT, bg=SEPARATOR_COLOR).pack(
            fill="x", pady=SEPARATOR_PADY
        )
        tk.Label(
            f, text=content_bottom, font=CONTENT_FONT, bg=FRAME_COLOR, fg=TEXT_COLOR
        ).pack(anchor="w")
        f.pack(fill="x", padx=SECTION_PADX, pady=SECTION_PADY)

    def _build_conjugation_table(self, conjugation):
        conj_frame = tk.Frame(
            self.main_frame,
            bg=BG_COLOR,
            bd=FRAME_BORDER_WIDTH,
            relief=FRAME_RELIEF,
            padx=FRAME_PADX,
            pady=FRAME_PADY,
        )
        tk.Label(
            conj_frame,
            text="Conjugation",
            font=CONJUGATION_HEADER_FONT,
            bg=BG_COLOR,
            fg=TEXT_COLOR,
        ).grid(row=0, column=0, columnspan=len(conjugation[0]), pady=(0, SECTION_PADY))

        self.row_widgets = []
        self.active_col = None

        for i, row in enumerate(conjugation[:10]):
            row_labels = []
            for j, cell in enumerate(row):
                label = tk.Label(
                    conj_frame,
                    text=cell,
                    font=CONJUGATION_CELLS_FONT,
                    bg=BG_COLOR,
                    fg=TEXT_COLOR,
                    borderwidth=CELL_BORDER_WIDTH,
                    relief=CELL_RELIEF,
                    padx=CELL_PADX,
                    pady=CELL_PADY,
                    width=CELL_WIDTH,
                )
                label.grid(row=i + 1, column=j, sticky="nsew")
                conj_frame.grid_columnconfigure(j, weight=1)

                label.bind("<Button-1>", lambda e, c=j: self.highlight_column(c))
                row_labels.append(label)
            self.row_widgets.append(row_labels)

        conj_frame.pack(fill="x", padx=SECTION_PADX, pady=SECTION_PADY)

    # === Highlighting ===
    def highlight_column(self, col_index):
        """Toggle highlight for the clicked column."""
        if self.active_col == col_index:
            for row in self.row_widgets:
                for label in row:
                    label.config(bg=BG_COLOR, font=CONJUGATION_CELLS_FONT)
            self.active_col = None
            return

        for row in self.row_widgets:
            for j, label in enumerate(row):
                if j == col_index:
                    label.config(
                        bg=HIGHLIGHTED_CELL_COLOR,
                        font=(FONT_NAME, CELL_SIZE, "bold"),
                    )
                else:
                    label.config(bg=BG_COLOR, font=CONJUGATION_CELLS_FONT)

        self.active_col = col_index

    # === Quiz ===
    def schedule_quiz(self, noun):
        if self._quiz_job:
            self.root.after_cancel(self._quiz_job)
            self._quiz_job = None
        if not self.quiz_enabled:
            return
        self._quiz_job = self.root.after(
            self.quiz_interval * MS_IN_SECOND,
            lambda: (QuizDialog(self.root, noun), self.schedule_quiz(noun)),
        )

    def set_quiz_enabled(self, enabled: bool):
        self.quiz_enabled = enabled
        today = self.manager.get_today()
        if today:
            self.schedule_quiz(today["noun"])

    def set_quiz_interval(self, seconds: int):
        self.quiz_interval = seconds
        today = self.manager.get_today()
        if today:
            self.schedule_quiz(today["noun"])

    # === Lifecycle ===
    def quit(self):
        self.root.quit()
        self.root.destroy()

    def run(self):
        self.root.mainloop()
