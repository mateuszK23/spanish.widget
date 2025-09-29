import tkinter as tk
import random

BG_COLOR = "#2e2e2e"
TEXT_COLOR = "#f9f9f9"

CLOSE_TIME_AFTER_RESPONSE = 750


class QuizDialog(tk.Toplevel):
    def __init__(self, parent, noun):
        super().__init__(parent)
        self.title("Quiz Time!")
        self.config(bg=BG_COLOR)
        self.geometry("400x200")
        self.resizable(False, False)

        # Center window
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - 200
        y = (self.winfo_screenheight() // 2) - 100
        self.geometry(f"+{x}+{y}")

        # Question
        ask_for = random.choice(["spanish", "english"])

        if ask_for == "spanish":
            self.question = f"Translate '{noun['english']}' to Spanish:"
            self.answer = noun["spanish"]
        else:
            self.question = f"Translate '{noun['spanish']}' to English:"
            self.answer = noun["english"]

        tk.Label(
            self,
            text=self.question,
            font=("Arial", 13, "bold"),
            bg=BG_COLOR,
            fg=TEXT_COLOR,
            wraplength=380,
            justify="center",
        ).pack(pady=15)

        self.entry_var = tk.StringVar()
        entry = tk.Entry(
            self,
            textvariable=self.entry_var,
            font=("Arial", 12),
            bg="#444",
            fg="white",
            insertbackground="white",
            justify="center",
        )
        entry.pack(pady=10, ipadx=5, ipady=5)
        entry.focus()

        self.feedback = tk.Label(
            self, text="", font=("Arial", 11), bg=BG_COLOR, fg="#ccc"
        )
        self.feedback.pack(pady=5)

        tk.Button(
            self,
            text="Submit",
            command=self.check_answer,
            bg="#555",
            fg="white",
            font=("Arial", 11, "bold"),
            relief="flat",
            padx=15,
            pady=5,
        ).pack(pady=10)

        self.bind("<Return>", lambda e: self.check_answer())

    def check_answer(self):
        user_ans = self.entry_var.get().strip().lower()
        if user_ans == self.answer.strip().lower():
            self.feedback.config(text="✅ Correct!", fg="#4CAF50")
        else:
            self.feedback.config(text=f"❌ Wrong! Correct: {self.answer}", fg="#FF5252")
        self.after(CLOSE_TIME_AFTER_RESPONSE, self.destroy)
