import logging

class BaseLogger:

    def __init__(self):
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def debug(self, msg: str):
        logging.debug(msg)

    def info(self, msg: str):
        logging.info(msg)

    def warning(self, msg: str):
        logging.warning(msg)
    
    def error(self, msg: str):
        logging.error(msg)

    def critical(self, msg: str):
        logging.critical(msg)


DEFAULT_LOGGER = BaseLogger()