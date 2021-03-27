import logging


def setup_logging(level):
    logger = logging.getLogger('stactools')
    logger.setLevel(level)

    ch = logging.StreamHandler()
    ch.setLevel(level)
    formatter = logging.Formatter('%(message)s')
    ch.setFormatter(formatter)

    logger.addHandler(ch)


setup_logging(logging.INFO)
