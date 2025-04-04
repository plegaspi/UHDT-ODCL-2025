import logging
import colorlog
import os

# --- Config ---
log_format = "%(asctime)s - %(log_color)s%(levelname)s%(reset)s - %(message)s"

COLOR_RESET = "\033[0m"
COLOR_BLUE = "\033[34m"
COLOR_CYAN = "\033[36m"
COLOR_MAGENTA = "\033[35m"
COLOR_WHITE = "\033[37m"

LOGGER_COLORS = {
    "annotated": COLOR_BLUE,
    "object-detection": COLOR_CYAN,
    "georeferencing": COLOR_MAGENTA,
    "optimized-payload-matching": COLOR_WHITE,
}

LOG_LEVEL_COLORS = {
    "DEBUG": "cyan",
    "INFO": "green",
    "WARNING": "yellow",
    "ERROR": "red",
    "CRITICAL": "bold_red",
}

# --- Formatter ---
class CustomColoredFormatter(colorlog.ColoredFormatter):
    def format(self, record):
        log_color = LOGGER_COLORS.get(record.name, COLOR_RESET)
        timestamp = f"{log_color}{self.formatTime(record)}{COLOR_RESET}"
        record.asctime = timestamp
        return super().format(record)

# --- Logger Class ---
class Custom_Logger:
    def __init__(self, logger_name, log_path, enabled=True):
        self.enabled = enabled
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(logging.DEBUG)
        self.logger.propagate = True

        if not self.logger.handlers:
            formatter = CustomColoredFormatter(
                log_format,
                log_colors=LOG_LEVEL_COLORS,
                reset=True,
                style="%",
            )

            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)

            file_handler = logging.FileHandler(log_path)
            file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

            self.logger.addHandler(console_handler)
            self.logger.addHandler(file_handler)

    def debug(self, msg):
        if self.enabled:
            self.logger.debug(msg)

    def info(self, msg):
        if self.enabled:
            self.logger.info(msg)

    def warning(self, msg):
        if self.enabled:
            self.logger.warning(msg)

    def error(self, msg):
        if self.enabled:
            self.logger.error(msg)

    def critical(self, msg):
        if self.enabled:
            self.logger.critical(msg)

    def get_logger(self):
        return self.logger

    @staticmethod
    def setup_root_logger(runtime_log_path):
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        
        logging.getLogger("matplotlib").setLevel(logging.WARNING)
        logging.getLogger("PIL").setLevel(logging.WARNING)  

        if not any(isinstance(h, logging.FileHandler) and getattr(h, "baseFilename", None) == os.path.abspath(runtime_log_path)
                   for h in root_logger.handlers):
            runtime_handler = logging.FileHandler(runtime_log_path)
            runtime_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
            root_logger.addHandler(runtime_handler)

        if not any(isinstance(h, logging.StreamHandler) for h in root_logger.handlers):
            root_logger.addHandler(logging.StreamHandler())

    @staticmethod
    def get_root_logger():
        return logging.getLogger()