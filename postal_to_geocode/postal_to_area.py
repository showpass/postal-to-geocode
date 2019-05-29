import os
import sqlite3
import threading
import gzip
import unicodecsv as csv

cwd = os.getcwd()

GEO_FILE_NAME = 'allCountries'

_local = threading.local()
_local.CONNECTION = None
_local.CURSOR = None

def _get_connection(file_name=None):
    file_name = file_name or GEO_FILE_NAME
    folder_path = os.path.dirname(os.path.realpath(__file__))
    db_full_path = os.path.join(folder_path, '{}.db'.format(file_name))

    assert os.path.exists(db_full_path), 'Missing DB file for location lookup. Initialization has not been run.'

    if not _local.CONNECTION:
        _local.CONNECTION = sqlite3.connect(db_full_path)

    return _local.CONNECTION


def lookup_postal_code(country, postal_code):
    if not _local.CURSOR:
        _local.CURSOR = _get_connection().cursor()
    if country.lower().strip() in ['ca', 'canada']:
        postal_code = postal_code[:3]

    _local.CURSOR.execute('''
        SELECT * FROM postal_to_cities WHERE country = ? AND postal_code = ?
    ''', (country, postal_code))

    first_one = _local.CURSOR.fetchone()

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


def generate_db_file(folder_path, file_url, file_name=None):
    file_name = file_name or GEO_FILE_NAME
    compressed_file_name = os.path.join(folder_path, '{}.zip'.format(file_name))
    file_full_path = os.path.join(folder_path, '{}.txt'.format(file_name))
    db_full_path = os.path.join(folder_path, '{}.db'.format(file_name))

    if not os.path.exists(folder_path):
        os.mkdir(folder_path)
    os.system('cd {}; rm -rf *; wget {}'.format(folder_path, file_url))
    os.system('unzip -q -n -d {} {}'.format(folder_path, compressed_file_name))

    conn = sqlite3.connect(db_full_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE postal_to_cities (
            country                                    VARCHAR (4),
            postal_code                                VARCHAR (16),
            place_name                                 TEXT,
            order_sub_div_1_name_state                 TEXT,
            order_sub_div_1_code_state                 TEXT,
            order_sub_div_2_name_county_province       TEXT,
            order_sub_div_2_code_county_province       TEXT,
            order_sub_div_3_name_community             TEXT,
            order_sub_div_3_code_community             TEXT,
            Latitude                                   NUMERIC,
            Longitude                                  NUMERIC,
            Accuracy                                   INTEGER,
            UNIQUE (
                country,
                postal_code
            )
            ON CONFLICT REPLACE
        );
        
    ''')

    cursor.execute('''
        CREATE INDEX someIndex ON postal_to_cities (postal_code, country);
    ''')

    print('Analyzing location data file')

    with open(file_full_path, 'r') as address_file:
        dialect = csv.Sniffer().sniff(address_file.read(1024))
        address_file.seek(0)
        _address_csv = csv.reader(address_file, dialect, encoding='utf-8')
        to_db = [tuple(col_v) for col_v in _address_csv]

    print('Importing database into a sqlite3 db file')

    cursor.executemany('''
        INSERT INTO postal_to_cities (country, postal_code, place_name, order_sub_div_1_name_state,
            order_sub_div_1_code_state, order_sub_div_2_name_county_province, order_sub_div_2_code_county_province,
            order_sub_div_3_name_community, order_sub_div_3_code_community, Latitude, Longitude, Accuracy) VALUES
            (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    ''', to_db)

    conn.commit()
    conn.close()

    print('done.')


def compress_db(file_name=None):
    file_name = file_name or GEO_FILE_NAME
    folder_path = os.path.dirname(os.path.realpath(__file__))
    db_full_path = os.path.join(folder_path, '{}.db'.format(file_name))
    gz_full_path = os.path.join(folder_path, '{}.gz'.format(file_name))
    with open(db_full_path, 'rb') as db_file:
        with gzip.open(gz_full_path, 'wb') as gzip_file:
            gzip_file.write(db_file.read())


def uncompress_db(file_name=None):
    file_name = file_name or GEO_FILE_NAME
    folder_path = os.path.dirname(os.path.realpath(__file__))
    db_full_path = os.path.join(folder_path, '{}.db'.format(file_name))
    gz_full_path = os.path.join(folder_path, '{}.gz'.format(file_name))
    with gzip.open(gz_full_path, 'rb') as gzip_file:
        with open(db_full_path, 'wb') as db_file:
            db_file.write(gzip_file.read())