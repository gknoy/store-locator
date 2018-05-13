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
  --address=<address>  Find nearest store to this address. If there are multiple best-matches, return the first.
  --units=(mi|km)      Display units in miles or kilometers [default: mi]
  --output=(text|json) Output in human-readable text, or in JSON (e.g. machine-readable) [default: text]

Example
  find_store --address="1770 Union St, San Francisco, CA 94123"
  find_store --zip=94115 --units=km
"""

import csv
import json
import sys
from decimal import Decimal
from math import asin, cos, pow, radians, sin, sqrt
from docopt import docopt
import googlemaps


def _quantize(d):
    """Convenience helper for rendering distance/lat/long"""
    return str(d.quantize(Decimal('0.001')))


class Store(object):
    """
    Encapsulate a Store so that we can easily pre-process radian coordinates, and have helpful rendering methods.
    """
    def __init__(self, name, lat, long, location='', address='', city='', state='', zip='', county=''):
        self.name = name
        self.location = location
        self.address = address
        self.city = city
        self.state = state
        self.zip = zip
        self.lat = Decimal(lat)
        self.long = Decimal(long)
        # pre-compute these so that we can make it faster to calculate distances
        # from all the stores. ;)
        self.lat_radians = radians(self.lat)
        self.long_radians = radians(self.long)
        self.county = county

    def get_radian_coords(self):
        return (self.lat_radians, self.long_radians)

    def to_js(self):
        return {
            'name': self.name,
            'location': self.location,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'zip': self.zip,
            'county': self.county,
            'latitude': _quantize(self.lat),
            'longitude': _quantize(self.long),
        }

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
            county=line[8],  # e.g 'Collin County',
        )

    def __repr__(self):
        return f'<Store {self.name} {self.lat} {self.long}>'

    def __str__(self):
        return (
            f'Store: {self.name}\n'
            f'    {self.location} ({self.county})\n'
            f'    {self.address}\n'
            f'    {self.city}\n'
            f'    {self.state}, {self.zip}\n'
            f'    Latitude:  {_quantize(self.lat)}\n'
            f'    Longitude: {_quantize(self.long)}\n'
        )


def get_store_locations(fname='store-locations.csv'):
    """
    Parse the store locations, names, etc from the CSV
    For now, we'll just put these in dicts.  At some point, it may be good to put them in Store objects.
    """
    stores = []
    with open(fname) as f:
        # using reader(f.readlines()) so that our mock will work with csv.reader
        reader = csv.reader(f.readlines())
        stores = [Store.from_line(line) for i, line in enumerate(reader) if i != 0]

    return stores


def get_api_keys(fname='api-keys.json'):
    """Read API keys from a gitignored configuration file"""
    with open(fname) as f:
        return json.load(f)


EARTH_RADIUS_KM = Decimal('6378.137')
EARTH_RADIUS_MI = Decimal('3963.191')


def great_circle_distance(a, b, km=True):
    """
    Return the distance (along a great circle of a sphere)

    We use the simpler haversine formula, as we aren't really concerned
    with the rounding errors that might occur for stores that are on opposite
    sides of the globe from each other.

    Reference:
    https://en.wikipedia.org/wiki/Great-circle_distance
    """

    (lat_a, lon_a) = a  # must be in radians
    (lat_b, lon_b) = b

    delta_lat = abs(lat_a - lat_b)
    delta_lon = abs(lon_a - lon_b)

    delta = 2 * asin(sqrt(
        pow(sin(delta_lat/2), 2)
        +
        (cos(lat_a) * cos(lat_b) * pow(sin(delta_lon/2), 2))
    ))

    r = EARTH_RADIUS_KM if km else EARTH_RADIUS_MI
    return r * Decimal(delta)


def find_store(start, stores, units='mi'):
    """
    Find the closest store among stores
    """
    use_km = (units != 'mi')
    stores_by_distance = [
        (store, great_circle_distance(start, store.get_radian_coords(), use_km))
        for store in stores
    ]

    # return the (first) closest one, even if a tie
    return sorted(stores_by_distance, key=lambda item: item[1])[0]


def render(store, distance, units, output='text'):
    if output == 'json':
        js = {
            'store': store.to_js(),
            'distance': _quantize(distance),
            'units': units,
        }
        print(json.dumps(js, indent=2, sort_keys=True))
    else:
        print(str(store))
        print(f'Distance: {_quantize(distance)} {units}')


def main(argv):
    """Main entry point for find_store.py"""
    arguments = docopt(__doc__)

    address = arguments['--address']  # takes precedence over zip
    zip = arguments['--zip']
    units = arguments['--units']  # 'km' or 'mi'
    output = arguments['--output']  # default text

    api_keys = get_api_keys()
    gmaps = googlemaps.Client(key=api_keys['GOOGLE_GEOCODING_API_KEY'])

    geocoded = gmaps.geocode(address or zip)
    # pre-calculate radians so we don't have to do it in great_circle_distance
    start = (
        radians(geocoded[0]['geometry']['location']['lat']),
        radians(geocoded[0]['geometry']['location']['lng']),
    )

    stores = get_store_locations()

    (store, distance) = find_store(start=start, stores=stores, units=units)
    render(store, distance, units, output)


if __name__ == '__main__':  # pragma no cover
    print(sys.argv)
    main(sys.argv)  # pragma no cover
