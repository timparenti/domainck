#!/usr/bin/python3

import sys

import logging

from .cli import CliParser
from .log import LogHandler
from . import helpers

import whois


# Parse command line arguments.
cli = CliParser('domainck', "python -m domainck")
cli.option('-v', '--verbose', dest='verbose', action='store_true', default=False, help='run verbosely')
cli.option('-l', '--logdir', dest='log_dir', metavar='DIR', action='store', default="log", help="specify a path for logging")
cli.file_read_option('-D', '--domainfile', dest='domain_file', metavar='FILE', action='store', default=None, help="file containing list domains to check")
cli.option('-d', '--domains', dest='domains', nargs='+', metavar='FQDN', action='store', default=[], help="explicit list of domains to check")
cli.option('-r', '--retries', dest='retries', metavar='N', action='store', type=int, default=3, help="number of retry attempts when fetching WHOIS data")
args = cli.parse()

# Configure logging.
log_handler = LogHandler()
log_handler.file_output(args.log_dir)
if args.verbose:
  log_handler.stream_output()
else:
  log_handler.stream_output(log_level=logging.ERROR)
logger = log_handler.start('domainck')


if args.domain_file is not None:
  domain_list = args.domain_file.read().splitlines()
else:
  domain_list = []
domain_list.extend(args.domains)

whois_data = {}
if len(domain_list) == 0:
  logger.error("No domains specified.")
  exit(1)


domains_remaining = set(domain_list)
for r in range(args.retries):
  logger.info(f"Attempt {r+1}/{args.retries}, {len(domains_remaining)} domains to check.")
  fqdn_list = list(domains_remaining)

  # Fetch WHOIS data for each domain.
  for fqdn in fqdn_list:
    try:
      logger.info(f"Requesting WHOIS data for {fqdn} ...")
      w = whois.whois(fqdn)
    except whois.parser.PywhoisError as e:
      logger.warning(f"- No match found for {fqdn}")
      whois_data[fqdn] = None
      domains_remaining.remove(fqdn)
      continue
    except Exception as e:
      exc_type, exc_value, exc_traceback = sys.exc_info()
      logger.warning(f"- Exception {exc_type.__name__} occurred on {fqdn}, keeping for re-attempt")
      continue

    # Store this domain's WHOIS data for later processing and remove it from
    # the set.
    logger.info(f"- Expiration date for {fqdn} is {w.expiration_date}")
    whois_data[fqdn] = w
    domains_remaining.remove(fqdn)

  if len(domains_remaining) == 0:
    break

# All retries exhausted.
if len(domains_remaining) != 0:
  logger.error(f"CHECKS FAILED on {len(domains_remaining)} domains after {args.retries} attempts.")


# TODO: Store all WHOIS data to disk statefully and alert upon change from
# previous.

exit(0)
