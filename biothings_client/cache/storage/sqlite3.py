"""
Overridden sqlite3 storage for our hishel cache instance

Primarily so we can support hard-deleting our cache without having
to wait for the TTL expiration
"""

import sqlite3
from typing import Any

from biothings_client._dependencies import _CACHING

if _CACHING:
    import logging
    import uuid

    import hishel  # type: ignore[import-not-found]
    from hishel._core._storages._packing import unpack  # type: ignore[import-not-found]

    logger = logging.getLogger("biothings.client")
    logger.setLevel(logging.INFO)

    class BiothingsClientSyncSqliteStorage(hishel.SyncSqliteStorage):
        """Overriden SyncSqliteStorage instance for biothings-client."""

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        def hard_cleanup(self):
            """Fully clear everything in the entries table for our cache.

            Mirrors the _batch_cleanup method, but we pay no attention to
            the TTL and instead simply wipe the entire table. Hard resets
            our cache
            """
            try:
                entry_identifiers = self.get_entries_table()
                if entry_identifiers is not None:
                    while (entry_id := entry_identifiers.fetchone()) is not None:
                        entry_uuid = uuid.UUID(bytes=entry_id[0])
                        self.hard_remove_entry(entry_uuid)
                    logger.info("Successfully cleared cache entries")
                self.rebuild_cache_database()
            except Exception as gen_exc:
                raise gen_exc

        def get_entries_table(self) -> sqlite3.Cursor:
            """Get all rows in the `entries` cache table."""
            entry_identifiers = None
            with self._lock:
                cache_entries_table = "entries"
                connection = self._ensure_connection()
                cursor = connection.cursor()
                entry_identifiers = cursor.execute("SELECT id FROM %s", (cache_entries_table,))
            return entry_identifiers

        def rebuild_cache_database(self) -> None:
            """Runs the VACUUM directive to rebuild our database after wipe."""
            with self._lock:
                connection = self._ensure_connection()
                cursor = connection.cursor()
                cursor.execute("VACUUM")

        def hard_remove_entry(self, id: uuid.UUID) -> None:  # pylint: disable=W0622
            """Hard delete entry in the entry database rather than soft delete.

            Identical implementation to remove_entry, except we call _hard_delete_pair
            at the end instead of _soft_delete_pair
            """
            with self._lock:
                connection = self._ensure_connection()
                cursor = connection.cursor()
                cursor.execute("SELECT data FROM entries WHERE id = ?", (id.bytes,))
                result = cursor.fetchone()

                if result is not None:
                    pair = unpack(result[0], kind="pair")
                    assert pair is not None
                    self._hard_delete_pair(pair, cursor)
                    connection.commit()

    class BiothingsClientAsyncSqliteStorage(hishel.AsyncSqliteStorage):
        """Overriden AsyncSqliteStorage instance for biothings-client."""

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        async def hard_cleanup(self):
            """Fully clear everything in the entries table for our cache.

            Mirrors the _batch_cleanup method, but we pay no attention to
            the TTL and instead simply wipe the entire table. Hard resets
            our cache
            """
            try:
                entry_identifiers = await self.get_entries_table()
                if entry_identifiers is not None:
                    while (entry_id := await entry_identifiers.fetchone()) is not None:
                        entry_uuid = uuid.UUID(bytes=entry_id[0])
                        await self.hard_remove_entry(entry_uuid)
                    logger.info("Successfully cleared cache entries")
                await self.rebuild_cache_database()
            except Exception as gen_exc:
                raise gen_exc

        async def get_entries_table(self) -> Any:
            """Get all rows in the `entries` cache table."""
            entry_identifiers = None
            async with self._lock:
                cache_entries_table = "entries"
                connection = await self._ensure_connection()
                cursor = await connection.cursor()
                entry_identifiers = await cursor.execute("SELECT id FROM %s", (cache_entries_table,))
            return entry_identifiers

        async def rebuild_cache_database(self) -> None:
            """Runs the VACUUM directive to rebuild our database after wipe."""
            async with self._lock:
                connection = await self._ensure_connection()
                cursor = await connection.cursor()
                await cursor.execute("VACUUM")

        async def hard_remove_entry(self, id: uuid.UUID) -> None:  # pylint: disable=W0622
            """Hard delete entry in the entry database rather than soft delete.

            Identical implementation to remove_entry, except we call _hard_delete_pair
            at the end instead of _soft_delete_pair
            """
            async with self._lock:
                connection = await self._ensure_connection()
                cursor = await connection.cursor()
                await cursor.execute("SELECT data FROM entries WHERE id = ?", (id.bytes,))
                result = await cursor.fetchone()

                if result is not None:
                    pair = unpack(result[0], kind="pair")
                    assert pair is not None
                    await self._hard_delete_pair(pair, cursor)
                    await connection.commit()
