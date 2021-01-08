import os
import sqlite3
import threading

from postal_to_geocode.retrieve_geo_data import setup_db

cwd = os.getcwd()

GEO_FILE_NAME = 'allCountries'

_local = threading.local()


def _get_connection(file_name=GEO_FILE_NAME):
    folder_path = os.path.dirname(os.path.realpath(__file__))
    db_full_path = os.path.join(folder_path, f'{file_name}.db')
    setup_db(db_full_path=db_full_path, folder_path=folder_path)
    connection = getattr(_local, 'CONNECTION', sqlite3.connect(db_full_path))
    # assign it back just incase the getattr above defaulted
    _local.CONNECTION = connection

    return connection


def lookup_postal_code(country, postal_code):
    cursor = getattr(_local, 'CURSOR', _get_connection().cursor())
    # assign it back to the _local incase the getattr above defaulted
    _local.CURSOR = cursor

    if country.lower().strip() in ['ca', 'canada']:
        postal_code = postal_code[:3]

    cursor.execute('''
        SELECT * FROM postal_to_cities WHERE country = ? AND postal_code = ?
    ''', (country, postal_code))

    first_one = cursor.fetchone()

    if first_one:
        return {
            'country': first_one[0],
            'community': first_one[2],
            'province': first_one[3],
            'short_province': first_one[4],
            'city': first_one[5],
            'latitude': first_one[9],
            'longitude': first_one[10],
        }

    return None

