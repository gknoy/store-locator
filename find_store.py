"""
Find Store
  find_store will locate the nearest store (as the vrow flies) from
  store-locations.csv, print the matching store address, as well as
  the distance to that store.

Usage:
  find_store --address="<address>"
  find_store --address="<address>" [--units=(mi|km)] [--output=text|json]
  find_store --zip=<zip>
  find_store --zip=<zip> [--units=(mi|km)] [--output=text|json]

Options:
  --zip=<zip>          Find nearest store to this zip code. If there are multiple best-matches, return the first.
  --address            Find nearest store to this address. If there are multiple best-matches, return the first.
  --units=(mi|km)      Display units in miles or kilometers [default: mi]
  --output=(text|json) Output in human-readable text, or in JSON (e.g. machine-readable) [default: text]

Example
  find_store --address="1770 Union St, San Francisco, CA 94123"
  find_store --zip=94115 --units=km
"""

import csv
import json
from decimal import Decimal
from docopt import docopt


#
# Stores
#
class Store(object):
    def __init__(self, name, location, address, city, state, zip, lat, long, county):
        self.name=name
        self.location=location
        self.address=address
        self.city=city
        self.state=state
        self.zip=zip
        self.lat=lat
        self.long=long
        self.county=county

    def distance_from(self, lat, long):
        return great_circle_distance((self.lat, self.long), (lat, long))

    @classmethod
    def from_line(cls, line):
        return cls(
            name=line[0],  # e.g 'Plano West',
            location=line[1],  # e.g 'NEC Dallas N Tollway & W Park Blvd',
            address=line[2],  # e.g '2200 Dallas Pkwy',
            city=line[3],  # e.g 'Plano',
            state=line[4],  # e.g 'TX',
            zip=line[5],  # e.g '75093-4300',
            lat=line[6],  # e.g '33.0304051',
            long=line[7],  # e.g '-96.8270449',
            county=line[8],  # e.g 'Collin County'],
        )

def get_store_locations(fname='store-locations.csv'):
    """
    Parse the store locations, names, etc from the CSV
    For now, we'll just put these in dicts.  At some point, it may be good to put them in Store objects.
    """
    stores = []
    with open(fname) as f:
        reader = csv.reader(f)
        stores = [Store.from_line(line) for i, line in enumerate(reader) if i != 0]
    return stores


#
# Location finding
#

def get_api_keys(fname='api-keys.json'):
    """Read API keys from a gitignored configuration file"""
    with open(fname) as f:
        return json.loads(f)


def geocode(address=None, zip=None):
    """
    Placeholder for Google geocoding API
    Get a (lat, long) for an arbitrary location
    """
    # TODO use the google API
    return (0, 0)


EARTH_RADIUS_KM = Decimal('6378.137')

def great_circle_distance(a, b):
    """
    Return the distance (along a great circle of a sphere)

    References:
    https://en.wikipedia.org/wiki/Great-circle_distance
    https://en.wikipedia.org/wiki/Haversine_formula
    """
    # TODO ;)
    return Decimal('42')


def find_store(address=None, zip=None, units='mi', output='text'):
    """
    Find the closest store among stores
    """
    start = geocode(address, zip)

    # for each store, calculate great circle distance from location
    # return the (first) closest one.
    pass


API_KEYS = get_api_keys()
STORE_LOCATIONS = get_store_locations()


# entry point
if __name__ == '__main__':
    arguments = docopt(__doc__, version='Store Locator 0.1')
