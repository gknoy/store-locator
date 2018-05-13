"""
# Tests for find_store
"""

import json
from io import StringIO
from unittest import main as unittest_main, TestCase
from unittest.mock import patch, mock_open
from decimal import Decimal
from math import radians
from find_store import (
    find_store as _find_store,
    get_api_keys,
    great_circle_distance,
    get_store_locations,
    render,
    Store,
    # NYI: geocoding
)


class StoreTest(TestCase):
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

    def test_create_from_line(self):
        """Verify that from_line works"""
        expected = {
            'name': 'Name',
            'location': 'Human readable location',
            'address': '123 Street Address',
            'city': 'City',
            'state': 'STATE',
            'zip': '12345-1234',
            'lat': Decimal('33.1234'),
            'long': Decimal('-96.1234'),
            'county': 'County',
        }
        line = [
            'Name',
            'Human readable location',
            '123 Street Address',
            'City',
            'STATE',
            '12345-1234',
            '33.1234',
            '-96.1234',
            'County',
        ]
        store = Store.from_line(line)
        for (k, v) in expected.items():
            self.assertEqual(getattr(store, k), v)

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

    def test_get_radian_coords(self):
        coords = self.store.get_radian_coords()
        self.assertEqual(coords, (self.store.lat_radians, self.store.long_radians))

    def test_repr(self):
        self.assertEqual(repr(self.store), '<Store Name 33.1234 -96.1234>')

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


class GreatCircleDistanceTest(TestCase):

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


class FileReadingTest(TestCase):

    def test_get_api_keys(self):
        mocked_open = mock_open(read_data='{"GOOGLE_GEOCODING_API_KEY": "<your key>"}')
        with patch('find_store.open', mocked_open) as m:
            keys = get_api_keys()
            m.assert_called_once_with('api-keys.json')
            self.assertEqual(keys, {'GOOGLE_GEOCODING_API_KEY': '<your key>'})

    def test_get_store_locations(self):
        lines = [
            'Store Name,Store Location,Address,City,State,Zip Code,Latitude,Longitude,County\n',
            'Name1,Store Location1,Address1,City1,State1,Zip Code1,1.111,10.111,County1\n',
            'Name2,Store Location2,Address2,City2,State2,Zip Code2,2.222,20.222,County2\n',
        ]
        mocked_open = mock_open(read_data=''.join(lines))
        with patch('find_store.open', mocked_open) as _open:
            stores = get_store_locations()
            _open.assert_called_once_with('store-locations.csv')
            self.assertEqual(
                [repr(s) for s in stores],
                ['<Store Name1 1.111 10.111>', '<Store Name2 2.222 20.222>']
            )


class FindStoreTest(TestCase):

    def setUp(self):
        self.stores = [
            Store(name='A', lat=1.111, long=10.111),
            Store(name='B', lat=2.222, long=20.222),
            Store(name='C', lat=3.333, long=30.333),
        ]

    def test_find_km(self, m):
        store, distance = _find_store(start=(1.5, 17.0), units='km', stores=self.stores)
        self.assertEqual(store, self.stores[1])
        self.assertAlmostEqual(distance, Decimal('367.38'), places=2)

    def test_find_mi(self, m):
        store, distance = _find_store(start=(1.5, 17.0), units='mi', stores=self.stores)
        self.assertEqual(store, self.stores[1])
        self.assertAlmostEqual(distance, Decimal('228.28'), places=2)


class RenderTest(TestCase):

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

    def test_render_json(self):
        rendered = ''
        with patch('sys.stdout', new_callable=StringIO) as m:
            render(self.store, distance=Decimal(1234.5678), units='furlongs', output='json')
            rendered = m.getvalue()

        expected = json.dumps({
            'store': self.store.to_js(),
            'distance': '1234.568',
            'units': 'furlongs',
        }, indent=2, sort_keys=True)

        self.assertEqual(rendered, expected + '\n')

    def test_render_text(self):
        with patch('sys.stdout', new_callable=StringIO) as m:
            render(self.store, distance=Decimal(1234.5678), units='furlongs', output='text')
            rendered = m.getvalue()

        self.assertEqual(rendered, (
            'Store: Name\n'
            '    Human readable location (County)\n'
            '    123 Street Address\n'
            '    City\n'
            '    STATE, 12345-1234\n'
            '    Latitude:  33.123\n'
            '    Longitude: -96.123\n'
            '\n'
            'Distance: 1234.568 furlongs\n'
        ))



FAKE_GEOCODE_RESULTS = [
    {
        'geometry': {
            'location': {
                'lat': 37.6398299,
                'lng': -123.173825,
            }
        }
    }
]


class MainTest(TestCase):

    def setUp(self):
        self.stores = [
            Store(
                name='Store A',
                location='Location A',
                address='123 Street Address',
                city='City A',
                state='AA',
                zip='12345-1234',
                lat='1.111',
                long='10.111',
                county='County',
            ),
            Store(
                name='Store A',
                location='Location B',
                address='123 Street Address',
                city='City B',
                state='BB',
                zip='12345-1234',
                lat='2.222',
                long='20.222',
                county='County',
            ),
            Store(
                name='Store C',
                location='Location C',
                address='123 Street Address',
                city='City C',
                state='CC',
                zip='12345-1234',
                lat='3.333',
                long='30.333',
                county='County',
            ),
        ]

    @patch('googlemaps.geocode', return_value=FAKE_GEOCODE_RESULTS)
    def test_main(self):
        cases = [
            {
                'argv': [],
                'result': (
                    'Store: Name\n'
                    '    Location A (County)\n'
                    '    123 Street Address\n'
                    '    City A\n'
                    '    STATE, 12345-1234\n'
                    '    Latitude:  1.111\n'
                    '    Longitude: 10.111\n'
                    '\n'
                    'Distance: 1234.568 furlongs\n'
                )
            }
        ]



#
# TODO: Add tests of using the geocoding API
#


if __name__ == '__main__':
    unittest_main()
