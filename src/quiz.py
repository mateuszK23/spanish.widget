from PySide6 import QtWidgets, QtCore
from utils import center_on_screen
import random

CLOSE_TIME_AFTER_RESPONSE = 750


class QuizDialog(QtWidgets.QDialog):
    def __init__(self, parent, noun: dict):
        super().__init__(parent)
        self.setWindowTitle("Quiz Time!")
        self.setModal(False)
        self.setFixedSize(420, 200)

        ask_for = random.choice(["spanish", "english"])
        if ask_for == "spanish":
            question_text = f"Translate '{noun['english']}' to Spanish:"
            self.answer = noun["spanish"]
        else:
            question_text = f"Translate '{noun['spanish']}' to English:"
            self.answer = noun["english"]

        layout = QtWidgets.QVBoxLayout(self)

        label = QtWidgets.QLabel(question_text)
        label.setWordWrap(True)
        label.setAlignment(QtCore.Qt.AlignCenter)
        label.setStyleSheet("font-weight: bold; font-size: 13px;")
        layout.addWidget(label)

        self.entry = QtWidgets.QLineEdit()
        self.entry.setPlaceholderText("Type your answer and press Enter")
        self.entry.returnPressed.connect(self.check_answer)
        layout.addWidget(self.entry)

        self.feedback = QtWidgets.QLabel("")
        self.feedback.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.feedback)

        submit_btn = QtWidgets.QPushButton("Submit")
        submit_btn.clicked.connect(self.check_answer)
        layout.addWidget(submit_btn, alignment=QtCore.Qt.AlignCenter)

        self.entry.setFocus()
        self.show()
        center_on_screen(self)

    def check_answer(self):
        user_ans = self.entry.text().strip().lower()
        if user_ans == self.answer.strip().lower():
            self.feedback.setText("✅ Correct!")
            self.feedback.setStyleSheet("color: #4CAF50;")
        else:
            self.feedback.setText(f"❌ Wrong! Correct: {self.answer}")
            self.feedback.setStyleSheet("color: #FF5252;")
        QtCore.QTimer.singleShot(CLOSE_TIME_AFTER_RESPONSE, self.accept)
