import logging


class Logger:
    def __init__(name: str):
        self.logger_name: str = name

        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False
        self.formatter = logging.Formatter('%(asctime)s: %(name)s: %(levelname)s: %(message)s')  # type: ignore
        self.stream_handler = logging.StreamHandler()  # type: ignore
        self.stream_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.stream_handler)