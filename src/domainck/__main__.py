#!/usr/bin/python3

import logging

from .cli import CliParser
from .log import LogHandler
from . import helpers


# Parse command line arguments.
cli = CliParser('domainck', "python -m domainck")
cli.option('-v', '--verbose', dest='verbose', action='store_true', default=False, help='run verbosely')
cli.option('-l', '--logdir', dest='log_dir', metavar='DIR', action='store', default="log", help="specify a path for logging")
args = cli.parse()

# Configure logging.
log_handler = LogHandler()
log_handler.file_output(args.log_dir)
if args.verbose:
  log_handler.stream_output()
else:
  log_handler.stream_output(log_level=logging.ERROR)
logger = log_handler.start('domainck')


# Hello, world!
print("domainck")
