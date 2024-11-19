"""
Custom cache storage handling for the biothings-client
"""

from pathlib import Path
from typing import Optional, Union
import logging
import sqlite3

import hishel


logger = logging.getLogger("biothings.client")
logger.setLevel(logging.INFO)


class BiothingsClientSqlite3Cache(hishel.SQLiteStorage):
    """
    Overriden sqlite3 client for some extra functionality

    We have two main properties that we want from this overridden
    class:

    1) The ability to get the cache location. This is accessed via
    the `cache_filepath` property
    2) The ability to clear the cache. This can be performed via the
    `clear_cache` methodcall
    """

    def __init__(
        self,
        serializer: Optional[hishel.BaseSerializer] = None,
        connection: Optional[sqlite3.Connection] = None,
        ttl: Optional[Union[int, float]] = None,
    ) -> None:
        self._cache_filepath = None
        if connection is None:
            connection, _cache_filepath = BiothingsClientSqlite3Cache.database_connection()
            self._cache_filepath = Path(_cache_filepath).absolute().resolve()
        super().__init__(serializer, connection, ttl)

    def clear_cache(self) -> None:
        """
        Clears the sqlite3 cache

        1) Performs a DELETE to remove all rows without
        dropping the table
        2) Update the auto-increment counter
        3) Perform vacuum operation
        """
        cache_table_name = "cache"
        try:
            with self._connection as connection:
                drop_table_command = f"DELETE FROM {cache_table_name}"
                connection.execute(drop_table_command)
        except sqlite3.OperationalError as operational_error:
            logger.exception(operational_error)
            exception_message = operational_error.args[0]
            missing_cache_table_message = f"no such table: {cache_table_name}"
            if exception_message == missing_cache_table_message:
                logger.debug("No table [%s] to clear. Skipping ...", cache_table_name)
            else:
                raise operational_error
        except Exception as gen_exc:
            logger.exception(gen_exc)
            raise gen_exc

        autoincrement_table_name = "SQLITE_SEQUENCE"
        try:
            reset_autoincrement_command = (
                f"UPDATE {autoincrement_table_name} SET seq = 0 WHERE name = '{cache_table_name}'"
            )
            connection.execute(reset_autoincrement_command)
        except sqlite3.OperationalError as operational_error:
            logger.exception(operational_error)
            exception_message = operational_error.args[0]
            missing_autoincrement_table_message = f"no such table: {autoincrement_table_name}"
            if exception_message == missing_autoincrement_table_message:
                logger.debug("No table [%s] to update. Skipping ...", autoincrement_table_name)
            else:
                raise operational_error
        except Exception as gen_exc:
            logger.exception(gen_exc)
            raise gen_exc

        try:
            vacuum_command = "VACUUM"
            connection.execute(vacuum_command)
        except sqlite3.OperationalError as operational_error:
            logger.exception(operational_error)
            raise operational_error
        except Exception as gen_exc:
            logger.exception(gen_exc)
            raise gen_exc

    @property
    def cache_filepath(self) -> Path:
        """
        Returns the filepath for the sqlite3 cache database

        We have either stored it because we generated it ourselves
        via `BiothingsClientSqlite3Storage.database_connection` or we
        have to look it up in the database via the following PRAGMA:
        https://www.sqlite.org/pragma.html#pragma_database_list
        """
        if self._cache_filepath is None:
            pragma_command = "PRAGMA database_list"
            for _, name, filename in self._connection.execute(pragma_command):
                if name == "main" and filename is not None:
                    self._cache_filepath = Path(filename).resolve().absolute()
                    break
        return self._cache_filepath

    @staticmethod
    def database_connection(cache_database_path: Union[str, Path] = None) -> tuple[sqlite3.Connection, Path]:
        """
        Creates the sqlite3 disk connection to the database file

        If no argument is provided for the path then the default
        path is the home directory of the user
        `~/.biothings.client.cache.sqlite3`
        """
        if cache_database_path is None:
            home_directory = Path.home()
            cache_name = ".biothings.client.cache.sqlite3"
            cache_database_path = home_directory.joinpath(cache_name)
        cache_database_path = Path(cache_database_path).resolve().absolute()

        timeout = 5
        try:
            cache_connection = sqlite3.connect(cache_database_path, timeout=timeout)
        except sqlite3.OperationalError as op_err:
            logger.exception(op_err)
            logger.error("%s table is locked. Unable to open cache database", cache_database_path)
            raise op_err
        except Exception as gen_exc:
            logger.exception(gen_exc)
            raise gen_exc
        return (cache_connection, cache_database_path)
