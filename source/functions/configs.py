import glob
import json
import os
import random

import qtawesome as qta
from functions.sfo import apply_changes

CONFIG_DIR = "config"


def load_available_icons():
    """All Font Awesome 5 icons shipped with qtawesome.

    Reads the charmaps inside qtawesome/fonts: solid (fa5s),
    regular (fa5) and brands (fa5b).
    """
    fonts_dir = os.path.join(os.path.dirname(qta.__file__), "fonts")
    charmaps = (
        ("fa5s", "fontawesome5-solid-webfont-charmap-*.json"),
        ("fa5", "fontawesome5-regular-webfont-charmap-*.json"),
        ("fa5b", "fontawesome5-brands-webfont-charmap-*.json"),
    )

    icons = []
    for prefix, pattern in charmaps:
        matches = glob.glob(os.path.join(fonts_dir, pattern))
        if matches:
            with open(matches[0], encoding="utf-8") as f:
                icons.extend(f"{prefix}.{name}" for name in sorted(json.load(f)))
    return icons


AVAILABLE_ICONS = load_available_icons()


def icon_color(value):
    """Normalizes a #RRGGBB color; returns white if invalid"""
    value = (value or "").strip().lstrip("#")
    if len(value) == 6 and all(c in "0123456789abcdefABCDEF" for c in value):
        return f"#{value.lower()}"
    return "#ffffff"


def load_configs():
    """Reads the JSON files from config/ (relative to the CWD, like the CLI).

    Returns a list of (path, data) in alphabetical order, skipping
    files that cannot be read as JSON.
    """
    if not os.path.isdir(CONFIG_DIR):
        return []

    configs = []
    for name in sorted(os.listdir(CONFIG_DIR)):
        if not name.endswith(".json"):
            continue
        path = os.path.join(CONFIG_DIR, name)
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, ValueError):
            continue
        if isinstance(data, dict):
            configs.append((path, data))
    return configs


def save_config(path, data):
    """Writes a configuration's data to its JSON"""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def create_config(data):
    """Creates config-<random 1000..99999>.json and returns its path"""
    if not os.path.isdir(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)

    for _ in range(100):
        path = os.path.join(CONFIG_DIR, f"config-{random.randint(1000, 99999)}.json")
        if not os.path.exists(path):
            save_config(path, data)
            return path
    return None


def delete_config(path):
    """Deletes a configuration's JSON"""
    try:
        os.remove(path)
    except OSError:
        return False
    return True


def apply_config(config, sfo_command, sfo_path):
    """Writes the config's Maintitle and Subtitle into param.sfo"""
    return apply_changes(
        sfo_command,
        sfo_path,
        config.get("Maintitle", ""),
        config.get("Subtitle", ""),
    )
