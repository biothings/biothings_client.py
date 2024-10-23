"""
Client fixtures for usage across the biothings_client testing
"""

import pytest

from biothings_client import get_async_client
from biothings_client.client.definitions import AsyncMyGeneInfo, AsyncMyChemInfo


@pytest.fixture(scope="session")
def async_gene_client() -> AsyncMyGeneInfo:
    """
    Fixture for generating an asynchronous mygene client
    """
    client = "gene"
    gene_client = get_async_client(client)
    return gene_client


@pytest.fixture(scope="session")
def async_chem_client() -> AsyncMyChemInfo:
    """
    Fixture for generating an asynchronous mychem client
    """
    client = "chem"
    chem_client = get_async_client(client)
    return chem_client
