"""
Setup the local cache configuration for the client

For the moment we plan to leverage a local sqlite3 database
as our caching strategy

*** Notes ***
Import caching headers taken from hishel documentation

# Force caching of the request
client.post(
    "https://example.com",
    extensions={"force_cache": True}
)


# Return a regular response if it is in the cache; else, return a 504 status code.
client.post(
        "https://example.com",
        headers=[("Cache-Control", "only-if-cached")]
)


# Ignore cached responses and do not store incoming responses!
response = client.post(
        "https://example.com",
        extensions={"cache_disabled": True}
)

"""

import hishel


def build_cache_client() -> hishel.CacheClient:
    """
    Builds a synchronous hishel httpx client
    """
    # specification configs
    controller = hishel.Controller(
        # Cache only GET and POST methods
        cacheable_methods=["GET", "POST"],
        # Cache only 200 status codes
        cacheable_status_codes=[200],
        # Use the stale response if there is a connection issue and the new response cannot be obtained.
        allow_stale=True,
        # First, revalidate the response and then utilize it.
        # If the response has not changed, do not download the
        # entire response data from the server; instead,
        # use the one you have because you know it has not been modified.
        always_revalidate=True,
    )

    # storage configurations
    storage = hishel.SQLiteStorage()
    client = hishel.CacheClient(controller=controller, storage=storage)
    return client


def build_async_cache_client() -> hishel.AsyncCacheClient:
    """
    Builds a synchronous hishel httpx client
    """
    # specification configurations
    controller = hishel.Controller(
        # Cache only GET and POST methods
        cacheable_methods=["GET", "POST"],
        # Cache only 200 status codes
        cacheable_status_codes=[200],
        # Use the stale response if there is a connection issue and the new response cannot be obtained.
        allow_stale=True,
        # First, revalidate the response and then utilize it.
        # If the response has not changed, do not download the
        # entire response data from the server; instead,
        # use the one you have because you know it has not been modified.
        always_revalidate=True,
    )

    # storage configurations
    storage = hishel.SQLiteStorage()
    client = hishel.AsyncCacheClient(controller=controller, storage=storage)
    return client
