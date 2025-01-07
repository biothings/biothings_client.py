import sys
import importlib


_PANDAS = importlib.util.find_spec("pandas") is not None
_CACHING = importlib.util.find_spec("hishel") is not None and importlib.util.find_spec("anysqlite") is not None
_CACHING_NOT_SUPPORTED = sys.version_info < (3, 8)
