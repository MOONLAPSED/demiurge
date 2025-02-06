import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler

# Create a logger with the name of the module
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create a formatter for log messages
formatter = logging.Formatter('[%(levelname)s]%(asctime)s||%(name)s: %(message)s', datefmt='%Y-%m-%d~%H:%M:%S%z')

# Create a console handler and add it to the logger
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Create a file handler and add it to the logger
logs_dir = Path(__file__).resolve().parent / 'logs'
logs_dir.mkdir(exist_ok=True)
file_handler = RotatingFileHandler(logs_dir / 'app.log', maxBytes=10485760, backupCount=10)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Log a message indicating that logging has been initialized
logger.info('Logging initialized from %s', __file__)
