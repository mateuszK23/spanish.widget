import os

# Directory of the current file (src/)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Project root (parent)
PROJECT_ROOT = os.path.dirname(BASE_DIR)

# Directories
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
LOGS_DIR = os.path.join(PROJECT_ROOT, "logs")
ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets") 

# Files
LOOKUP_FILE = os.path.join(DATA_DIR, "jehle_verb_lookup.json")
HISTORY_FILE = os.path.join(DATA_DIR, "history.json")
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")
TRAY_ICON = os.path.join(ASSETS_DIR, "dictionary.ico")