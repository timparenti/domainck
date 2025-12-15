import datetime
from json import JSONEncoder

from .. import helpers


# From https://stackoverflow.com/a/3768975/782129, 2019-04-25
class WhoisJSONEncoder(JSONEncoder):
  def default(self, obj):
    if isinstance(obj, datetime.datetime):
      return str(obj)
    return JSONEncoder.default(self, obj)


def normalize(w):
  for key in list(w.keys()):
    match key:

      case ( 'updated_date' | 'creation_date' | 'expiration_date' ):
        # Only include the first datetime when more than one is returned.
        if isinstance(w[key], list):
          w[key] = w[key][0]
        # These timestamps are returned naïvely as UTC; make the objects
        # timezone-aware.
        w[key] = w[key].replace(tzinfo=datetime.timezone.utc)

	# For expiration dates only, add a field summarizing expiration status:
        if key == 'expiration_date':
          thresholds = [
            datetime.timedelta(days=0),
            datetime.timedelta(days=7),
            datetime.timedelta(days=21),
            datetime.timedelta(days=45)
          ]
          time_to_exp = w[key] - helpers.now()
          for threshold in thresholds:
            if time_to_exp < threshold:
              exp_status = f"Less than {threshold}"
              break
          else:
            exp_status = "OK"
          w['expiration_status'] = exp_status

      case ( 'domain_name' | 'whois_server' ):
        # Normalize domain name and whois server to lower case.
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
          w[key] = sorted(result)

      case 'registrar':
        # Normalize variant versions of known registrar names.
        match w[key]:
          case "DREAMHOST":
            w[key] = "DreamHost, LLC"
          case ( "ENOM, INC." | "Enom, Inc." ):
            w[key] = "eNom, LLC"
          case "NAMECHEAP INC":
            w[key] = "NameCheap, Inc."
          case _:
            pass

      case 'status':
        # Sort statuses when more than one is returned.
        if isinstance(w[key], list):
          w[key] = sorted(w[key])

      case ( 'referral_url' | 'domain__id' | 'emails' | 'name' | 'org'
             | 'address' | 'city' | 'state' | 'country'
             | 'registrar_id' | 'registrar_url'
             | 'registrant_name' | 'registrant_state_province'
             | 'registrant_postal_code' | 'registrant_country'
             | 'tech_name' | 'tech_org' | 'admin_name' | 'admin_org'
             | 'reseller' ):
        # Remove certain unneeded or obscure keys.
        w.pop(key, None)

      case _:
        pass

  return w
