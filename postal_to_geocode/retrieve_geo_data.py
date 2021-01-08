import csv
import os
import sqlite3

from urllib.request import urlopen
from zipfile import ZipFile
from io import BytesIO, TextIOWrapper

GEO_FILE_NAME = 'allCountries'
GEO_FILE_URL = 'http://download.geonames.org/export/zip/allCountries.zip'


def setup_db(file_name=GEO_FILE_NAME, folder_path=None, db_full_path=None):
    folder_path = folder_path or os.path.dirname(os.path.realpath(__file__))
    db_full_path = db_full_path or os.path.join(folder_path, f'{file_name}.db')

    if not os.path.exists(db_full_path):
        db_zip_path = os.path.join(folder_path, f'{file_name}.zip')
        if os.path.exists(db_zip_path):
            uncompress_db()
        else:
            retrieve_geo_from_url()


def retrieve_geo_from_url(url=GEO_FILE_URL,file_name=GEO_FILE_NAME):
    print(f'Retrieving data file from {url}')
    geo_file = urlopen(url).read()
    geo_zip_data = ZipFile(BytesIO(geo_file))
    address_file = TextIOWrapper(geo_zip_data.open(f'{file_name}.txt'), encoding='UTF-8')
    import_csv_to_db(address_file)


def uncompress_db(file_name=GEO_FILE_NAME):
    print(f'Unarchiving and processing included data file {GEO_FILE_NAME}.zip')
    folder_path = os.path.dirname(os.path.realpath(__file__))
    zip_full_path = os.path.join(folder_path, f'{file_name}.zip')
    with ZipFile(zip_full_path, 'r') as geo_zip_data:
        address_file = TextIOWrapper(geo_zip_data.open(f'{file_name}.txt'), encoding='UTF-8')
        import_csv_to_db(address_file)


def import_csv_to_db(csv_file):
    folder_path = os.path.dirname(os.path.realpath(__file__))
    dialect = get_csv_dialect(csv_file)
    _address_csv = csv.reader(csv_file, dialect)
    conn = get_db_cursor(folder_path, file_name=GEO_FILE_NAME)
    prepare_db(conn)
    insert_into_db(conn, [tuple(col_v) for col_v in _address_csv])
    close_db(conn)


def get_csv_dialect(csv_file):
    dialect = csv.Sniffer().sniff(csv_file.read(1024))
    csv_file.seek(0)
    return dialect


def get_db_cursor(folder_path, file_name=GEO_FILE_NAME):
    db_full_path = os.path.join(folder_path, f'{file_name}.db')
    return sqlite3.connect(db_full_path)


def prepare_db(conn):
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


def insert_into_db(conn, records):
    cursor = conn.cursor()
    cursor.executemany('''
        INSERT INTO postal_to_cities (country, postal_code, place_name, order_sub_div_1_name_state,
            order_sub_div_1_code_state, order_sub_div_2_name_county_province, order_sub_div_2_code_county_province,
            order_sub_div_3_name_community, order_sub_div_3_code_community, Latitude, Longitude, Accuracy) VALUES
            (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    ''', records)


def close_db(conn):
    conn.commit()
    conn.close()