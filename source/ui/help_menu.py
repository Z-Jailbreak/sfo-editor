from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QSizePolicy, QScrollArea, QTextBrowser
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont
import qtawesome as qta

from functions.help import load_help_docs
from functions.language_manager import get_saved_language
from ui.base_menu import BaseMenu


class HelpMenu(BaseMenu):
    def __init__(self, parent=None):
        super().__init__(parent, title_key="help_title", icon_name="fa5s.question-circle")
        self.current_option = None
        self.docs = []
        self.main_scroll = None
        self.submenu_scroll = None
        self.main_container = None
        self.submenu_container = None
        self.main_layout = None
        self.submenu_layout = None
        self.stack = None
        self.setup_ui()

    def lang(self):
        config_file = getattr(self.main_window, "config_file", None)
        if config_file:
            return get_saved_language(config_file) or "en"
        return "en"

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

        self.refresh_docs()
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

    def refresh_docs(self):
        self.docs = load_help_docs(self.lang())

    def create_main_options(self):
        self.clear_layout(self.main_layout)

        if not self.docs:
            empty = QLabel(self.text("help_empty", ""))
            empty.setAlignment(Qt.AlignCenter)
            empty.setStyleSheet("color: #aaa; font-size: 13px;")
            self.main_layout.addWidget(empty)
            self.main_layout.addStretch()
            return

        for doc in self.docs:
            option_button = QPushButton()
            option_button.setObjectName("optionButton")
            option_button.setProperty("doc_id", doc["id"])
            option_button.setMinimumHeight(70)
            option_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
            option_button.setStyleSheet(self.option_button_style())

            button_layout = QHBoxLayout()
            button_layout.setContentsMargins(20, 15, 20, 15)
            button_layout.setSpacing(15)

            icon_label = QLabel()
            fa_icon = qta.icon("fa5s.file-alt", color='white')
            icon_label.setPixmap(fa_icon.pixmap(QSize(32, 32)))
            icon_label.setStyleSheet("background: transparent;")

            text_layout = QVBoxLayout()
            text_layout.setSpacing(5)

            title_label = QLabel(doc["title"])
            title_label.setFont(QFont("Arial", 14, QFont.Bold))
            title_label.setStyleSheet("color: white; background: transparent;")

            text_layout.addWidget(title_label)

            if doc["description"]:
                desc_label = QLabel(doc["description"])
                desc_label.setFont(QFont("Arial", 11))
                desc_label.setStyleSheet("color: #aaa; background: transparent;")
                text_layout.addWidget(desc_label)

            button_layout.addWidget(icon_label)
            button_layout.addLayout(text_layout, 1)
            button_layout.addStretch()

            option_button.setLayout(button_layout)
            option_button.clicked.connect(
                lambda checked, doc_id=doc["id"]: self.show_doc(doc_id)
            )

            self.main_layout.addWidget(option_button)

        self.main_layout.addStretch()

    def option_button_style(self):
        return """
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

    def show_doc(self, doc_id):
        doc = next((d for d in self.docs if d["id"] == doc_id), None)
        if doc is None:
            return

        self.current_option = doc_id
        self.submenu_title.setText(doc["title"])

        self.clear_layout(self.submenu_layout)

        back_to_main = self.make_back_to_main_button()
        self.submenu_layout.addWidget(back_to_main)

        viewer = QTextBrowser()
        viewer.setObjectName("markdownViewer")
        viewer.setOpenExternalLinks(True)
        viewer.setReadOnly(True)
        viewer.setMinimumHeight(400)
        viewer.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        viewer.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        viewer.setStyleSheet(self.markdown_viewer_style())
        viewer.setMarkdown(doc["content"])

        self.submenu_layout.addWidget(viewer, 1)

        self.main_scroll.hide()
        self.submenu_scroll.show()

    def markdown_viewer_style(self):
        return """
            QTextBrowser#markdownViewer {
                background-color: #252526;
                color: #e0e0e0;
                border: 2px solid #3c3c3c;
                border-radius: 12px;
                padding: 16px;
                font-size: 13px;
            }
            QTextBrowser#markdownViewer a { color: #4da3ff; }
        """

    def show_main_menu(self):
        self.current_option = None
        self.retranslate_title()
        self.submenu_scroll.hide()
        self.main_scroll.show()

    def retranslate(self):
        self.refresh_docs()
        self.create_main_options()

        if self.current_option and any(
            d["id"] == self.current_option for d in self.docs
        ):
            self.show_doc(self.current_option)
        else:
            self.current_option = None
            self.retranslate_title()
            self.submenu_scroll.hide()
            self.main_scroll.show()

    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()