import sys
import argparse
from typing import Any

# The CliParser class is a wrapper on argparse.ArgumentParser in order to
# streamline potentially complex argument requirements and validation.

class CliParser():
  parser: argparse.ArgumentParser

  def __init__(self, description: str, prog: str) -> None:
    self.parser = argparse.ArgumentParser(description=description, prog=prog)

  def option(self, *args: Any, **kwargs: Any) -> None:
    self.parser.add_argument(*args, **kwargs)

  def file_read_option(self, *args: Any, **kwargs: Any) -> None:
    self.parser.add_argument(*args, type=argparse.FileType('r'), **kwargs)

  def help(self) -> None:
    self.parser.print_help()

  def parse(self) -> argparse.Namespace:
    args = self.parser.parse_args()
    return args
