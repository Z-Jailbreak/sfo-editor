from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QSizePolicy, QScrollArea, QCheckBox
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont
import qtawesome as qta

from functions.language_manager import save_language
from functions.backup import get_backup_option, save_backup_option
from ui.base_menu import BaseMenu

OPTIONS = [
    ("language", "fa5s.cog"),
    ("backup", "fa5s.database"),
]

SUBOPTIONS = {
    "language": ["en", "es"]
}

BACKUP_OPTIONS = [
    ("backup_modify_sfo_title", "backup_modify_sfo", "fa5s.database"),
    ("backup_config_title", "backup_config", "fa5s.database"),
]

SUB_OPTION_STYLE = """
    QPushButton#subOptionButton {
        background-color: #2d2d2d;
        border: 2px solid #3c3c3c;
        border-radius: 12px;
        text-align: left;
    }
    QPushButton#subOptionButton:hover {
        background-color: #3c3c3c;
        border: 2px solid #0078d4;
    }
    QPushButton#subOptionButton:pressed {
        background-color: #0078d4;
    }
"""

SWITCH_STYLE = """
    QCheckBox {
        width: 52px;
        height: 28px;
        spacing: 0px;
        border: 1px solid #2a2a2a;
        border-radius: 14px;
        background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #4a4a4a, stop:1 #333333);
    }
    QCheckBox::indicator {
        width: 22px;
        height: 22px;
        border-radius: 11px;
        border: 1px solid #a8a8a8;
        background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #ffffff, stop:1 #e4e4e4);
        margin: 2px 3px 2px 3px;
    }
    QCheckBox:checked {
        border: 1px solid #005a9e;
        background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #3aa2ee, stop:0.5 #0078d4, stop:1 #0062b1);
    }
    QCheckBox::indicator:checked {
        margin: 2px 3px 2px 27px;
        border: 1px solid #d0d0d0;
        background-color: #ffffff;
    }
"""

MAIN_OPTION_STYLE = """
    QPushButton#optionButton {
        background-color: #2d2d2d;
        border: 2px solid #3c3c3c;
        border-radius: 12px;
        text-align: left;
    }
    QPushButton#optionButton:hover {
        background-color: #3c3c3c;
        border: 2px solid #0078d4;
    }
    QPushButton#optionButton:pressed {
        background-color: #0078d4;
    }
"""


class SettingsMenu(BaseMenu):
    def __init__(self, parent=None):
        super().__init__(parent, title_key="settings_title", icon_name="fa5s.cog")
        self.current_option = None
        self.main_scroll = None
        self.submenu_scroll = None
        self.main_container = None
        self.submenu_container = None
        self.main_layout = None
        self.submenu_layout = None
        self.stack = None
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        self.add_top_bar_to_layout(main_layout)

        self.stack = QVBoxLayout()

        self.main_scroll = self.create_scroll_area()
        self.main_container = QWidget()
        self.main_container.setStyleSheet("background-color: transparent;")
        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(15)
        self.main_layout.setContentsMargins(0, 10, 0, 20)
        self.main_container.setLayout(self.main_layout)
        self.main_scroll.setWidget(self.main_container)

        self.submenu_scroll = self.create_scroll_area()
        self.submenu_container = QWidget()
        self.submenu_container.setStyleSheet("background-color: transparent;")
        self.submenu_layout = QVBoxLayout()
        self.submenu_layout.setSpacing(15)
        self.submenu_layout.setContentsMargins(0, 10, 0, 20)
        self.submenu_container.setLayout(self.submenu_layout)
        self.submenu_scroll.setWidget(self.submenu_container)

        self.submenu_scroll.hide()

        self.stack.addWidget(self.main_scroll)
        self.stack.addWidget(self.submenu_scroll)

        main_layout.addLayout(self.stack, 1)

        self.setLayout(main_layout)
        self.setStyleSheet("QWidget { background-color: #1e1e1e; }")

        self.create_main_options()

    def create_scroll_area(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollArea > QWidget > QWidget {
                background-color: transparent;
            }
        """)
        return scroll

    def create_main_options(self):
        for key, icon_name in OPTIONS:
            option_button = QPushButton()
            option_button.setObjectName("optionButton")
            option_button.setMinimumHeight(70)
            option_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
            option_button.setStyleSheet(MAIN_OPTION_STYLE)

            button_layout = QHBoxLayout()
            button_layout.setContentsMargins(20, 15, 20, 15)
            button_layout.setSpacing(15)

            icon_label = QLabel()
            fa_icon = qta.icon(icon_name, color='white')
            icon_pixmap = fa_icon.pixmap(QSize(32, 32))
            icon_label.setPixmap(icon_pixmap)
            icon_label.setStyleSheet("background: transparent;")

            text_layout = QVBoxLayout()
            text_layout.setSpacing(5)

            title_label = QLabel(self.text(f"opt_{key}", ""))
            title_label.setFont(QFont("Arial", 14, QFont.Bold))
            title_label.setStyleSheet("color: white; background: transparent;")
            title_label.setProperty("text_key", f"opt_{key}")

            desc_label = QLabel(self.text(f"opt_{key}_desc", ""))
            desc_label.setFont(QFont("Arial", 11))
            desc_label.setStyleSheet("color: #aaa; background: transparent;")
            desc_label.setProperty("text_key", f"opt_{key}_desc")

            text_layout.addWidget(title_label)
            text_layout.addWidget(desc_label)

            button_layout.addWidget(icon_label)
            button_layout.addLayout(text_layout, 1)
            button_layout.addStretch()

            option_button.setLayout(button_layout)

            option_button.clicked.connect(
                lambda checked, opt_key=key: self.show_submenu(opt_key)
            )

            self.main_layout.addWidget(option_button)

        self.main_layout.addStretch()

    def show_submenu(self, option_key):
        self.current_option = option_key
        self.submenu_title.setText(self.text(f"opt_{option_key}", ""))

        self.clear_layout(self.submenu_layout)

        back_to_main = self.make_back_to_main_button()
        self.submenu_layout.addWidget(back_to_main)

        if option_key == "backup":
            self.add_backup_options()

        parent_icon = dict(OPTIONS).get(option_key, "fa5s.folder")
        for sub_key in SUBOPTIONS.get(option_key, []):
            sub_title = self.text(f"sub_{option_key}_{sub_key}", "")
            sub_description = self.text(f"sub_{option_key}_{sub_key}_desc", "")

            sub_button = QPushButton()
            sub_button.setObjectName("subOptionButton")
            sub_button.setMinimumHeight(65)
            sub_button.setStyleSheet(SUB_OPTION_STYLE)

            sub_layout = QHBoxLayout()
            sub_layout.setContentsMargins(20, 15, 20, 15)
            sub_layout.setSpacing(15)

            sub_icon_label = QLabel()
            sub_fa_icon = qta.icon(parent_icon, color='white')
            sub_pixmap = sub_fa_icon.pixmap(QSize(30, 30))
            sub_icon_label.setPixmap(sub_pixmap)
            sub_icon_label.setStyleSheet("background: transparent;")

            sub_text_layout = QVBoxLayout()
            sub_text_layout.setSpacing(5)

            sub_title_label = QLabel(sub_title)
            sub_title_label.setFont(QFont("Arial", 13, QFont.Bold))
            sub_title_label.setStyleSheet("color: white; background: transparent;")

            sub_desc_label = QLabel(sub_description)
            sub_desc_label.setFont(QFont("Arial", 11))
            sub_desc_label.setStyleSheet("color: #aaa; background: transparent;")

            sub_text_layout.addWidget(sub_title_label)
            sub_text_layout.addWidget(sub_desc_label)

            sub_layout.addWidget(sub_icon_label)
            sub_layout.addLayout(sub_text_layout, 1)
            sub_layout.addStretch()

            sub_button.setLayout(sub_layout)
            sub_button.clicked.connect(lambda checked, opt=sub_key: self.select_suboption(opt))

            self.submenu_layout.addWidget(sub_button)

        self.submenu_layout.addStretch()

        self.main_scroll.hide()
        self.submenu_scroll.show()

    def show_main_menu(self):
        self.current_option = None
        self.retranslate_title()
        self.submenu_scroll.hide()
        self.main_scroll.show()

    def add_backup_options(self):
        for title_key, ini_key, icon_name in BACKUP_OPTIONS:
            self.submenu_layout.addWidget(
                self.make_switch_row(title_key, ini_key, icon_name))

    def make_switch_row(self, title_key, ini_key, icon_name):
        button = QPushButton()
        button.setObjectName("subOptionButton")
        button.setMinimumHeight(70)
        button.setStyleSheet(SUB_OPTION_STYLE)

        layout = QHBoxLayout()
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(15)

        icon_label = QLabel()
        icon_label.setPixmap(qta.icon(icon_name, color="white").pixmap(QSize(30, 30)))
        icon_label.setStyleSheet("background: transparent;")

        title_label = QLabel(self.text(title_key, ""))
        title_label.setFont(QFont("Arial", 13, QFont.Bold))
        title_label.setStyleSheet("color: white; background: transparent;")

        switch = QCheckBox()
        switch.setStyleSheet(SWITCH_STYLE)
        switch.setFixedSize(54, 30)
        switch.setChecked(get_backup_option(ini_key))
        switch.setAttribute(Qt.WA_TransparentForMouseEvents)

        layout.addWidget(icon_label)
        layout.addWidget(title_label)
        layout.addStretch()
        layout.addWidget(switch)
        button.setLayout(layout)

        button.clicked.connect(lambda: switch.setChecked(not switch.isChecked()))
        switch.stateChanged.connect(
            lambda state, key=ini_key: save_backup_option(key, state == Qt.Checked))
        return button

    def retranslate(self):
        if self.current_option:
            self.show_submenu(self.current_option)
        else:
            self.retranslate_title()
            for i in range(self.main_layout.count()):
                widget = self.main_layout.itemAt(i).widget()
                if widget:
                    for child in widget.findChildren(QLabel):
                        key = child.property("text_key")
                        if key:
                            child.setText(self.text(key, ""))

    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def select_suboption(self, code):
        if self.main_window is None:
            return

        save_language(self.main_window.config_file, code)
        self.main_window.apply_language()