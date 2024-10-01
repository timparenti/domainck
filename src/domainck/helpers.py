import datetime
from json import JSONEncoder


def iso_to_local(dts):
  return datetime.datetime.fromisoformat(dts).astimezone().isoformat()
def iso_to_posix(dts):
  return int(datetime.datetime.fromisoformat(dts).timestamp())
def now():
  return datetime.datetime.now(datetime.timezone.utc).astimezone()

def run_date_filename():
 return now().strftime("%Y-%m-%d-%H%M%S")

# From https://stackoverflow.com/a/3768975/782129, 2019-04-25
class WhoisJSONEncoder(JSONEncoder):
  def default(self, obj):
    if isinstance(obj, datetime.datetime):
      return str(obj)
    return JSONEncoder.default(self, obj)
