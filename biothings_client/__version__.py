import importlib.metadata

# https://peps.python.org/pep-0396/#pep-376-metadata
distribution_name = "biothings_client"
__version__ = importlib.metadata.version(distribution_name)
