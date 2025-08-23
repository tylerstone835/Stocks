import os
import warnings

import pandas as pd
import sqlite3


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
    db_filepath: str,
    table_name: str,
    map: dict,
) -> None:
    """
    Parses information from map to construct/execute a create table statement
    in designated SQLite database.

    :param db_filepath: filepath to target database.
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

    with sqlite3.connect(db_filepath) as conn:
        cursor = conn.cursor()

        cursor.execute('BEGIN TRANSACTION;')
        cursor.execute(f'DROP TABLE IF EXISTS {table_name};')
        cursor.execute(create_table_statement)
        cursor.execute('COMMIT;')


def insert_data(
    *dfs: pd.DataFrame,
    table_name: str,
    db_filepath: str
) -> None:
    """
    Insert pd.DataFrame into target SQL table.

    :param df: Data to insert.
    :param table_name: Table to insert data into.
    :param db_filepath: Filepath of target database.
    """

    df = pd.concat(dfs)

    binders = ', '.join(['?' for _ in df.columns])

    with sqlite3.connect(db_filepath) as conn:
        cursor = conn.cursor()

        cursor.execute('BEGIN TRANSACTION;')
        cursor.executemany(f'INSERT INTO {table_name} VALUES({binders})', df.values)
        cursor.execute('COMMIT;')
