"""
logging_conf.py - Central logging configuration.
"""

import logging

def setup_logging(log_level, log_path):
    
    logger = logging.getLogger(__name__)
    logger.setLevel(log_level)
    logging.basicConfig(filename=log_path, format="%(asctime)s [%(levelname)s] %(message)s")

    logger.info('Logging Started')

    return logger