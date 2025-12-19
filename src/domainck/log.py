import sys
import subprocess
import socket

import pathlib

import logging

from . import helpers

# The LogManager class is a wrapper on logging.getLogger() and
# logging.FileHandler() in order to streamline preferred formats.

class LogManager():
  handlers: list[logging.Handler]

  def __init__(self) -> None:
    self.handlers = []

  def add_file_output(self, log_dir: str, log_file: str = helpers.run_date_filename(), log_suffix: str = 'log', log_level: int = logging.DEBUG) -> pathlib.Path:
    log_name = f'{log_file}.{log_suffix}'

    pathlib.Path(log_dir).resolve().mkdir(parents=True, exist_ok=True)
    log_path = pathlib.Path(log_dir, log_name).resolve()

    handler = logging.FileHandler(log_path)
    handler.setFormatter(logging.Formatter('%(asctime)s.%(msecs)03d %(levelname)-8s [%(name)s]\t%(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
    handler.setLevel(log_level)
    self.handlers.append(handler)

    # Symlink the latest logfile.
    log_link = pathlib.Path(log_dir, f'latest.{log_suffix}').absolute()
    subprocess.call(["ln", "-sf", log_name, log_link])

    return log_path

  def add_stream_output(self, stream=sys.stdout, log_level: int = logging.INFO) -> None:
    handler = logging.StreamHandler(stream)
    handler.setFormatter(logging.Formatter('%(message)s'))
    handler.setLevel(log_level)
    self.handlers.append(handler)

  def attach(self, logger: logging.Logger) -> None:
    for h in self.handlers:
      logger.addHandler(h)
