import configparser
import json
import os

from PyQt5.QtWidgets import QWidget


def check_and_create_config():
    """Creates the settings/ folder and settings.ini file if missing."""
    config = configparser.ConfigParser()
    config_file = os.path.join("settings", "settings.ini")

    if not os.path.exists("settings"):
        os.makedirs("settings")

    if not os.path.exists(config_file):
        config["Language"] = {"Current": "none"}
        with open(config_file, "w", encoding="utf-8") as f:
            config.write(f)

    return config_file


def get_saved_language(config_path):
    """Returns the language stored in the configuration"""
    config = configparser.ConfigParser()
    config.read(config_path, encoding="utf-8")

    if "Language" in config:
        lang = config.get("Language", "Current", fallback=None)
        if lang and lang.strip().lower() != "none":
            return lang
    return None


def save_language(config_path, language):
    """Saves the selected language to the configuration"""
    config = configparser.ConfigParser()

    if os.path.exists(config_path):
        config.read(config_path, encoding="utf-8")

    config["Language"] = {"Current": language}

    with open(config_path, "w", encoding="utf-8") as f:
        config.write(f)


def _locale_path(lang):
    """Path of a translation file, next to this script"""
    return os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "locales",
        f"{lang}.json",
    )


def load_texts(section, lang):
    """Loads texts from a translation JSON file by section"""
    path = _locale_path(lang)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            all_texts = json.load(f)
            return all_texts.get(section, {})
    return {}


def load_all_texts(lang):
    """Loads and merges all sections of the translation file.

    Returns a single flat dict with unique keys ready for
    `update_ui_texts`.
    """
    path = _locale_path(lang)
    if not os.path.exists(path):
        return {}

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, dict):
        return {}

    merged = {}
    has_sections = False
    for value in data.values():
        if isinstance(value, dict):
            has_sections = True
            merged.update(value)

    # Compatibility with flat files (no sections)
    if not has_sections:
        return {k: v for k, v in data.items() if isinstance(v, str)}

    return merged


def update_ui_texts(widget, texts):
    """Walks all child widgets and updates the ones with text_key.

    The child tree is walked (not the layouts) to also reach the
    QScrollArea contents, which are not in the child's layout.
    """

    def update(w):
        key = w.property("text_key")
        if key and key in texts:
            w.setText(texts[key])

        for child in w.children():
            if isinstance(child, QWidget):
                update(child)

    update(widget)
