"""
Generic client for Biothings APIs
"""

import importlib

from biothings_client.client.asynchronous import AsyncBiothingClient, get_async_client
from biothings_client.client.base import BiothingClient, get_client
from biothings_client.__version__ import __version__


__PANDAS = importlib.util.find_spec("pandas") is not None
__CACHING = importlib.util.find_spec("hishel") is not None and importlib.util.find_spec("anysqlite") is not None


__all__ = ["AsyncBiothingClient", "BiothingClient", "get_client", "get_async_client", "__version__"]
