import logging

logging.basicConfig(level=logging.DEBUG)

# Create a custom logger
logger = logging.getLogger(__name__)

# Create handlers
debug_handler = logging.FileHandler('debug.log')
debug_handler.setLevel(logging.DEBUG)


# Create formatters and add it to handlers
debug_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
debug_handler.setFormatter(debug_format)

# Add handlers to the logger
logger.addHandler(debug_handler)


# Logger commands
logger.debug('This is a debug message')
logger.info('This is an info message')
logger.warning('This is a warning message')
logger.error('This is an error message')
logger.critical('This is a critical message')