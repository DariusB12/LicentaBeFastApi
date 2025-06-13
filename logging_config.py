import logging
import sys

import colorlog

"""
Logging configuration
colored log for displaying on console
without color for file with logs (difficult to parse logs id using colors which are invisible characters)
"""

handler_console = colorlog.StreamHandler()
handler_console.setFormatter(colorlog.ColoredFormatter(
    '%(log_color)s%(asctime)s - %(levelname)s - [%(module)s.%(funcName)s:%(lineno)d] - %(message)s',
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'bold_red',
    }
))

handler_file = logging.FileHandler("app.log")
handler_file.setFormatter(logging.Formatter(
    '%(asctime)s - %(levelname)s - [%(module)s.%(funcName)s:%(lineno)d] - %(message)s'
))

logger = logging.getLogger("myapp")
logger.setLevel(logging.DEBUG)
logger.addHandler(handler_console)
logger.addHandler(handler_file)
