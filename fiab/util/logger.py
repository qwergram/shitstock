import logging
import requests

from fiab.settings import DISCORD_WEBHOOK

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


class DiscordLogger(BaseLogger):

    def info(self, msg: str):
        requests.post(DISCORD_WEBHOOK, data={
            'content': msg
        })

DEFAULT_LOGGER = DiscordLogger()