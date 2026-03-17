import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger("maxpost")
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

file_handler = RotatingFileHandler("logs/app.log", maxBytes=5*1024*1024, backupCount=5)
file_handler.setFormatter(formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)
