import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QApplication,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from functions.language_manager import get_saved_language, save_language


class LanguageManager(QWidget):
    def __init__(self, config_path):
        super().__init__()
        self.config_path = config_path
        self.selected_language = None
        self.language_buttons = {}
        self.setup_ui()
        self.setup_styles()
        self.adjustSize()
        self.setFixedSize(420, self.height())

    def setup_ui(self):
        self.setWindowTitle("SFO Save Editor - Language Selection")
        self.setWindowFlags(Qt.WindowCloseButtonHint)

        layout = QVBoxLayout()
        layout.setContentsMargins(24, 16, 24, 16)
        layout.setSpacing(10)
        self.setLayout(layout)

        title = QLabel("Language Selection")
        title.setAlignment(Qt.AlignCenter)
        title.setObjectName("title")

        underline = QFrame()
        underline.setObjectName("underline")
        underline.setFixedHeight(2)

        layout.addWidget(title)
        layout.addWidget(underline)

        desc = QLabel("Please select your preferred language:")
        desc.setAlignment(Qt.AlignCenter)
        desc.setObjectName("description")
        desc.setFont(QFont("Arial", 10))
        layout.addWidget(desc)

        grid = QGridLayout()
        grid.setSpacing(10)
        grid.setContentsMargins(0, 22, 0, 0)

        languages = [("Spanish", "es"), ("English", "en")]

        for i, (text, code) in enumerate(languages):
            btn = QPushButton(text)
            btn.setCheckable(True)
            btn.setObjectName("langButton")
            btn.setFixedHeight(38)
            btn.clicked.connect(lambda _, c=code, b=btn: self.select_language(c, b))
            self.language_buttons[code] = btn
            grid.addWidget(btn, i // 2, i % 2)

        layout.addLayout(grid)
        layout.addSpacing(16)

        btn_container = QHBoxLayout()
        btn_container.setSpacing(10)

        self.accept_btn = QPushButton("\u2714 Accept")
        self.accept_btn.setObjectName("acceptButton")
        self.accept_btn.setFixedHeight(36)
        self.accept_btn.clicked.connect(self.accept_language)

        self.cancel_btn = QPushButton("\u2716 Cancel")
        self.cancel_btn.setObjectName("cancelButton")
        self.cancel_btn.setFixedHeight(36)
        self.cancel_btn.clicked.connect(self.cancel_selection)

        btn_container.addWidget(self.accept_btn)
        btn_container.addWidget(self.cancel_btn)
        btn_container.setStretch(0, 1)
        btn_container.setStretch(1, 1)
        layout.addLayout(btn_container)

    def setup_styles(self):
        self.setStyleSheet("""
            QWidget { background-color: #1e1e1e; color: #ffffff; }
            QLabel#title { font-size: 15px; font-weight: bold; }
            #underline { background-color: #0078d4; }
            QLabel#description { color: #b0b0b0; font-size: 11px; }
            QPushButton#langButton {
                background-color: #2d2d2d; border: 2px solid #3c3c3c;
                border-radius: 6px; padding: 4px; font-weight: bold;
                font-size: 13px;
            }
            QPushButton#langButton:hover { border: 2px solid #0078d4; }
            QPushButton#langButton:checked { background-color: #0078d4; border: 2px solid #0078d4; }
            QPushButton#acceptButton, QPushButton#cancelButton {
                background-color: #2d2d2d; border: 2px solid #3c3c3c; border-radius: 4px;
                font-size: 13px;
            }
            QPushButton#acceptButton:hover { border: 2px solid #0078d4; }
            QPushButton#acceptButton:pressed { background-color: #0078d4; }
            QPushButton#cancelButton:hover { border: 2px solid #ff4444; }
            QPushButton#cancelButton:pressed { background-color: #ff4444; }
        """)

    def select_language(self, code, button):
        for btn in self.language_buttons.values():
            btn.setChecked(False)
        button.setChecked(True)
        self.selected_language = code

    def accept_language(self):
        if not self.selected_language:
            QMessageBox.warning(self, "Warning", "Please select a language")
            return

        save_language(self.config_path, self.selected_language)
        self.close()

    def cancel_selection(self):
        if (
            QMessageBox.question(
                self,
                "Exit",
                "Are you sure you want to exit?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            == QMessageBox.Yes
        ):
            sys.exit(0)


def get_language(config_file):
    lang = get_saved_language(config_file)
    if lang:
        return lang

    app = QApplication.instance() or QApplication(sys.argv)

    manager = LanguageManager(config_file)
    manager.show()
    app.exec_()

    return manager.selected_language or sys.exit(0)