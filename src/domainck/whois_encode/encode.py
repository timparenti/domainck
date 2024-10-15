import datetime
from json import JSONEncoder


# From https://stackoverflow.com/a/3768975/782129, 2019-04-25
class WhoisJSONEncoder(JSONEncoder):
  def default(self, obj):
    if isinstance(obj, datetime.datetime):
      return str(obj)
    return JSONEncoder.default(self, obj)


def normalize(w):
  for key in list(w.keys()):
    match key:

      case 'updated_date' | 'creation_date' | 'expiration_date':
        # Only include the first datetime when more than one is returned.
        if isinstance(w[key], list):
          w[key] = w[key][0]

      case 'domain_name':
        # Normalize domain name to lower case.
        if isinstance(w[key], list):
          w[key] = w[key][0].lower()
        else:
          w[key] = w[key].lower()

      case 'name_servers':
        # Uniquify name servers case-insensitively.
        if isinstance(w[key], list):
          seen = set()
          result = []
          for item in w[key]:
            lower_item = item.lower()
            if lower_item not in seen:
              seen.add(lower_item)
              result.append(lower_item)
          w[key] = result

      case 'registrar':
        # Normalize variant versions of known registrar names.
        match w[key]:
          case "ENOM, INC.":
            w[key] = "Enom, Inc."
          case "NAMECHEAP INC":
            w[key] = "NameCheap, Inc."
          case _:
            pass

      case ( 'referral_url' | 'emails' | 'name' | 'org' | 'address'
             | 'city' | 'state' | 'registrant_postal_code' | 'country' ):
        # Remove certain unneeded keys.
        w.pop(key, None)

      case _:
        pass

  return w
