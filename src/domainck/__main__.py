#!/usr/bin/python3

import sys

import logging
import json

from .cli import CliParser
from .log import LogHandler
from .gitcache import GitCacheHandler
from . import helpers

import whois

from .whois_encode.encode import normalize, WhoisJSONEncoder


# Parse command line arguments.
cli = CliParser('domainck', "python -m domainck")
cli.option('-v', '--verbose', dest='verbose', action='store_true', default=False, help='run verbosely')
cli.option('-l', '--logdir', dest='log_dir', metavar='DIR', action='store', default="log", help="specify a path for logging")
cli.option('-c', '--cachedir', dest='cache_dir', metavar='DIR', action='store', default="cache", help="specify a path for on-disk caching")
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

if len(domain_list) == 0:
  logger.error("No domains specified.  Provide a file with -D or list individually with -d.")
  print()
  cli.help()
  exit(1)


cacher = GitCacheHandler(args.cache_dir)
cacher.clear_working_dir()

cacher.write_file("_domains.csv", '\n'.join(sorted(domain_list)))
domains_remaining = set(domain_list)
for r in range(args.retries):
  logger.info(f"Attempt {r+1}/{args.retries}, {len(domains_remaining)} domains to check.")
  fqdn_list = list(domains_remaining)

  # Fetch WHOIS data for each domain.
  for fqdn in fqdn_list:
    logger.info(f"Requesting WHOIS data for {fqdn} ...")
    w = {}
    try:
      w = whois.whois(fqdn)
      w = normalize(w)
      logger.info(f"- Expiration date for {fqdn} is {w.expiration_date}")
      domains_remaining.remove(fqdn)
    except whois.parser.WhoisDomainNotFoundError as e:
      logger.warning(f"- No match found for {fqdn}")
      domains_remaining.remove(fqdn)
      continue
    except Exception as e:
      exc_type, exc_value, exc_traceback = sys.exc_info()
      logger.warning(f"- Exception {exc_type.__name__} occurred on {fqdn}, keeping for re-attempt")
      continue
    finally:
      # Statefully store this domain's WHOIS data to disk processing.
      cacher.write_file(f"{fqdn}.json", json.dumps(w, indent=2, cls=WhoisJSONEncoder))

  if len(domains_remaining) == 0:
    break

# All retries exhausted.
if len(domains_remaining) != 0:
  logger.error(f"CHECKS FAILED on {len(domains_remaining)} domains after {args.retries} attempts:")
  for fqdn in domains_remaining:
    logger.error(f"- {fqdn}")
    cacher.write_file(f"{fqdn}.json", json.dumps({}))


# Commit current cache state to the cache repo.
logger.info("Committing current cache state to the cache repo...")
commit_success = cacher.commit()
if not commit_success:
  logger.info("... no changes.")
else:
  # Upon change from previous state, write diff to stdout for use with `cron`.
  print(cacher.show_latest_diff())

exit(0)
