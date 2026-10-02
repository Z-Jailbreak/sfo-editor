import configparser
import os
import random
import shutil
import sys

from functions.sfo import query_value

SETTINGS_FILE = os.path.join("settings", "settings.ini")


def get_backup_option(key):
    """Reads a [Backup] key (enabled/disabled) from settings.ini; missing section = disabled"""
    config = configparser.ConfigParser()
    config.read(SETTINGS_FILE, encoding="utf-8")
    if "Backup" not in config:
        return False
    return config.get("Backup", key, fallback="").strip().lower() == "enabled"


def save_backup_option(key, enabled):
    """Saves or creates the [Backup] key (enabled/disabled) when the user changes it"""
    config = configparser.ConfigParser()
    if os.path.exists(SETTINGS_FILE):
        config.read(SETTINGS_FILE, encoding="utf-8")
    if "Backup" not in config:
        config["Backup"] = {}
    config["Backup"][key] = "enabled" if enabled else "disabled"

    os.makedirs("settings", exist_ok=True)
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        config.write(f)


def _backup_folder():
    """backup/ folder next to the binary (or the CWD in development)"""
    if getattr(sys, "frozen", False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.getcwd()
    folder = os.path.join(base, "backup")
    os.makedirs(folder, exist_ok=True)
    return folder


def _make_backup(sfo_command, sfo_path, method):
    """Copies the sfo as BACKUP-<method><titleid>-<1000..9999><counter>.sfo

    The counter is 2 digits (00, 01, ...) and counts per method and CUSA:
    SFO and CONFIG backups of the same game count separately.
    """
    if not sfo_path or not os.path.exists(sfo_path):
        return None

    title_id = query_value(sfo_command, sfo_path, "title_id")
    digits = "".join(c for c in title_id if c.isdigit())[:5]
    digits = digits.ljust(5, "0")

    folder = _backup_folder()
    prefix = f"BACKUP-{method}{digits}-"
    counter = len([f for f in os.listdir(folder) if f.startswith(prefix)])

    name = f"{prefix}{random.randint(1000, 9999)}{counter:02d}.sfo"
    destination = os.path.join(folder, name)
    try:
        shutil.copy2(sfo_path, destination)
    except OSError:
        return None
    return destination


def backup_modify_sfo(sfo_command, sfo_path):
    """Copies param.sfo if the Modify SFO backup is enabled"""
    if not get_backup_option("backup_modify_sfo"):
        return None
    return _make_backup(sfo_command, sfo_path, "SFO")


def backup_config_sfo(sfo_command, sfo_path):
    """Copies param.sfo if the Configurations backup is enabled"""
    if not get_backup_option("backup_config"):
        return None
    return _make_backup(sfo_command, sfo_path, "CONFIG")
