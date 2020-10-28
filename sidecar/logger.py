import logging
import logging.handlers
import sys

log_format = "%(asctime)s - [%(name)s] - [%(levelname)-5s] - %(message)s"
FORMATTER = logging.Formatter(log_format)


def get_console_handler():
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(FORMATTER)
    return console_handler


def get_logger(logger_name):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(get_console_handler())
    logger.propagate = False
    return logger
