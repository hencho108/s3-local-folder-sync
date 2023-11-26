import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logging(config: dict):
    """
    Handles the setup and configuration of the logging system
    """
    log_directory = config["log_directory"]
    log_filepath = os.path.join(log_directory, config["log_filename"])
    log_max_size = config["log_max_size"]
    backup_count = config["backup_count"]

    # Ensure log directory exists
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

    # Configure logging with rotation
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            RotatingFileHandler(
                log_filepath, maxBytes=log_max_size, backupCount=backup_count
            ),
            logging.StreamHandler(),
        ],
    )
