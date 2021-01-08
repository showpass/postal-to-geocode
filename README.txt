# Postal To GeoCode

This package retrieves postal to address data from geonames.org and transforms it into a sqlite3 db for quick retrieval.

To use, import `lookup_postal_code` and use with country and postal. For example:

```address_data = lookup_postal_code('CA', 'T2P1J9')```