import os

import qtawesome as qta
from PyQt5.QtCore import QRect, QSize, Qt
from PyQt5.QtGui import QFont, QFontMetrics, QPixmap
from PyQt5.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from functions.backup import backup_modify_sfo
from functions.sfo import MAX_DESC, MAX_TITLE, apply_changes, query_value
from ui.base_menu import BaseMenu


class SfoMenu(BaseMenu):
    def __init__(self, parent=None):
        super().__init__(parent, title_key="sfo_title", icon_name="fa5s.file-signature")
        self.sfo_path = ""
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(10)

        self.add_top_bar_to_layout(main_layout)

        columns = QHBoxLayout()
        columns.setContentsMargins(0, 0, 0, 0)
        columns.setSpacing(24)

        columns.addWidget(self.create_info_panel(), 0, Qt.AlignVCenter)
        columns.addWidget(self.create_form_panel(), 1, Qt.AlignVCenter)

        main_layout.addLayout(columns, 1)
        self.setLayout(main_layout)
        self.setStyleSheet(self.stylesheet())

    def create_info_panel(self):
        info_container = QWidget()
        info_container.setObjectName("infoContainer")
        info_container.setFixedWidth(340)

        info_layout = QVBoxLayout()
        info_layout.setContentsMargins(14, 10, 14, 10)
        info_layout.setSpacing(4)
        info_layout.addStretch(1)

        self.info_title = QLabel(self.text("sfo_info_title", ""))
        self.info_title.setProperty("text_key", "sfo_info_title")
        self.info_title.setAlignment(Qt.AlignCenter)
        self.info_title.setWordWrap(True)
        self.info_title.setFont(QFont("Arial", 16, QFont.Bold))
        self.info_title.setStyleSheet("color: white; background: transparent;")
        info_layout.addWidget(self.info_title)

        info_underline = QFrame()
        info_underline.setObjectName("infoUnderline")
        info_underline.setFixedHeight(2)
        info_underline.setStyleSheet("background-color: #6f6f6f;")
        info_layout.addWidget(info_underline)
        info_layout.addSpacing(6)

        self.name_caption = QLabel(self.text("sfo_info_name", ""))
        self.name_caption.setProperty("text_key", "sfo_info_name")
        self.name_caption.setFont(QFont("Arial", 12))
        self.name_caption.setStyleSheet("color: #aaa; background: transparent;")

        self.name_value = QLabel(self.text("sfo_info_none", "\u2014"))
        self.name_value.setFont(QFont("Arial", 15, QFont.Bold))
        self.name_value.setStyleSheet("color: white; background: transparent;")
        self.name_value.setWordWrap(True)
        self.name_value.setTextInteractionFlags(Qt.TextSelectableByMouse)

        info_layout.addWidget(self.name_caption)
        info_layout.addWidget(self.name_value)
        info_layout.addSpacing(4)

        self.subtitle_caption = QLabel(self.text("sfo_info_description", ""))
        self.subtitle_caption.setProperty("text_key", "sfo_info_description")
        self.subtitle_caption.setFont(QFont("Arial", 12))
        self.subtitle_caption.setStyleSheet("color: #aaa; background: transparent;")

        self.subtitle_value = QLabel(self.text("sfo_info_none", "\u2014"))
        self.subtitle_value.setFont(QFont("Arial", 13, QFont.Bold))
        self.subtitle_value.setStyleSheet("color: white; background: transparent;")
        self.subtitle_value.setWordWrap(True)
        self.subtitle_value.setFixedHeight(70)
        self.subtitle_value.setTextInteractionFlags(Qt.TextSelectableByMouse)

        info_layout.addWidget(self.subtitle_caption)
        info_layout.addWidget(self.subtitle_value)
        info_layout.addSpacing(4)

        self.title_id_caption = QLabel(self.text("sfo_info_title_id", ""))
        self.title_id_caption.setProperty("text_key", "sfo_info_title_id")
        self.title_id_caption.setFont(QFont("Arial", 12))
        self.title_id_caption.setStyleSheet("color: #aaa; background: transparent;")

        self.title_id_value = QLabel(self.text("sfo_info_none", "\u2014"))
        self.title_id_value.setFont(QFont("Arial", 16, QFont.Bold))
        self.title_id_value.setStyleSheet("color: white; background: transparent;")
        self.title_id_value.setTextInteractionFlags(Qt.TextSelectableByMouse)

        info_layout.addWidget(self.title_id_caption)
        info_layout.addWidget(self.title_id_value)
        info_layout.addSpacing(6)

        self.image_label = QLabel()
        self.image_label.setObjectName("gameImage")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setFixedSize(194, 108)
        self.image_label.setVisible(False)
        info_layout.addWidget(self.image_label, 0, Qt.AlignHCenter)

        self.image_missing = QLabel(self.text("sfo_info_no_image", ""))
        self.image_missing.setProperty("text_key", "sfo_info_no_image")
        self.image_missing.setAlignment(Qt.AlignCenter)
        self.image_missing.setWordWrap(True)
        self.image_missing.setFont(QFont("Arial", 12))
        self.image_missing.setStyleSheet("color: #aaa; background: transparent;")
        self.image_missing.setVisible(False)
        info_layout.addWidget(self.image_missing)

        info_layout.addStretch(2)
        info_container.setLayout(info_layout)
        return info_container

    def create_form_panel(self):
        form_container = QWidget()
        form_container.setMaximumWidth(560)

        form_layout = QVBoxLayout()
        form_layout.setContentsMargins(24, 0, 0, 0)
        form_layout.setSpacing(6)
        form_layout.addStretch(1)

        self.select_button = QPushButton()
        self.select_button.setObjectName("selectButton")
        self.select_button.setFixedHeight(46)

        select_layout = QHBoxLayout()
        select_layout.setSpacing(10)
        select_layout.setContentsMargins(0, 0, 0, 0)
        select_layout.setAlignment(Qt.AlignCenter)

        select_icon = QLabel()
        select_icon.setPixmap(qta.icon("fa5s.folder-open", color="white").pixmap(QSize(22, 22)))
        select_icon.setStyleSheet("background: transparent;")

        select_text = QLabel(self.text("sfo_select", ""))
        select_text.setProperty("text_key", "sfo_select")
        select_text.setFont(QFont("Arial", 14, QFont.Bold))
        select_text.setStyleSheet("color: white; background: transparent;")

        select_layout.addWidget(select_icon)
        select_layout.addWidget(select_text)
        self.select_button.setLayout(select_layout)
        self.select_button.clicked.connect(self.select_file)

        self.file_label = QLabel(self.text("sfo_no_file", ""))
        self.file_label.setAlignment(Qt.AlignCenter)
        self.file_label.setFont(QFont("Arial", 11))
        self.file_label.setStyleSheet("color: #aaa; background: transparent;")

        self.title_caption = QLabel(self.text("sfo_label_title", ""))
        self.title_caption.setProperty("text_key", "sfo_label_title")
        self.title_caption.setFont(QFont("Arial", 13, QFont.Bold))
        self.title_caption.setStyleSheet("color: white; background: transparent;")

        self.title_input = QLineEdit()
        self.title_input.setObjectName("sfoInput")
        self.title_input.setMaxLength(MAX_TITLE)

        self.description_caption = QLabel(self.text("sfo_label_desc", ""))
        self.description_caption.setProperty("text_key", "sfo_label_desc")
        self.description_caption.setFont(QFont("Arial", 13, QFont.Bold))
        self.description_caption.setStyleSheet("color: white; background: transparent;")

        self.description_input = QLineEdit()
        self.description_input.setObjectName("sfoInput")
        self.description_input.setMaxLength(MAX_DESC)

        self.apply_button = QPushButton()
        self.apply_button.setObjectName("applyButton")
        self.apply_button.setFixedHeight(52)
        self.apply_button.setFixedWidth(240)

        apply_layout = QHBoxLayout()
        apply_layout.setSpacing(10)
        apply_layout.setContentsMargins(0, 0, 0, 0)
        apply_layout.setAlignment(Qt.AlignCenter)

        apply_icon = QLabel()
        apply_icon.setPixmap(qta.icon("fa5s.check", color="white").pixmap(QSize(22, 22)))
        apply_icon.setStyleSheet("background: transparent;")

        apply_text = QLabel(self.text("sfo_apply", ""))
        apply_text.setProperty("text_key", "sfo_apply")
        apply_text.setFont(QFont("Arial", 14, QFont.Bold))
        apply_text.setStyleSheet("color: white; background: transparent;")

        apply_layout.addWidget(apply_icon)
        apply_layout.addWidget(apply_text)
        self.apply_button.setLayout(apply_layout)
        self.apply_button.clicked.connect(self.submit)

        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setFont(QFont("Arial", 12))
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet("color: #aaa; background: transparent;")

        form_layout.addWidget(self.select_button)
        form_layout.addWidget(self.file_label)
        form_layout.addSpacing(14)
        form_layout.addWidget(self.title_caption)
        form_layout.addWidget(self.title_input)
        form_layout.addSpacing(14)
        form_layout.addWidget(self.description_caption)
        form_layout.addWidget(self.description_input)
        form_layout.addSpacing(18)
        form_layout.addWidget(self.apply_button, 0, Qt.AlignHCenter)
        form_layout.addSpacing(8)
        form_layout.addWidget(self.status_label)
        form_layout.addStretch(2)

        form_container.setLayout(form_layout)
        return form_container

    def showEvent(self, event):
        super().showEvent(event)
        if not self.sfo_path:
            self.select_file()

    def select_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            self.text("sfo_select", ""),
            "",
            "param.sfo (param.sfo);;Archivos SFO (*.sfo);;Todos los archivos (*)",
        )

        if path:
            self.sfo_path = path
            self.file_label.setText("")
            backup_modify_sfo(getattr(self.main_window, "sfo_command", None), path)
        else:
            self.sfo_path = ""
            self.file_label.setText(self.text("sfo_no_file", ""))

        self.refresh_info()

    def submit(self):
        title = self.title_input.text().strip()
        description = self.description_input.text().strip()

        if not self.sfo_path:
            self.show_status(self.text("sfo_need_file", ""), "#ff5252")
            return

        sfo_command = getattr(self.main_window, "sfo_command", None)
        result = apply_changes(sfo_command, self.sfo_path, title, description)

        if result == "empty":
            self.show_status(self.text("sfo_empty", ""), "#aaa")
        elif result == "ok":
            self.refresh_info()
            self.show_status(self.text("sfo_success", ""), "#4caf50")
        else:
            self.refresh_info()
            self.show_status(self.text("sfo_error", ""), "#ff5252")

    def show_status(self, message, color):
        self.status_label.setText(message)
        self.status_label.setStyleSheet(f"color: {color}; background: transparent;")

    def refresh_info(self):
        sfo_command = getattr(self.main_window, "sfo_command", None)
        empty = self.text("sfo_info_none", "\u2014")

        if not self.sfo_path:
            self.name_value.setText(empty)
            self.subtitle_value.setText(empty)
            self.title_id_value.setText(empty)
            self.image_label.clear()
            self.image_label.setVisible(False)
            self.image_missing.setVisible(False)
            return

        title_id = query_value(sfo_command, self.sfo_path, "title_id")
        title = query_value(sfo_command, self.sfo_path, "maintitle")
        description = query_value(sfo_command, self.sfo_path, "subtitle")
        self.name_value.setText(title or empty)
        self.subtitle_value.setText(description or empty)
        self.title_id_value.setText(title_id or empty)

        size = 13
        width = self.subtitle_value.width() or 260
        while size > 7:
            needed = (
                QFontMetrics(QFont("Arial", size, QFont.Bold))
                .boundingRect(QRect(0, 0, width, 4000), Qt.TextWordWrap, description)
                .height()
            )
            if needed <= 70:
                break
            size -= 1
        self.subtitle_value.setFont(QFont("Arial", size, QFont.Bold))

        icon = os.path.join(os.path.dirname(self.sfo_path) or ".", "icon0.png")
        pixmap = QPixmap(icon) if os.path.exists(icon) else QPixmap()

        if not pixmap.isNull():
            self.image_label.setPixmap(
                pixmap.scaled(192, 192, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )
            self.image_label.setVisible(True)
            self.image_missing.setVisible(False)
        else:
            self.image_label.clear()
            self.image_label.setVisible(False)
            self.image_missing.setVisible(True)

    def retranslate(self):
        self.retranslate_title()
        self.status_label.setText("")
        if not self.sfo_path:
            self.file_label.setText(self.text("sfo_no_file", ""))
        self.refresh_info()

    def stylesheet(self):
        return """
            QWidget {
                background-color: #1e1e1e;
            }
            QLineEdit#sfoInput {
                background-color: #2d2d2d;
                border: 2px solid #3c3c3c;
                border-radius: 12px;
                padding: 12px 16px;
                color: white;
                font-size: 14px;
                min-height: 20px;
            }
            QLineEdit#sfoInput:focus {
                border: 2px solid #0078d4;
            }
            QPushButton#selectButton {
                background-color: #2d2d2d;
                border: 2px solid #3c3c3c;
                border-radius: 12px;
            }
            QPushButton#selectButton:hover {
                background-color: #3c3c3c;
                border: 2px solid #0078d4;
            }
            QPushButton#selectButton:pressed {
                background-color: #0078d4;
            }
            QPushButton#applyButton {
                background-color: #0078d4;
                border: 2px solid #0078d4;
                border-radius: 12px;
            }
            QPushButton#applyButton:hover {
                background-color: #1a86e0;
            }
            QPushButton#applyButton:pressed {
                background-color: #0060a8;
            }
            QWidget#infoContainer {
                background-color: #2d2d2d;
                border: 2px solid #3c3c3c;
                border-radius: 12px;
            }
            QLabel#gameImage {
                background-color: #1e1e1e;
                border: 2px solid #3c3c3c;
                border-radius: 3px;
            }
        """