import os

import sqlite3


def create_db_table_from_map(
    database_fp: str,
    table_name: str,
    map: dict,
) -> None:
    """
    Parses information from map to construct/execute a create table statement
    in designated SQLite database.

    :param database_fp: filepath to target database.
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

    with sqlite3.connect(database_fp) as conn:
        cursor = conn.cursor()

        cursor.execute('BEGIN TRANSACTION;')
        cursor.execute(f'DROP TABLE IF EXISTS {table_name};')
        cursor.execute(create_table_statement)
        cursor.execute('COMMIT;')
