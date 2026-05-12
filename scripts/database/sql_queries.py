from pathlib import Path

import tomllib

with Path("config\\config.toml").open("rb") as f:
    cfg = tomllib.load(f)
    table_name = cfg["database"]["user_table_name"]
    create_table_sql_path = cfg["database"]["sql"]["create_table_path"]
    delete_table_sql_path = cfg["database"]["sql"]["delete_table_path"]
    insert_user_data_sql_path = cfg["database"]["sql"]["insert_user_data_path"]


def create_user_table_query() -> str:
    """Function to get an SQL query for creating user table

    Returns:
        str: Returns SQL query for creating user table
    """
    table_creation_query = ""
    with Path(create_table_sql_path).open("r") as f:
        table_creation_query = f.read().replace("${table_name}", table_name)
    return table_creation_query


def delete_existing_table_query() -> str:
    """Function to get an SQL query for deleting existing user table

    Returns:
        str: Returns SQL query for deleting existing user table
    """
    table_delete_query = ""
    with Path(delete_table_sql_path).open("r") as f:
        table_delete_query = f.read().replace("${table_name}", table_name)
    return table_delete_query


def insert_user_data_query() -> str:
    """Function to get an SQL query for inserting user data into user table

    Returns:
        str: Returns SQL query for inserting user data into user table
    """
    insert_data_query = ""
    with Path(insert_user_data_sql_path).open("r") as f:
        insert_data_query = f.read().replace("${table_name}", table_name)
    return insert_data_query
