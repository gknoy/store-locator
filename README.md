# Store locator

This repo is a store locator for a fictional retail chain.  Stores are located in `store-locations.csv`.

### Installation

First, create an `api_keys.json` with your [credentials](https://console.developers.google.com/apis/dashboard):
```js
{
  "GOOGLE_GEOCODING_API_KEY": "<your key>"
}
```

```
make prepare-venv

set GOOGLE_GEOLOCATION_API_KEY=<your API key here>
python find_store.py --help
```

### Usage

```
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
```

### How this works

Store locations are stored in `store-locations.csv`.  We parse those to get records for each each store location.

Users provide an address (or a zip code).  
We use Google's geocoding API to find the latitude and longitude of the user's location
(or the center of the zip code), and then sort the store locations by their proximity to the starting point.
