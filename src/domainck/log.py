import sys
import subprocess
import socket

import importlib.metadata
import pathlib

import logging

from . import helpers

# The LogHandler class is a wrapper on logging.getLogger() and
# logging.FileHandler() in order to streamline preferred formats.

class LogHandler():
  logger = logging.getLogger()
  log_path = None

  def __init__(self, log_level=logging.DEBUG):
    self.logger = logging.getLogger()
    self.logger.setLevel(log_level)

  def file_output(self, log_dir, log_file=helpers.run_date_filename(), log_suffix='log', log_level=logging.DEBUG):
    log_name = f'{log_file}.{log_suffix}'

    pathlib.Path(log_dir).resolve().mkdir(parents=True, exist_ok=True)
    self.log_path = pathlib.Path(log_dir, log_name).resolve()

    handler = logging.FileHandler(self.log_path)
    handler.setFormatter(logging.Formatter('%(asctime)s.%(msecs)03d:%(levelname)s\t%(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
    handler.setLevel(log_level)
    self.logger.addHandler(handler)

    # Symlink the latest logfile.
    log_link = pathlib.Path(log_dir, f'latest.{log_suffix}').absolute()
    subprocess.call(["ln", "-sf", log_name, log_link])

  def stream_output(self, stream=sys.stdout, log_level=logging.INFO):
    handler = logging.StreamHandler(stream)
    handler.setFormatter(logging.Formatter('%(message)s'))
    handler.setLevel(log_level)
    self.logger.addHandler(handler)

  def start(self, pkg):
    self.logger.info(f"Package name: {pkg}")
    self.logger.info(f"Package version: {importlib.metadata.version(pkg)}")
    self.logger.info(f"Logging began: {helpers.now()}")
    self.logger.info(f"Local host: {socket.getfqdn()}")
    self.logger.info(f"Log location: {self.log_path}")
    self.logger.info("--------------------")

    return self.logger
