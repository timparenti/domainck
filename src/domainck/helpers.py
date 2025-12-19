import datetime
import socket


def iso_to_local(dts: str) -> str:
  return datetime.datetime.fromisoformat(dts).astimezone().isoformat()
def iso_to_posix(dts: str) -> int:
  return int(datetime.datetime.fromisoformat(dts).timestamp())
def now() -> datetime.datetime:
  return datetime.datetime.now(datetime.timezone.utc).astimezone()

def run_date_filename() -> str:
 return now().strftime("%Y-%m-%d-%H%M%S")

def get_local_hostname() -> str:
  host = socket.getfqdn()
  if host == "1.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.ip6.arpa":
    host = "localhost"
  return host
