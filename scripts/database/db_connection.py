import logging
import logging.config
import sqlite3
from collections.abc import Sequence
from pathlib import Path
from types import TracebackType
from typing import Self

import tomllib
from scripts.database.sql_queries import (
    create_user_table_query,
    delete_existing_table_query,
    insert_user_data_query,
)

logging.config.fileConfig("config\\logging.conf")
logger = logging.getLogger()

with Path("config\\config.toml").open("rb") as f:
    cfg = tomllib.load(f)
    db_path = cfg["database"]["path"]


class SQLiteDBConnectionManager:
    connection: sqlite3.Connection | None
    cursor: sqlite3.Cursor | None

    def __init__(self) -> None:
        """Connection manager initlization method"""
        self.connection = None
        self.cursor = None

    def insert_user_data_into_table(
            self, to_db: Sequence[tuple[object, ...]]
    ) -> None:
        """Function to insert user data into table and commit the changes
        or rollback them if anything went wrong

        Args:
            to_db (Sequence[Tuple[Any]]): Sequence of tuples consisting of
            user data to be inserted into db
        """
        query = insert_user_data_query()
        if isinstance(self.cursor, sqlite3.Cursor) and isinstance(
            self.connection, sqlite3.Connection
        ):
            try:
                self.cursor.executemany(query, to_db)
            except Exception as e:
                self.connection.rollback()
                logging.info(f"Rollbacked due to {e}")
            else:
                self.connection.commit()
                logging.info("Commited")

    def create_user_data_table(self) -> None:
        """Function to create a user data table in db"""
        query = create_user_table_query()
        if isinstance(self.cursor, sqlite3.Cursor):
            self.cursor.execute(query)
            logging.info("User data table created")

    def remove_existing_table(self) -> None:
        """Function to remove existing user table from db"""
        query = delete_existing_table_query()
        if isinstance(self.cursor, sqlite3.Cursor):
            self.cursor.execute(query)
            logging.info("Existing user data table removed")

    def __enter__(self) -> Self:
        """Function that makes database connection and creates a cursor

        Returns:
            Self: Returns created object
        """
        self.connection = sqlite3.connect(db_path)
        self.cursor = self.connection.cursor()
        logging.info("Connection created")
        return self

    def __exit__(
        self,
        type_: type[BaseException] | None,
        value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Function that ensures that db connection is closed

        Args:
            type_ (type[BaseException] | None): Type of found exception
            value (BaseException | None): Value of found exception
            traceback (TracebackType | None): Traceback of found exception
        """
        if type_:
            logging.exception(f"{type_}, {value}, {traceback}")
        if isinstance(self.connection, sqlite3.Connection):
            self.connection.close()
            logging.info("Connection closed")


def recreate_db() -> None:
    """Function to recreate database by remove existing user table
    and creating a new one using SQLite Connection Manager
    """
    with SQLiteDBConnectionManager() as sqlite:
        sqlite.remove_existing_table()
    with SQLiteDBConnectionManager() as sqlite:
        sqlite.create_user_data_table()


def insert_user_data_into_table(
    user_data_to_insert: Sequence[tuple[object, ...]],
) -> None:
    """Function to insert user data into table using SQLite Connection Manager

    Args:
        user_data_to_insert (Sequence[tuple[object, ...]]): User that that is
        supposed to be written into table
    """
    with SQLiteDBConnectionManager() as sqlite:
        sqlite.insert_user_data_into_table(user_data_to_insert)
