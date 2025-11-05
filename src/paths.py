import os
import sys

## PROD

def resource_path(relative_path: str) -> str:
    """Path for read-only bundled resources (UI, icons)"""
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, relative_path)


# === Writable directories (real folders on disk) ===
DATA_DIR = "data"
LOGS_DIR = "logs"
DICTIONARY_DIR = "dictionary"

for d in (DATA_DIR, LOGS_DIR, DICTIONARY_DIR):
    os.makedirs(d, exist_ok=True)

# === Read-only resources (to bundle with PyInstaller) ===
ASSETS_DIR = "assets"
UI_DIR = "ui"

# === Writable files ===
HISTORY_FILE = os.path.join(DATA_DIR, "history.json")
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")

# === Read-only files (use resource_path) ===
VERBS_FILE = resource_path(os.path.join(DICTIONARY_DIR, "verbs.json"))
NOUNS_FILE = resource_path(os.path.join(DICTIONARY_DIR, "nouns.json"))
SENTENCES_FILE = resource_path(os.path.join(DICTIONARY_DIR, "sentences.json"))
TRAY_ICON = resource_path(os.path.join(ASSETS_DIR, "dictionary.ico"))
MAIN_WIDGET_UI = resource_path(os.path.join(UI_DIR, "main_widget.ui"))


## DEV -> Uncomment to develop, comment out section above

# Directory of the current file (src/)
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# # Project root (parent)
# PROJECT_ROOT = os.path.dirname(BASE_DIR)

# # Directories
# DATA_DIR = os.path.join(PROJECT_ROOT, "data")
# LOGS_DIR = os.path.join(PROJECT_ROOT, "logs")
# ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets")
# DICTIONARY_DIR = os.path.join(PROJECT_ROOT, "dictionary")
# UI_DIR = os.path.join(PROJECT_ROOT, "ui")

# # Ensure all directories exist
# for dir in (DATA_DIR, LOGS_DIR, ASSETS_DIR, DICTIONARY_DIR):
#     os.makedirs(dir, exist_ok=True)

# # Files
# VERBS_FILE = os.path.join(DICTIONARY_DIR, "verbs.json")
# NOUNS_FILE = os.path.join(DICTIONARY_DIR, "nouns.json")
# SENTENCES_FILE = os.path.join(DICTIONARY_DIR, "sentences.json")

# HISTORY_FILE = os.path.join(DATA_DIR, "history.json")
# SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")
# TRAY_ICON = os.path.join(ASSETS_DIR, "dictionary.ico")
# MAIN_WIDGET_UI = os.path.join(UI_DIR, "main_widget.ui")
