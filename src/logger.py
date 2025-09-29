import logging
import os
import sys
from paths import LOGS_DIR

# Path to log file
LOG_FILE = os.path.join(LOGS_DIR, "app.log")

# Configure root logger
logging.basicConfig(
    level=logging.INFO,  # switch to DEBUG for more detail
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("spanish_widget")


# ---- Redirect stderr to logger ----
class StreamToLogger:
    """Redirect writes to a logger instance instead of stderr/stdout."""
    def __init__(self, logger, level):
        self.logger = logger
        self.level = level

    def write(self, message):
        message = message.strip()
        if message:
            self.logger.log(self.level, message)

    def flush(self):
        pass


sys.stderr = StreamToLogger(logger, logging.ERROR)


# ---- Catch uncaught exceptions ----
def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        # Let Ctrl+C behave normally
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))


sys.excepthook = handle_exception
