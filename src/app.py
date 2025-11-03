from datetime import date
from PySide6 import QtUiTools, QtCore, QtWidgets, QtGui
from PySide6.QtWidgets import (
    QMenu,
    QHeaderView,
    QDialog,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QCheckBox,
    QSpinBox,
    QHBoxLayout,
)
from PySide6.QtGui import QAction

from data_manager import DailyDataManager
from quiz import QuizDialog
from tray import TrayController
from logger import logger
from settings_manager import load_settings, save_settings
from utils import center_on_screen
from paths import MAIN_WIDGET_UI

MS_IN_SECOND = 1000


class SettingsDialog(QDialog):
    """Simple Qt settings window replacing tkinter settings"""

    def __init__(self, parent, quiz_enabled, quiz_interval):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.setFixedSize(300, 180)

        layout = QVBoxLayout(self)
        title = QLabel("<b>Settings</b>")
        layout.addWidget(title)

        self.chk_quiz = QCheckBox("Enable Quizzes")
        self.chk_quiz.setChecked(quiz_enabled)
        layout.addWidget(self.chk_quiz)

        interval_layout = QHBoxLayout()
        lbl = QLabel("Quiz Interval (seconds):")
        interval_layout.addWidget(lbl)
        self.spin_interval = QSpinBox()
        self.spin_interval.setRange(1, 3600)
        self.spin_interval.setValue(quiz_interval)
        interval_layout.addWidget(self.spin_interval)
        layout.addLayout(interval_layout)

        btn_save = QPushButton("Save & Close")
        btn_save.clicked.connect(self.accept)
        layout.addWidget(btn_save)

    @property
    def quiz_enabled(self):
        return self.chk_quiz.isChecked()

    @property
    def quiz_interval(self):
        return self.spin_interval.value()


class SpanishWidget(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        logger.info("Starting SpanishWidget")
        self.manager = DailyDataManager()

        # Load UI
        loader = QtUiTools.QUiLoader()
        ui_file = QtCore.QFile(MAIN_WIDGET_UI)
        ui_file.open(QtCore.QFile.ReadOnly)
        self.ui = loader.load(ui_file, self)
        ui_file.close()
        self.setCentralWidget(self.ui)

        # Connect widgets
        self.conjugationTable = self.findChild(
            QtWidgets.QTableWidget, "conjugationTable"
        )

        # Load settings
        settings = load_settings()
        self.quiz_enabled = settings["quiz_enabled"]
        self.quiz_interval = settings["quiz_interval"]
        self.tense_filters = settings.get("tense_filters", {})
        self._quiz_timer = None

        logger.info(f"Loaded settings: {settings}")

        # System tray (pure Qt)
        self.tray = TrayController(self)
        self.tray.start()

        # Load today's data
        data = self._load_today_data()
        self.display_data(data)
        self.schedule_quiz(data["noun"])

        # Setup UI behavior
        self.populate_filter_menu()

        # Drag events
        self.ui.dragButton.pressed.connect(self.start_drag)
        self.ui.dragButton.released.connect(self.end_drag)

    def start_drag(self):
        self._drag_active = True
        self._drag_offset = QtGui.QCursor.pos() - self.frameGeometry().topLeft()
        QtWidgets.QApplication.instance().installEventFilter(self)

    def end_drag(self):
        self._drag_active = False
        QtWidgets.QApplication.instance().removeEventFilter(self)

    def eventFilter(self, obj, event):
        if self._drag_active and event.type() == QtCore.QEvent.MouseMove:
            cursor_pos = QtGui.QCursor.pos()
            self.move(cursor_pos - self._drag_offset)
            return True
        return super().eventFilter(obj, event)

    # === Data management ===
    def _generate_data(self):
        noun = self.manager.random_noun()
        verb = self.manager.random_verb()
        conj = self.manager.conjugation(verb.spanish)
        return {"noun": noun.__dict__, "verb": verb.__dict__, "conjugation": conj}

    def _load_today_data(self):
        logger.info(f"Checking for existing entry on {date.today()}")
        data = self.manager.get_today()
        if data:
            logger.info(f"Data for {date.today()} found!")
            return data
        logger.info("No data found, generating new entry")
        generated = self._generate_data()
        self.manager.save_today(
            generated["noun"], generated["verb"], generated["conjugation"]
        )
        return generated

    def regenerate_data_for_today(self):
        generated = self._generate_data()
        self.manager.save_today(
            generated["noun"], generated["verb"], generated["conjugation"]
        )
        self.display_data(generated)
        self.schedule_quiz(generated["noun"])

    # === UI Display ===
    def display_data(self, data):
        noun_data = data["noun"]
        verb_data = data["verb"]
        conjugation = data["conjugation"]

        self.populate_words_data(noun_data, verb_data)
        self.populate_conjugation_table(conjugation)

    def populate_words_data(self, noun_data, verb_data):
        self.ui.nounSpanishLabel.setText(noun_data["spanish"].upper())
        self.ui.nounEnglishLabel.setText(noun_data["english"])
        self.ui.verbSpanishLabel.setText(verb_data["spanish"].upper())
        self.ui.verbEnglishLabel.setText(verb_data["english"])

    def populate_conjugation_table(self, conjugation):
        filtered_conjugation = [
            row for row in conjugation if not (row and "vosotros" in row[0].lower())
        ]

        rows = len(filtered_conjugation) - 1
        cols = len(filtered_conjugation[0]) - 1

        table = self.conjugationTable
        table.clear()
        table.setRowCount(rows)
        table.setColumnCount(cols)
        table.setHorizontalHeaderLabels(filtered_conjugation[0][1:])

        vertical_headers = []
        for i, row_data in enumerate(filtered_conjugation[1:]):
            for j, cell in enumerate(row_data):
                if j == 0:
                    vertical_headers.append(cell)
                    continue
                item = QtWidgets.QTableWidgetItem(cell)
                table.setItem(i, j - 1, item)

        table.setVerticalHeaderLabels(vertical_headers)
        table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.last_clicked = None
        self.setup_table_signals()

    def setup_table_signals(self):
        table = self.conjugationTable
        table.itemSelectionChanged.connect(self.update_bold_selected_cells)
        table.cellClicked.connect(self.on_cell_clicked)

    def on_cell_clicked(self, row, column):
        item = self.conjugationTable.item(row, column)
        if not item:
            return
        index = (row, column)
        if getattr(self, "last_clicked", None) == index and item.isSelected():
            QtCore.QTimer.singleShot(0, self.conjugationTable.clearSelection)
            self.last_clicked = None
        else:
            self.last_clicked = index

    def update_bold_selected_cells(self):
        table = self.conjugationTable
        selected = set((i.row(), i.column()) for i in table.selectedIndexes())

        for i in range(table.rowCount()):
            for j in range(table.columnCount()):
                item = table.item(i, j)
                if not item:
                    continue
                font = item.font()
                font.setBold((i, j) in selected)
                item.setFont(font)

    def populate_filter_menu(self):
        menu = QMenu(self)
        self.filter_actions = {}

        for tense in ["Present", "Preterite", "Imperfect", "Conditional", "Future"]:
            action = QAction(tense, menu)
            action.setCheckable(True)
            # Use saved filter state
            action.setChecked(self.tense_filters.get(tense, True))
            action.triggered.connect(
                lambda checked, t=tense: self.toggle_tense(t, checked)
            )
            menu.addAction(action)
            self.filter_actions[tense] = action

        menu.aboutToShow.connect(lambda: self.conjugationTable.clearSelection())
        self.ui.filterButton.setMenu(menu)

        # Apply filters on startup
        for tense, checked in self.tense_filters.items():
            self.toggle_tense(tense, checked)

    def toggle_tense(self, tense, checked):
        col_map = {
            "Present": 0,
            "Preterite": 1,
            "Imperfect": 2,
            "Conditional": 3,
            "Future": 4,
        }
        if tense in col_map:
            self.conjugationTable.setColumnHidden(col_map[tense], not checked)

        # Save the change to settings
        self.tense_filters[tense] = checked
        save_settings(self.quiz_enabled, self.quiz_interval, self.tense_filters)

    # === Quiz ===
    def schedule_quiz(self, noun):
        if self._quiz_timer:
            self._quiz_timer.stop()
        if not self.quiz_enabled:
            return

        self._quiz_timer = QtCore.QTimer(self)
        self._quiz_timer.setSingleShot(True)
        self._quiz_timer.timeout.connect(
            lambda: (QuizDialog(self, noun), self.schedule_quiz(noun))
        )
        self._quiz_timer.start(self.quiz_interval * MS_IN_SECOND)

    def set_quiz_enabled(self, enabled):
        self.quiz_enabled = enabled
        today = self.manager.get_today()
        if today:
            self.schedule_quiz(today["noun"])

    def set_quiz_interval(self, seconds):
        self.quiz_interval = seconds
        today = self.manager.get_today()
        if today:
            self.schedule_quiz(today["noun"])

    def open_settings(self):
        dlg = SettingsDialog(self, self.quiz_enabled, self.quiz_interval)
        center_on_screen(dlg)
        if dlg.exec() == QDialog.Accepted:
            self.quiz_enabled = dlg.quiz_enabled
            self.quiz_interval = dlg.quiz_interval
            save_settings(self.quiz_enabled, self.quiz_interval)
            today = self.manager.get_today()
            if today:
                self.schedule_quiz(today["noun"])

    def quit(self):
        QtWidgets.QApplication.quit()
