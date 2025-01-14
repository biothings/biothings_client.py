"""
Test suite for the sync client
"""

from typing import List

import httpx
import pytest

import biothings_client


@pytest.mark.parametrize(
    "client_name,client_url,class_name",
    [
        (["gene"], "https://mygene.info/v3", "MyGeneInfo"),
        (["variant"], "https://myvariant.info/v1", "MyVariantInfo"),
        (["chem", "drug"], "https://mychem.info/v1", "MyChemInfo"),
        (["disease"], "https://mydisease.info/v1", "MyDiseaseInfo"),
        (["taxon"], "https://t.biothings.io/v1", "MyTaxonInfo"),
        (["geneset"], "https://mygeneset.info/v1", "MyGenesetInfo"),
    ],
)
def test_get_client(client_name: List[str], client_url: str, class_name: str):
    """
    Tests our ability to generate sync clients
    """
    client_name_instances = [biothings_client.get_client(name) for name in client_name]
    client_url_instance = biothings_client.get_client(url=client_url)
    clients = [client_url_instance, *client_name_instances]
    for client in clients:
        assert type(client).__name__ == class_name


@pytest.mark.parametrize(
    "client_name,client_url,class_name",
    [
        ("gene", "https://mygene.info/v3", "MyGeneInfo"),
        ("variant", "https://mychem.info/v1", "MyVariantInfo"),
        ("chem", "https://mychem.info/v1", "MyChemInfo"),
        ("disease", "https://mydisease.info/v1", "MyDiseaseInfo"),
        ("taxon", "https://t.biothings.io/v1", "MyTaxonInfo"),
        ("geneset", "https://mygeneset.info/v1", "MyGenesetInfo"),
    ],
)
def test_generate_settings(client_name: str, client_url: str, class_name: str):
    client_settings = biothings_client.client.base.generate_settings(client_name, url=client_url)
    assert client_settings["class_kwargs"]["_default_url"] == client_url
    assert client_settings["class_name"] == class_name


@pytest.mark.parametrize(
    "client_name",
    (
        "gene",
        "variant",
        "chem",
        "disease",
        "taxon",
        "geneset",
    ),
)
def test_url_protocol(client_name: str):
    """
    Tests that our HTTP protocol modification methods work
    as expected when transforming to either HTTP or HTTPS
    """
    client_instance = biothings_client.get_client(client_name)

    http_protocol = "http://"
    https_protocol = "https://"

    # DEFAULT: HTTPS
    assert client_instance.url.startswith(https_protocol)

    # Transform to HTTP
    client_instance.use_http()
    assert client_instance.url.startswith(http_protocol)

    # Transform back to HTTPS
    client_instance.use_https()
    client_instance.url.startswith(https_protocol)


def test_client_proxy_discovery(mock_client_proxy_configuration):
    """
    Tests for verifying that we properly auto-discover the
    proxy configuration from the environment using the built-in
    methods provided by HTTPX

    Brought to light by user issues on VPN
    https://github.com/biothings/mygene.py/issues/26#issuecomment-2588065562
    """
    client_name = "gene"
    gene_client = biothings_client.get_client(client_name)
    gene_client._build_http_client()
    http_mounts = gene_client.http_client._mounts
    assert isinstance(http_mounts, dict)
    assert len(http_mounts) == 2

    for url_pattern, http_transport in http_mounts.items():
        assert isinstance(url_pattern, httpx._utils.URLPattern)
        assert isinstance(http_transport, httpx.HTTPTransport)

        if url_pattern.pattern == "https://":
            proxy_url = http_transport._pool._proxy_url
            assert proxy_url.scheme == b"http"
            assert proxy_url.host == b"fakehttpsproxyhost"
            assert proxy_url.port == 6375
            assert proxy_url.target == b"/"

        elif url_pattern.pattern == "http://":
            proxy_url = http_transport._pool._proxy_url
            assert proxy_url.scheme == b"http"
            assert proxy_url.host == b"fakehttpproxyhost"
            assert proxy_url.port == 6374
            assert proxy_url.target == b"/"


@pytest.mark.skipif(not biothings_client._CACHING, reason="caching libraries not installed")
def test_cache_client_proxy_discovery(mock_client_proxy_configuration):
    """
    Tests for verifying that we properly auto-discover the
    proxy configuration from the environment using the built-in
    methods provided by HTTPX

    Brought to light by user issues on VPN
    https://github.com/biothings/mygene.py/issues/26#issuecomment-2588065562
    """
    client_name = "gene"
    gene_client = biothings_client.get_client(client_name)
    gene_client._build_cache_http_client()

    http_mounts = gene_client.http_client._mounts
    assert isinstance(http_mounts, dict)
    assert len(http_mounts) == 2

    for url_pattern, http_transport in gene_client.http_client._mounts.items():
        assert isinstance(url_pattern, httpx._utils.URLPattern)
        assert isinstance(http_transport, httpx.HTTPTransport)

        if url_pattern.pattern == "https://":
            proxy_url = http_transport._pool._proxy_url
            assert proxy_url.scheme == b"http"
            assert proxy_url.host == b"fakehttpsproxyhost"
            assert proxy_url.port == 6375
            assert proxy_url.target == b"/"

        elif url_pattern.pattern == "http://":
            proxy_url = http_transport._pool._proxy_url
            assert proxy_url.scheme == b"http"
            assert proxy_url.host == b"fakehttpproxyhost"
            assert proxy_url.port == 6374
            assert proxy_url.target == b"/"
