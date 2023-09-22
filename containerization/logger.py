import logging

from pathlib import Path

from data import Paths


class Logger:
    def __init__(self, name: str):
        self.logger_name: str = name

        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False

        self.formatter = logging.Formatter('%(asctime)s: %(name)s: %(levelname)s: %(message)s')  # type: ignore

        self.log_file: Path = Paths.logs_dir / f'{self.logger_name}.log'
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

        self.file_handler = logging.FileHandler(self.log_file, mode='w')  # type: ignore
        self.file_handler.setLevel(logging.DEBUG)
        self.file_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.file_handler)

        self.stream_handler = logging.StreamHandler()  # type: ignore
        self.stream_handler.setLevel(logging.INFO)
        self.stream_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.stream_handler)

    def log_and_raise(self, error_message: str):
        self.logger.error(error_message)
        raise RuntimeError(error_message)

    def warn_and_continue(self, warning_message: str):
        self.logger.warning(warning_message)
