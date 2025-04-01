import logging
import sys

from flask import current_app, has_request_context


def configure_logger(logger):
    """
    Configures a logger with a standard format and adds it to Flask's logger if in a request context.

    Args:
        logger (logging.Logger): The logger instance to configure.

    Behavior:
        - Sets the logging level to DEBUG.
        - Adds a StreamHandler with timestamp formatting.
        - Adds Flask's request-context-aware handlers if available.
    """
    logger.setLevel(logging.DEBUG)

    # Create a console handler that logs to stderr
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(logging.DEBUG)

    # Create a formatter with a timestamp
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Add the formatter to the handler
    handler.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(handler)

    # We also need to add the handler to the Flask logger
    if has_request_context():
        app_logger = current_app.logger
        for handler in app_logger.handlers:
            logger.addHandler(handler)