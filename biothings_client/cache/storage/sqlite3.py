"""
Overridden sqlite3 storage for our hishel cache instance

Primarily so we can support hard-deleting our cache without having
to wait for the TTL expiration
"""

from biothings_client._dependencies import _CACHING

if _CACHING:
    import logging
    import uuid

    import hishel
    from hishel._core._storages._packing import unpack

    logger = logging.getLogger("biothings.client")
    logger.setLevel(logging.INFO)

    class BiothingsClientSyncSqliteStorage(hishel.SyncSqliteStorage):

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        def hard_cleanup(self):
            """Fully clear everything in the entries table for our cache.

            Mirrors the _batch_cleanup method, but we pay no attention to
            the TTL and instead simply wipe the entire table. Hard resets
            our cache
            """
            try:
                entry_identifiers = []
                with self._lock:
                    cache_entries_table = "entries"
                    connection = self._ensure_connection()
                    cursor = connection.cursor()
                    entry_identifiers = cursor.execute(f"SELECT id FROM {cache_entries_table}")

                if entry_identifiers is not None:
                    breakpoint()
                    while (entry_id := entry_identifiers.fetchone()) is not None:
                        entry_uuid = uuid.UUID(bytes=entry_id[0])
                        self.hard_remove_entry(entry_uuid)
                    logger.info("Successfully cleared cache entries")
            except Exception as gen_exc:
                raise gen_exc

        def hard_remove_entry(self, id: uuid.UUID) -> None:
            """Hard delete entry in the entry database rather than soft delete.

            Identical implementation to remove_entry, except we call _hard_delete_pair
            at the end instead of _soft_delete_pair
            """
            with self._lock:
                connection = self._ensure_connection()
                cursor = connection.cursor()
                cursor.execute("SELECT data FROM entries WHERE id = ?", (id.bytes,))
                result = cursor.fetchone()

                if result is None:
                    return None

                pair = unpack(result[0], kind="pair")
                self._hard_delete_pair(pair, cursor)
                connection.commit()

    class BiothingsClientAsyncSqliteStorage(hishel.AsyncSqliteStorage):

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        async def hard_cleanup(self):
            """Fully clear everything in the entries table for our cache.

            Mirrors the _batch_cleanup method, but we pay no attention to
            the TTL and instead simply wipe the entire table. Hard resets
            our cache
            """
            try:
                entry_identifiers = None
                async with self._lock:
                    cache_entries_table = "entries"
                    connection = await self._ensure_connection()
                    cursor = await connection.cursor()
                    entry_identifiers = await cursor.execute(f"SELECT id FROM {cache_entries_table}")

                if entry_identifiers is not None:
                    while (entry_id := await entry_identifiers.fetchone()) is not None:
                        entry_uuid = uuid.UUID(bytes=entry_id[0])
                        await self.hard_remove_entry(entry_uuid)
                    logger.info("Successfully cleared cache entries")
            except Exception as gen_exc:
                raise gen_exc

        async def hard_remove_entry(self, id: uuid.UUID) -> None:
            """Hard delete entry in the entry database rather than soft delete.

            Identical implementation to remove_entry, except we call _hard_delete_pair
            at the end instead of _soft_delete_pair
            """
            async with self._lock:
                connection = await self._ensure_connection()
                cursor = await connection.cursor()
                await cursor.execute("SELECT data FROM entries WHERE id = ?", (id.bytes,))
                result = await cursor.fetchone()

                if result is None:
                    return None

                pair = unpack(result[0], kind="pair")
                await self._hard_delete_pair(pair, cursor)
                await connection.commit()
