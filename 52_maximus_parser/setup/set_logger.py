import logging
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
import os


def setup_logging():
    # Set up the folder structure based on year, month, and day
    log_folder = os.path.join('logs', datetime.now().strftime('%Y/%m/%d'))
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)

    log_file_path = os.path.join(log_folder, 'app.log')

    # Configure the custom formatter
    log_format = '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    formatter = logging.Formatter(log_format, datefmt='%Y-%m-%d %H:%M:%S')

    # Create a rotating file handler with time-based rotation
    handler = TimedRotatingFileHandler(log_file_path, when="midnight", interval=1, backupCount=0, encoding='utf-8')

    # Set the formatter for the handler
    handler.setFormatter(formatter)

    # Set the logging level for the handler
    handler.setLevel(logging.INFO)

    # Get the root logger and add the handler
    logger = logging.getLogger()
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    return logger
