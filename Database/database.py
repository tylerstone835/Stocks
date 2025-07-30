import os

import sqlite3

database_fp = os.environ.get('STOCK_DATABASE')


def create_database_table(
    database_fp: str,
    table_name: str,
    table_map: dict,
) -> None:
    """
    Parses information from table_map to construct/execute a create table statement
    in designated SQLite database.

    :param database_fp: filepath to target database.
    :param table_name: Name for created table.
    :param table_map: dict object containing column names (keys) and dtype/constraint values.
    """

    column_definitions = ',\n\t'.join([f'{column} {table_map[column]['dtype']} {table_map[column]['constraint']}'
                                       for column in table_map])

    primary_key = ', '.join([column for column in table_map if table_map[column]['primary_key']])

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
