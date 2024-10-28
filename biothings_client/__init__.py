"""
Generic client for Biothings APIs
"""

from biothings_client.client.asynchronous import AsyncBiothingClient, get_async_client
from biothings_client.client.base import BiothingClient, get_client
from biothings_client.__version__ import __version__


__all__ = ["AsyncBiothingClient", "BiothingClient", "get_client", "get_async_client", "__version__"]
