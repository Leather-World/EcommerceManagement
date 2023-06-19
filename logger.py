import logging

def setup_logger():
    # Create a logger instance
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # Create a file handler to write log messages to a file
    file_handler = logging.FileHandler('app.log')
    file_handler.setLevel(logging.DEBUG)

    # Create a console handler to print log messages to the console
    # console_handler = logging.StreamHandler()
    # console_handler.setLevel(logging.INFO)

    # Create a formatter to define the log message format
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s [%(filename)s:%(lineno)d - %(funcName)s]')

    # Set the formatter for the handlers
    file_handler.setFormatter(formatter)
    # console_handler.setFormatter(formatter)

    # Add the handlers to the logger
    logger.addHandler(file_handler)
    # logger.addHandler(console_handler)

    return logger
