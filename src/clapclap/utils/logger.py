import logging
import sys
import os

logger = logging.getLogger("clapclap")

os.environ["TRANSFORMERS_VERBOSITY"] = "error"
os.environ["HF_HUB_VERBOSITY"] = "error"
os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"


def setup_logger(log_level: int = 0):
    if log_level == 0:
        log_level = logging.WARNING
    elif log_level == 1:
        log_level = logging.INFO
    else:
        log_level = logging.DEBUG

    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Prevent duplicate handlers if setup is called multiple times
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    # Stream handler pointing to stderr
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(log_level)

    # Custom formatter: cleaner for CLI use (omit timestamps/module names unless debugging)
    if log_level == logging.DEBUG:
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    else:
        # Simple format for normal/info/warning modes
        formatter = logging.Formatter("%(levelname)s: %(message)s")

    handler.setFormatter(formatter)
    root_logger.addHandler(handler)
