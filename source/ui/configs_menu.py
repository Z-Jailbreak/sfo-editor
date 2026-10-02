import qtawesome as qta
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from functions.backup import backup_config_sfo
from functions.configs import (
    apply_config,
    create_config,
    delete_config,
    icon_color,
    load_configs,
    save_config,
)
from ui.base_menu import BaseMenu

OPTION_STYLE = """
    QPushButton#optionButton {
        background-color: #2d2d2d;
        border: 2px solid #3c3c3c;
        border-radius: 12px;
        color: white;
        text-align: center;
    }
    QPushButton#optionButton:hover {
        background-color: #3c3c3c;
        border: 2px solid #0078d4;
    }
    QPushButton#optionButton:pressed {
        background-color: #0078d4;
    }
"""

INPUT_STYLE = """
    QLineEdit#configInput,
    QLineEdit#configSearch {
        background-color: #2d2d2d;
        border: 2px solid #3c3c3c;
        border-radius: 12px;
        padding: 8px 14px;
        color: white;
        font-size: 14px;
        min-height: 20px;
    }
    QLineEdit#configInput:focus {
        border: 2px solid #0078d4;
    }
    QComboBox#configCombo {
        background-color: #2d2d2d;
        border: 2px solid #3c3c3c;
        border-radius: 12px;
        padding: 8px 14px;
        color: white;
        font-size: 14px;
        min-height: 20px;
    }
    QComboBox#configCombo:focus {
        border: 2px solid #0078d4;
    }
    QComboBox#configCombo QAbstractItemView {
        background-color: #2d2d2d;
        color: white;
        selection-background-color: #0078d4;
    }
"""

FORM_FIELDS = (
    ("ConfigName", "configs_name"),
    ("ConfigDescription", "configs_desc"),
    ("Author", "configs_author"),
    ("Maintitle", "configs_maintitle"),
    ("Subtitle", "configs_subtitle"),
    ("Version", "configs_version"),
    ("Notes", "configs_notes"),
)


class ConfigsMenu(BaseMenu):
    def __init__(self, parent=None):
        super().__init__(parent, title_key="configs_title", icon_name="fa5s.wrench")
        self.configs = []
        self.create_fields = {}
        self.detail_fields = {}
        self.status_label = None
        self.config_loaded = False
        self._icon_cache = {}
        self._qicon_cache = {}
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        self.add_top_bar_to_layout(main_layout)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollArea > QWidget > QWidget {
                background-color: transparent;
            }
        """)

        self.pages = QStackedWidget()
        self.pages.setStyleSheet(INPUT_STYLE)
        self.scroll.setWidget(self.pages)

        main_layout.addWidget(self.scroll, 1)
        self.setLayout(main_layout)
        self.setStyleSheet("QWidget { background-color: #1e1e1e; }")

        self.show_list()

    def showEvent(self, event):
        super().showEvent(event)
        if hasattr(self, "pages"):
            self.show_list()

    def show_list(self):
        self.configs = load_configs()
        page = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(0, 10, 0, 20)

        static_button = self.make_button(
            icon_name="fa5s.tools",
            title=self.text("configs_static", ""),
            text_key="configs_static",
        )
        static_button.clicked.connect(self.show_manage)
        layout.addWidget(static_button)

        for path, config in self.configs:
            button = self.make_button(
                icon_name=config.get("ConfigIcon") or "fa5s.file-alt",
                title=config.get("ConfigName") or "",
                description=config.get("ConfigDescription") or "",
                info=" ".join(str(v) for v in (config.get("Author", ""), config.get("Version", "")) if v),
                color=icon_color(config.get("ConfigIconColor")),
            )
            button.clicked.connect(lambda checked, cfg=config: self.select_config(cfg))
            layout.addWidget(button)

        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setFont(QFont("Arial", 12))
        if not self.configs:
            self.set_status("configs_empty", "#aaaaaa")
        elif self.config_loaded:
            self.set_status("configs_loaded", "#4caf50")
        else:
            self.status_label.hide()
        layout.addWidget(self.status_label)

        layout.addStretch()
        page.setLayout(layout)
        self._set_page(0, page)

    def show_manage(self):
        self.configs = load_configs()
        page = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(0, 10, 0, 20)

        row = QHBoxLayout()
        row.setSpacing(15)

        back_button = self.make_small_button("configs_back", "fa5s.arrow-left")
        back_button.clicked.connect(self.show_list)
        row.addWidget(back_button, 1)

        create_button = self.make_small_button("configs_create", "fa5s.plus")
        create_button.clicked.connect(self.show_create)
        row.addWidget(create_button, 1)

        layout.addLayout(row)

        for index, (path, config) in enumerate(self.configs):
            button = self.make_button(
                icon_name=config.get("ConfigIcon") or "fa5s.file-alt",
                title=config.get("ConfigName") or "",
                color=icon_color(config.get("ConfigIconColor")),
            )
            button.clicked.connect(lambda checked, i=index: self.show_detail(i))
            layout.addWidget(button)

        layout.addStretch()
        page.setLayout(layout)
        self._set_page(1, page)

    def show_create(self):
        page = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(0, 10, 0, 20)

        layout.addWidget(self.make_page_back(self.show_manage))

        self.create_fields = {}
        layout.addLayout(self.build_form(self.create_fields))

        row = QHBoxLayout()
        row.setSpacing(15)
        create_action = self.make_small_button("configs_create_btn", "fa5s.plus")
        create_action.clicked.connect(self.create_from_form)
        cancel_action = self.make_small_button("configs_cancel", "fa5s.times")
        cancel_action.clicked.connect(self.show_manage)
        row.addWidget(create_action, 1)
        row.addWidget(cancel_action, 1)
        layout.addLayout(row)
        layout.addStretch()

        page.setLayout(layout)
        self._set_page(2, page)

    def show_detail(self, index):
        self.configs = load_configs()
        if index >= len(self.configs):
            return self.show_manage()

        path, config = self.configs[index]
        page = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(0, 10, 0, 20)

        layout.addWidget(self.make_page_back(self.show_manage))

        self.detail_fields = {}
        layout.addLayout(self.build_form(self.detail_fields, config))

        row = QHBoxLayout()
        row.setSpacing(15)
        save_action = self.make_small_button("configs_save", "fa5s.save")
        save_action.clicked.connect(lambda: self.save_detail(path))
        delete_action = self.make_small_button("configs_delete", "fa5s.trash-alt")
        delete_action.clicked.connect(lambda: self.delete_detail(path))
        row.addWidget(save_action, 1)
        row.addWidget(delete_action, 1)
        layout.addLayout(row)
        layout.addStretch()

        page.setLayout(layout)
        self._set_page(3, page)

    def _set_page(self, index, page):
        while self.pages.count() <= index:
            self.pages.addWidget(QWidget())

        old = self.pages.widget(index)
        self.pages.insertWidget(index, page)
        if old is not None:
            self.pages.removeWidget(old)
            old.deleteLater()
        self.pages.setCurrentIndex(index)

    def select_config(self, config):
        path, _ = QFileDialog.getOpenFileName(
            self,
            self.text("configs_select_sfo", ""),
            "",
            "param.sfo (*.sfo);;Todos los archivos (*)",
        )
        if not path:
            return

        sfo_command = getattr(self.main_window, "sfo_command", None)
        backup_config_sfo(sfo_command, path)
        result = apply_config(config, sfo_command, path)
        if result == "ok":
            self.config_loaded = True
            self.set_status("configs_loaded", "#4caf50")
        else:
            self.set_status("configs_error", "#e53935")

    def create_from_form(self):
        for field in ("ConfigName", "Maintitle", "Subtitle"):
            if not self.create_fields[field].text().strip():
                QMessageBox.warning(self, "", self.text("configs_required", ""))
                return

        name = self.create_fields["ConfigName"].text().strip()
        if create_config(self.form_data(self.create_fields, name)):
            self.show_manage()

    def save_detail(self, path):
        name = self.detail_fields["ConfigName"].text().strip()
        if not name:
            QMessageBox.warning(self, "", self.text("configs_name_required", ""))
            return

        for path_config, config in load_configs():
            if path_config != path:
                continue
            self.form_data(self.detail_fields, name, config)
            save_config(path, config)
            break
        self.show_manage()

    def delete_detail(self, path):
        answer = QMessageBox.question(
            self,
            "",
            self.text("configs_confirm_delete", ""),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if answer == QMessageBox.Yes and delete_config(path):
            self.show_manage()

    def form_data(self, fields, name, data=None):
        data = {} if data is None else data
        data["ConfigName"] = name
        for field, caption in FORM_FIELDS:
            if field == "ConfigName":
                continue
            data[field] = fields[field].text()
        data["ConfigIcon"] = fields["ConfigIcon"].currentText()
        data["ConfigIconColor"] = icon_color(fields["ConfigIconColor"].text())
        return data

    def set_status(self, key, color):
        if self.status_label is None:
            return
        self.status_label.setText(self.text(key, ""))
        self.status_label.setStyleSheet(f"color: {color};")
        self.status_label.setProperty("text_key", key)
        self.status_label.show()

    def make_button(self, icon_name, title, description="", info="", text_key=None, color="white"):
        button = QPushButton()
        button.setObjectName("optionButton")
        button.setMinimumHeight(90)
        button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        button.setStyleSheet(OPTION_STYLE)

        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(20, 15, 20, 15)
        button_layout.setSpacing(15)

        icon_label = QLabel()
        icon_label.setPixmap(self.icon_pixmap(icon_name, 32, color))
        icon_label.setStyleSheet("background: transparent;")

        text_layout = QVBoxLayout()
        text_layout.setSpacing(5)

        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setStyleSheet("color: white; background: transparent;")
        if text_key:
            title_label.setProperty("text_key", text_key)
        text_layout.addWidget(title_label)

        if description:
            desc_label = QLabel(description)
            desc_label.setFont(QFont("Arial", 11))
            desc_label.setStyleSheet("color: #aaa; background: transparent;")
            text_layout.addWidget(desc_label)

        if info:
            info_label = QLabel(info)
            info_label.setFont(QFont("Arial", 11))
            info_label.setStyleSheet("color: #aaa; background: transparent;")
            text_layout.addWidget(info_label)

        button_layout.addWidget(icon_label)
        button_layout.addLayout(text_layout, 1)
        button_layout.addStretch()
        button.setLayout(button_layout)
        return button

    def make_small_button(self, text_key, icon_name):
        button = QPushButton()
        button.setObjectName("optionButton")
        button.setFixedHeight(44)
        button.setStyleSheet(OPTION_STYLE)

        layout = QHBoxLayout()
        layout.setContentsMargins(12, 0, 12, 0)
        layout.setSpacing(10)
        layout.addStretch(1)

        icon_label = QLabel()
        icon_label.setPixmap(self.icon_pixmap(icon_name, 22))
        icon_label.setStyleSheet("background: transparent;")

        title_label = QLabel(self.text(text_key, ""))
        title_label.setFont(QFont("Arial", 15, QFont.Bold))
        title_label.setStyleSheet("color: white; background: transparent;")
        title_label.setProperty("text_key", text_key)

        layout.addWidget(icon_label)
        layout.addWidget(title_label)
        layout.addStretch(1)
        button.setLayout(layout)
        return button

    def make_page_back(self, slot):
        button = self.make_button(
            icon_name="fa5s.arrow-left",
            title=self.text("configs_back", ""),
            text_key="configs_back",
        )
        button.clicked.connect(slot)
        return button

    def make_caption(self, text_key):
        caption = QLabel(self.text(text_key, ""))
        caption.setFont(QFont("Arial", 13, QFont.Bold))
        caption.setStyleSheet("color: white; background: transparent;")
        caption.setProperty("text_key", text_key)
        return caption

    def build_form(self, fields, values=None):
        values = values or {}
        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignLeft)
        form.setContentsMargins(0, 0, 0, 0)

        for field, caption in FORM_FIELDS:
            input_field = QLineEdit(values.get(field, ""))
            input_field.setObjectName("configInput")
            fields[field] = input_field
            form.addRow(self.make_caption(caption), input_field)

        combo, preview, color_input, search = self.make_icon_picker(
            values.get("ConfigIcon"), values.get("ConfigIconColor")
        )
        fields["ConfigIcon"] = combo
        fields["ConfigIconColor"] = color_input

        icon_row = QHBoxLayout()
        icon_row.setSpacing(10)
        icon_row.addWidget(preview)
        icon_row.addWidget(search)
        icon_row.addWidget(combo, 1)
        form.addRow(self.make_caption("configs_icon"), icon_row)
        form.addRow(self.make_caption("configs_icon_color"), color_input)

        return form

    def icon_pixmap(self, icon_name, size, color="white"):
        key = (icon_name, size, color)
        if key not in self._icon_cache:
            try:
                pixmap = qta.icon(icon_name, color=color).pixmap(QSize(size, size))
            except Exception:
                pixmap = None
            if pixmap is None or pixmap.isNull():
                try:
                    pixmap = qta.icon("fa5s.file-alt", color="white").pixmap(QSize(size, size))
                except Exception:
                    pixmap = None
            self._icon_cache[key] = pixmap
        return self._icon_cache[key]

    def icon_qicon(self, icon_name):
        if icon_name not in self._qicon_cache:
            self._qicon_cache[icon_name] = QIcon(self.icon_pixmap(icon_name, 24))
        return self._qicon_cache[icon_name]

    def make_icon_picker(self, current=None, color=None):
        current = current or "fa5s.cog"
        combo = QComboBox()
        combo.setObjectName("configCombo")
        for name in self.get_available_icons():
            combo.addItem(self.icon_qicon(name), name)

        if current not in self.get_available_icons():
            combo.insertItem(0, self.icon_qicon(current), current)
        combo.setCurrentText(current)

        search = QLineEdit()
        search.setObjectName("configSearch")
        search.setFixedWidth(170)
        search.setPlaceholderText(self.text("configs_icon_search", ""))
        search.textChanged.connect(lambda pattern: self.filter_icons(combo, pattern))

        color_input = QLineEdit(color or "#ffffff")
        color_input.setObjectName("configInput")
        color_input.setMaxLength(7)
        color_input.textChanged.connect(lambda _: refresh())

        preview = QLabel()
        preview.setFixedSize(48, 48)
        preview.setAlignment(Qt.AlignCenter)

        def refresh():
            preview.setPixmap(
                self.icon_pixmap(combo.currentText(), 40, icon_color(color_input.text()))
            )

        combo.currentTextChanged.connect(lambda _: refresh())
        refresh()
        return combo, preview, color_input, search

    def get_available_icons(self):
        from functions.configs import load_available_icons
        if not hasattr(self, "_available_icons"):
            self._available_icons = load_available_icons()
        return self._available_icons

    def filter_icons(self, combo, pattern):
        current = combo.currentText()
        combo.blockSignals(True)
        combo.clear()
        pattern = pattern.lower()
        for name in self.get_available_icons():
            if pattern in name.lower():
                combo.addItem(self.icon_qicon(name), name)
        if combo.findText(current) < 0:
            combo.insertItem(0, self.icon_qicon(current), current)
        combo.setCurrentIndex(max(combo.findText(current), 0))
        combo.blockSignals(False)

    def retranslate(self):
        self.retranslate_title()
        search = self.findChild(QLineEdit, "configSearch")
        if search is not None:
            search.setPlaceholderText(self.text("configs_icon_search", ""))
        if self.pages.currentIndex() == 0:
            self.show_list()