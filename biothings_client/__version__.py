"""
Package versioning using PEP-376
https://peps.python.org/pep-0396/#pep-376-metadata
"""

try:
    from importlib import metadata
except ImportError:
    # Running on pre-3.8 Python; use importlib-metadata package
    import importlib_metadata as metadata  # type: ignore

DISTRIBUTION_NAME = "biothings_client"
__version__ = metadata.version(DISTRIBUTION_NAME)
