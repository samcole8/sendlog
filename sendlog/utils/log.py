import logging
from pythonjsonlogger.json import JsonFormatter

def config(path: str):
    """Configure the root logger for use across the program."""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    # Set the formatter
    formatter = JsonFormatter("{asctime}{levelname}", style="{")

    if path:
        file_handler = logging.FileHandler(path)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    stdout_handler = logging.StreamHandler()
    stdout_handler.setFormatter(formatter)
    logger.addHandler(stdout_handler)

def write(logger_func, code: str, message: str, **kwargs):
    """Write a log message in a standardised format."""
    log = {
        "code ": code,
        "message": message,
        "data": {key: value for key, value in kwargs.items()}
    }
    logger_func(log)
