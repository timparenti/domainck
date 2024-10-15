import datetime


def iso_to_local(dts):
  return datetime.datetime.fromisoformat(dts).astimezone().isoformat()
def iso_to_posix(dts):
  return int(datetime.datetime.fromisoformat(dts).timestamp())
def now():
  return datetime.datetime.now(datetime.timezone.utc).astimezone()

def run_date_filename():
 return now().strftime("%Y-%m-%d-%H%M%S")
