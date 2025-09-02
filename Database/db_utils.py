from datetime import date, datetime, timedelta
import os
import warnings

import pandas as pd
import sqlite3


DB_FILEPATH = os.environ.get('STOCK_DATABASE')

"""
Supressing the futurewarning regarding the future behavior of pd.concat.
pd.DataFrame objects with blank/null values is expected and allowed in this
use case.
"""
warnings.filterwarnings(
    "ignore",
    message=".*dataframe concatenation with empty or all-na entries is deprecated.*"
)


def create_table_from_map(
    table_name: str,
    map: dict,
) -> None:
    """
    Parses information from map to construct/execute a create table statement
    in designated SQLite database.

    :param table_name: Name for created table.
    :param map: dict object containing column names (keys) and dtype/constraint values.
    """

    column_definitions = ',\n\t'.join([f'{column} {map[column]['dtype']} {map[column]['constraint']}'
                                       for column in map]).replace(' PRIMARY KEY', '')

    primary_key = ', '.join([column for column in map if map[column]['constraint'] == 'PRIMARY KEY'])

    if not primary_key:
        raise ValueError('Primary key(s) not found in table map.')

    create_table_statement = f"""
        CREATE TABLE {table_name}
        (
        {column_definitions},
        PRIMARY KEY ({primary_key})
        );
    """

    with sqlite3.connect(DB_FILEPATH) as conn:
        cursor = conn.cursor()

        cursor.execute('BEGIN TRANSACTION;')
        cursor.execute(f'DROP TABLE IF EXISTS {table_name};')
        cursor.execute(create_table_statement)
        cursor.execute('COMMIT;')


def insert_data(
    *dfs: pd.DataFrame,
    table_name: str,
) -> None:
    """
    Insert pd.DataFrame into target SQL table.

    :param df: Data to insert.
    :param table_name: Table to insert data into.
    """

    df = pd.concat(dfs)

    binders = ', '.join(['?' for _ in df.columns])

    with sqlite3.connect(DB_FILEPATH) as conn:
        cursor = conn.cursor()

        cursor.execute('BEGIN TRANSACTION;')
        cursor.executemany(f'INSERT INTO {table_name} VALUES({binders})', df.values)
        cursor.execute('COMMIT;')


def get_missing_days(
    table_name: str
) -> list[date]:
    """
    Identifies how many days of data is missing from database table.
    Does not include Saturday/Sundays in response array.

    :param table_name: Name of target SQL table.
    :return: array of datetime.date that are missing from DB.
    """

    with sqlite3.connect(DB_FILEPATH) as conn:
        cursor = conn.cursor()
        response = cursor.execute(f'SELECT MAX(date) FROM {table_name}')

    if not response:
        return []

    last_date = datetime.strptime(response.fetchone()[0], '%Y-%m-%d').date()
    today = date.today()

    date_array = []
    for i in range((today - last_date).days):
        new_date = last_date + timedelta(days=i + 1)
        if new_date.weekday() < 5:
            date_array.append(new_date)

    return date_array
