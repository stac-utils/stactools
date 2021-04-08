import logging


class Logging:
    _logging_setup: bool = False

    @classmethod
    def setup_logging(cls, level):
        if cls._logging_setup:
            return

        logger = logging.getLogger()
        logger.setLevel(level)

        ch = logging.StreamHandler()
        ch.setLevel(level)
        formatter = logging.Formatter('%(message)s')
        ch.setFormatter(formatter)

        logger.addHandler(ch)

        cls._logging_setup = True


Logging.setup_logging(logging.INFO)
