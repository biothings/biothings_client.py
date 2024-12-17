"""
Custom cache storage handling for the biothings-client
"""

from pathlib import Path
from typing import Optional, Union
import logging
import sqlite3

from biothings_client._dependencies import _CACHING

if _CACHING:
    import anysqlite
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
        connection: Optional[anysqlite.Connection] = None,
        ttl: Optional[Union[int, float]] = None,
    ) -> None:
        self._cache_filepath: Path = None
        self._connection: Optional[sqlite3.Connection] = connection or None
        self._setup_completed: bool = False
        super().__init__(serializer, connection, ttl)

    def setup_database_connection(self, cache_filepath: Union[str, Path] = None) -> None:
        """
        Establishes the sqlite3 database connection if it hasn't been
        created yet

        Override of the _setup method so that we can specify the database
        file path. Exposed publically so that the user can specify this as well
        along with during biothings_client testing
        """
        if not self._setup_completed:
            if cache_filepath is None:
                home_directory = Path.home()
                cache_directory = home_directory.joinpath(".cache")
                cache_directory.mkdir(parents=True, exist_ok=True)
                cache_filepath.joinpath(".hishel.sqlite")
            self._cache_filepath = cache_filepath.resolve().absolute()

            with self._setup_lock:
                if not self._connection:  # pragma: no cover
                    self._connection = sqlite3.connect(self._cache_filepath, check_same_thread=False)
                table_creation_commnd = "CREATE TABLE IF NOT EXISTS cache(key TEXT, data BLOB, date_created REAL)"
                self._connection.execute(table_creation_commnd)
                self._connection.commit()
                self._setup_completed = True

    def clear_cache(self) -> None:
        """
        Clears the sqlite3 cache

        1) Performs a DELETE to remove all rows without
        dropping the table
        2) Update the auto-increment counter
        3) Perform vacuum operation
        """
        cache_table_name = "cache"
        with self._setup_lock:
            try:
                drop_table_command = f"DELETE FROM {cache_table_name}"
                self._connection.execute(drop_table_command)
                self._connection.commit()
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
                self._connection.execute(reset_autoincrement_command)
                self._connection.commit()
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
                self._connection.execute(vacuum_command)
                self._connection.commit()
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
        self.setup_database_connection()
        if self._cache_filepath is None:
            pragma_command = "PRAGMA database_list"
            for _, name, filename in self._connection.execute(pragma_command):
                if name == "main" and filename is not None:
                    self._cache_filepath = Path(filename).resolve().absolute()
                    break
        return self._cache_filepath


class AsyncBiothingsClientSqlite3Cache(hishel.AsyncSQLiteStorage):
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
        connection: Optional[anysqlite.Connection] = None,
        ttl: Optional[Union[int, float]] = None,
    ) -> None:
        self._cache_filepath = None
        super().__init__(serializer, connection, ttl)

    async def setup_database_connection(self, cache_filepath: Union[str, Path] = None) -> None:
        """
        Establishes the sqlite3 database connection if it hasn't been
        created yet

        Override of the _setup method so that we can specify the database
        file path. Exposed publically so that the user can specify this as well
        along with during biothings_client testing
        """
        if not self._setup_completed:
            if cache_filepath is None:
                home_directory = Path.home()
                cache_directory = home_directory.joinpath(".cache")
                cache_directory.mkdir(parents=True, exist_ok=True)
                cache_filepath.joinpath(".hishel.sqlite")
            self._cache_filepath = cache_filepath.resolve().absolute()

            async with self._setup_lock:
                if not self._connection:  # pragma: no cover
                    self._connection = await anysqlite.connect(self._cache_filepath, check_same_thread=False)
                table_creation_commnd = "CREATE TABLE IF NOT EXISTS cache(key TEXT, data BLOB, date_created REAL)"
                await self._connection.execute(table_creation_commnd)
                await self._connection.commit()
                self._setup_completed = True

    async def clear_cache(self) -> None:
        """
        Clears the sqlite3 cache

        1) Performs a DELETE to remove all rows without
        dropping the table
        """
        async with self._setup_lock:
            cache_table_name = "cache"
            try:
                drop_table_command = f"DELETE FROM {cache_table_name}"
                await self._connection.execute(drop_table_command)
                await self._connection.commit()
            except anysqlite.OperationalError as operational_error:
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
                await self._connection.execute(reset_autoincrement_command)
                await self._connection.commit()
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
                await self._connection.execute(vacuum_command)
                await self._connection.commit()
            except sqlite3.OperationalError as operational_error:
                logger.exception(operational_error)
                raise operational_error
            except Exception as gen_exc:
                logger.exception(gen_exc)
                raise gen_exc

    @property
    async def cache_filepath(self) -> Path:
        """
        Returns the filepath for the sqlite3 cache database

        We have either stored it because we generated it ourselves
        via `BiothingsClientSqlite3Storage.database_connection` or we
        have to look it up in the database via the following PRAGMA:
        https://www.sqlite.org/pragma.html#pragma_database_list
        """
        if self._cache_filepath is None:
            pragma_command = "PRAGMA database_list"
            async for _, name, filename in self._connection.execute(pragma_command):
                if name == "main" and filename is not None:
                    self._cache_filepath = Path(filename).resolve().absolute()
                    break
        return self._cache_filepath
