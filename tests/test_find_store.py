"""
# Tests for find_store
"""

import unittest
from decimal import Decimal
from math import radians
from find_store import (
    # find_store,
    great_circle_distance,
    Store,
    # NYI: testing of loading API keys, or geocoding
)


class StoreTest(unittest.TestCase):
    """
    Verify that we can construct Store records, and render them in various ways
    """

    def setUp(self):
        self.store = Store(
            name='Name',
            location='Human readable location',
            address='123 Street Address',
            city='City',
            state='STATE',
            zip='12345-1234',
            lat='33.1234',
            long='-96.1234',
            county='County',
        )

    def test_create(self):
        """Verify that we store the fields in the right places"""
        expected = {
            'name': 'Name',
            'location': 'Human readable location',
            'address': '123 Street Address',
            'city': 'City',
            'state': 'STATE',
            'zip': '12345-1234',
            'lat': Decimal('33.1234'),
            'long': Decimal('-96.1234'),
            'lat_radians': 0.5781123894550897,
            'long_radians': -1.6776698182115175,
            'county': 'County',
        }
        for (k, v) in expected.items():
            self.assertEqual(getattr(self.store, k), v)

    def test_to_js(self):
        js = self.store.to_js()
        self.assertEqual(js, {
            'name': 'Name',
            'location': 'Human readable location',
            'address': '123 Street Address',
            'city': 'City',
            'state': 'STATE',
            'zip': '12345-1234',
            'latitude': '33.123',
            'longitude': '-96.123',
            'county': 'County',
        })

    def test_str(self):
        """Verify that we pretty-print our store nicely"""
        s = str(self.store)
        expected = (
            'Store: Name\n'
            '    Human readable location (County)\n'
            '    123 Street Address\n'
            '    City\n'
            '    STATE, 12345-1234\n'
            '    Latitude:  33.123\n'
            '    Longitude: -96.123\n'
        )
        self.assertEqual(s, expected)


class GreatCircleDistanceTest(unittest.TestCase):

    def _to_radians(self, deg=0, min=0, sec=0):
        """Example locations are given in (deg, min, sec), but great_circle_distance needs radians"""
        return radians(deg + (min / 60) + (sec / 3600))

    def test_great_circle_distance(self):
        """
        Verify that we calculate great circle distance between arbitrary (latitude, longitude) locations.
        Test data generated with [https://www.greatcirclemapper.net]
        """
        _r = self._to_radians
        routes = [
            {
                'a': {
                    'name': 'LHR',
                    'lat': _r(51, 28, 14),
                    'long': _r(0, 27, 42),
                },
                'b': {
                    'name': 'JFK',
                    'lat': _r(40, 38, 23),
                    'long': _r(73, 46, 44),
                },
                'km': 5555,
                'mi': 3551.7,
            },
            {
                'a': {
                    'name': 'SFO',
                    'lat': _r(37, 37, 8),
                    'long': _r(122, 22, 30),
                },
                'b': {
                    'name': 'PDX',
                    'lat': _r(45, 35, 19),
                    'long': _r(122, 35, 52),
                },
                'km': 885,
                'mi': 549.9,
            },
            {
                'a': {
                    'name': 'STS',
                    'lat': _r(38, 30, 32),
                    'long': _r(122, 48, 46),
                },
                'b': {
                    'name': 'SFO',
                    'lat': _r(37, 37, 8),
                    'long': _r(122, 22, 30),
                },
                'km': 106,
                'mi': 65.865,
            },
        ]
        margin = 0.03
        for route in routes:
            a = (route['a']['lat'], route['a']['long'])
            b = (route['b']['lat'], route['b']['long'])
            km_delta = Decimal(margin * route['km'])
            mi_delta = Decimal(margin * route['mi'])
            self.assertAlmostEqual(Decimal(route['km']), great_circle_distance(a, b, km=True), delta=km_delta)
            self.assertAlmostEqual(Decimal(route['mi']), great_circle_distance(a, b, km=False), delta=mi_delta)


if __name__ == '__main__':
    unittest.main()
