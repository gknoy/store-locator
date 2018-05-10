"""
# Tests for find_store
"""

import unittest
from decimal import Decimal
from find_store import (
    # find_store,
    # great_circle_distance,
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


if __name__ == '__main__':
    unittest.main()
