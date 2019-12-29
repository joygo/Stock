import os
from configparser import ConfigParser
import logging, logging.handlers
import datetime
"""[summary]
common functions and constant

"""

ROOT_PATH = os.getcwd().replace("\\","/")
STOCK_DATA_PATH = "{}/{}".format(ROOT_PATH, "StockData")
CONFIG_PATH = "{}/{}".format(ROOT_PATH, "config")
LOG_FILE = "{}/stock.log".format(ROOT_PATH)

class SelfConfigParser(ConfigParser):
    def __init__(self, **kwargs):
        super(SelfConfigParser, self).__init__(**kwargs)

    def get_default(self, section, option, default=''):
        if self.has_section(section):
            if self.has_option(section, option):
                return self.get(section, option)
        return default

    def get_total_default(self, section, default=''):
        if self.has_section(section):
            return self.items(section)
        return default


class Functions():

    def set_log(self, message):
        logger = logging.getLogger("stock_log")
        logger.setLevel(logging.DEBUG)
        # fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
        if not logger.handlers:
            handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=(1024 * 1024), backupCount=1, encoding='utf-8')
            logger.addHandler(handler)
            fm = logging.Formatter("%(asctime)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
            handler.setFormatter(fm)
        # logger.addHandler(fh)
        logger.info(message)
