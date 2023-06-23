import logging


def suppress_specific_logs(logger, message):
    logger = logging.getLogger(logger)

    class NoParsingFilter(logging.Filter):
        def filter(self, record):
            return not record.getMessage().startswith(message)

    logger.addFilter(NoParsingFilter())
