import json
from paths import SETTINGS_FILE
from logger import logger
from utils import format_seconds

DEFAULT_QUIZ_INTERVAL = 60 * 60 # In seconds

def save_settings(enabled: bool, interval: int):
    data = {"quiz_enabled": enabled, "quiz_interval": interval}
    logger.info(f"Settings changed. Saving {data}.\nQuiz interval readable format: {format_seconds(interval)}")
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def load_settings():
    try:
        logger.info(f"Reading {SETTINGS_FILE}")
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            logger.info(f"Found saved data")
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        logger.info(f"Saved data not found, using defaults")
        return {"quiz_enabled": True, "quiz_interval": DEFAULT_QUIZ_INTERVAL}
