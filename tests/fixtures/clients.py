"""
All client instances from the biothings_client package

sync:
>>> MyGeneInfo client
>>> MyChemInfo client
>>> MyVariantInfo client
>>> MyGenesetInfo client

async:
>>> AsyncMyGeneInfo client
>>> AsyncMyChemInfo client
>>> AsyncMyVariantInfo client
>>> AsyncMyGenesetInfo client
"""

import pytest

from biothings_client import get_client, get_async_client
from biothings_client.client.definitions import (
    AsyncMyChemInfo,
    AsyncMyGeneInfo,
    AsyncMyGenesetInfo,
    AsyncMyVariantInfo,
    MyChemInfo,
    MyGeneInfo,
    MyGenesetInfo,
    MyVariantInfo,
)


@pytest.fixture(scope="session")
def gene_client() -> MyGeneInfo:
    """
    Fixture for generating a synchronous mygene client
    """
    client = "gene"
    gene_client = get_client(client)
    return gene_client


@pytest.fixture(scope="session")
def async_gene_client() -> AsyncMyGeneInfo:
    """
    Fixture for generating an asynchronous mygene client
    """
    client = "gene"
    gene_client = get_async_client(client)
    return gene_client


@pytest.fixture(scope="session")
def chem_client() -> MyChemInfo:
    """
    Fixture for generating a synchronous mychem client
    """
    client = "chem"
    chem_client = get_client(client)
    return chem_client


@pytest.fixture(scope="session")
def async_chem_client() -> AsyncMyChemInfo:
    """
    Fixture for generating an asynchronous mychem client
    """
    client = "chem"
    chem_client = get_async_client(client)
    return chem_client


@pytest.fixture(scope="session")
def variant_client() -> MyVariantInfo:
    """
    Fixture for generating a synchronous myvariant client
    """
    client = "variant"
    variant_client = get_client(client)
    return variant_client


@pytest.fixture(scope="session")
def async_variant_client() -> AsyncMyVariantInfo:
    """
    Fixture for generating an asynchronous myvariant client
    """
    client = "variant"
    variant_client = get_async_client(client)
    return variant_client


@pytest.fixture(scope="session")
def geneset_client() -> MyGenesetInfo:
    """
    Fixture for generating a synchronous mygeneset client
    """
    client = "geneset"
    geneset_client = get_client(client)
    return geneset_client


@pytest.fixture(scope="session")
def async_geneset_client() -> AsyncMyGenesetInfo:
    """
    Fixture for generating an asynchronous mygeneset client
    """
    client = "geneset"
    geneset_client = get_async_client(client)
    return geneset_client
