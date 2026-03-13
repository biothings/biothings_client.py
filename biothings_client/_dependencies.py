import sys
from importlib import util

_PANDAS = util.find_spec("pandas") is not None
_CACHING = util.find_spec("hishel") is not None and util.find_spec("anysqlite") is not None
_CACHING_NOT_SUPPORTED = sys.version_info < (3, 8)
