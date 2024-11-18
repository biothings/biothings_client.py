"""
Tests the client caching functionality
"""

from typing import Callable, Union

import pytest

from biothings_client.client.base import get_client


@pytest.mark.parametrize(
    "method,client,function,function_arguments",
    [
        ("GET", "gene", "getgene", {"_id": "1017", "return_raw": True}),
        ("POST", "gene", "getgenes", {"ids": ["1017", "1018"], "return_raw": True}),
        ("GET", "gene", "query", {"q": "cdk2", "return_raw": True}),
        ("POST", "gene", "querymany", {"q": ["1017", "695"], "return_raw": True}),
        (
            "GET",
            "chem",
            "getdrug",
            {"_id": "ZRALSGWEFCBTJO-UHFFFAOYSA-N", "return_raw": True},
        ),
        (
            "POST",
            "chem",
            "getdrugs",
            {"ids": ["ZRALSGWEFCBTJO-UHFFFAOYSA-N", "RRUDCFGSUDOHDG-UHFFFAOYSA-N"], "return_raw": True},
        ),
        (
            "GET",
            "chem",
            "query",
            {"q": "chebi.name:albendazole", "size": 5, "return_raw": True},
        ),
        ("POST", "chem", "querymany", {"q": ["CHEBI:31690", "CHEBI:15365"], "scopes": "chebi.id", "return_raw": True}),
        ("GET", "variant", "getvariant", {"_id": "chr9:g.107620835G>A", "return_raw": True}),
        ("POST", "variant", "getvariants", {"ids": ["chr9:g.107620835G>A", "chr1:g.876664G>A"], "return_raw": True}),
        ("GET", "variant", "query", {"q": "dbsnp.rsid:rs58991260", "return_raw": True}),
        ("POST", "variant", "querymany", {"q": ["rs58991260", "rs2500"], "scopes": "dbsnp.rsid", "return_raw": True}),
        ("GET", "geneset", "getgeneset", {"_id": "WP100", "return_raw": True}),
        ("POST", "geneset", "getgenesets", {"ids": ["WP100", "WP101"], "return_raw": True}),
        ("GET", "geneset", "query", {"q": "wnt", "fields": "name,count,source,taxid", "return_raw": True}),
        (
            "POST",
            "geneset",
            "querymany",
            {"q": ["wnt", "jak-stat"], "fields": "name,count,source,taxid", "return_raw": True},
        ),
    ],
)
def test_caching_get(method: str, client: str, function: str, function_arguments: dict):
    """
    Test the GET method with caching enabled for the specific client
    """
    client_instance = get_client(client)
    client_instance.set_caching()
    assert client_instance.caching_enabled
    client_instance.clear_cache()

    client_callback = getattr(client_instance, function)
    assert isinstance(client_callback, Callable)
    cold_response = client_callback(**function_arguments)
    hot_response = client_callback(**function_arguments)

    client_instance.stop_caching()
    forced_cold_response = client_callback(**function_arguments)
    client_instance.set_caching()
    hot_response2 = client_callback(**function_arguments)
    client_instance.clear_cache()
    forced_cold_response2 = client_callback(**function_arguments)
    hot_response3 = client_callback(**function_arguments)

    responses = [cold_response, forced_cold_response, forced_cold_response2, hot_response, hot_response2, hot_response3]
    client_instance.clear_cache()
