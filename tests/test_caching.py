"""
Tests the client caching functionality
"""

import datetime
import logging
from typing import Callable

import pytest

import biothings_client
from biothings_client.client.asynchronous import get_async_client
from biothings_client.client.base import get_client


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


@pytest.mark.skipif(not biothings_client._CACHING, reason="caching libraries not installed")
@pytest.mark.parametrize(
    "method,client,function,function_arguments",
    [
        ("GET", "gene", "getgene", {"_id": "1017", "return_raw": True}),
        ("POST", "gene", "getgenes", {"ids": ["1017", "1018"], "return_raw": True}),
        ("GET", "gene", "query", {"q": "cdk2", "return_raw": True}),
        ("POST", "gene", "querymany", {"qterms": ["1017", "695"], "return_raw": True}),
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
        (
            "POST",
            "chem",
            "querymany",
            {"qterms": ["CHEBI:31690", "CHEBI:15365"], "scopes": "chebi.id", "return_raw": True},
        ),
        ("GET", "variant", "getvariant", {"_id": "chr9:g.107620835G>A", "return_raw": True}),
        ("POST", "variant", "getvariants", {"ids": ["chr9:g.107620835G>A", "chr1:g.876664G>A"], "return_raw": True}),
        ("GET", "variant", "query", {"q": "dbsnp.rsid:rs58991260", "return_raw": True}),
        (
            "POST",
            "variant",
            "querymany",
            {"qterms": ["rs58991260", "rs2500"], "scopes": "dbsnp.rsid", "return_raw": True},
        ),
        ("GET", "geneset", "getgeneset", {"_id": "WP100", "return_raw": True}),
        ("POST", "geneset", "getgenesets", {"ids": ["WP100", "WP101"], "return_raw": True}),
        ("GET", "geneset", "query", {"q": "wnt", "fields": "name,count,source,taxid", "return_raw": True}),
        (
            "POST",
            "geneset",
            "querymany",
            {"qterms": ["wnt", "jak-stat"], "fields": "name,count,source,taxid", "return_raw": True},
        ),
    ],
)
def test_sync_caching(method: str, client: str, function: str, function_arguments: dict):
    """
    Tests sync caching methods for a variety of data
    """
    try:
        client_instance = get_client(client)
        client_instance._build_http_client()
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
        cold_response2 = client_callback(**function_arguments)
        client_instance.clear_cache()
        forced_cold_response2 = client_callback(**function_arguments)
        hot_response2 = client_callback(**function_arguments)

        cold_responses = [cold_response, cold_response2, forced_cold_response, forced_cold_response2]
        hot_responses = [hot_response, hot_response2]
        for cold_response in cold_responses:
            assert cold_response.status_code == 200
            assert not cold_response.extensions.get("from_cache", False)
            assert not cold_response.extensions.get("revalidated", False)

        for hot_response in hot_responses:
            assert hot_response.status_code == 200
            assert hot_response.extensions["from_cache"]
            assert not hot_response.extensions["revalidated"]
            assert isinstance(hot_response.extensions["cache_metadata"]["created_at"], datetime.datetime)
            assert hot_response.extensions["cache_metadata"]["number_of_uses"] >= 1
            assert all(hot_response.elapsed < cold_response.elapsed for cold_response in cold_responses)

    except Exception as gen_exc:
        client_instance.clear_cache()
        logger.exception(gen_exc)
        raise gen_exc


@pytest.mark.asyncio
@pytest.mark.skipif(not biothings_client._CACHING, reason="caching libraries not installed")
@pytest.mark.parametrize(
    "method,client,function,function_arguments",
    [
        ("GET", "gene", "getgene", {"_id": "1017", "return_raw": True}),
        ("POST", "gene", "getgenes", {"ids": ["1017", "1018"], "return_raw": True}),
        ("GET", "gene", "query", {"q": "cdk2", "return_raw": True}),
        ("POST", "gene", "querymany", {"qterms": ["1017", "695"], "return_raw": True}),
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
        (
            "POST",
            "chem",
            "querymany",
            {"qterms": ["CHEBI:31690", "CHEBI:15365"], "scopes": "chebi.id", "return_raw": True},
        ),
        ("GET", "variant", "getvariant", {"_id": "chr9:g.107620835G>A", "return_raw": True}),
        ("POST", "variant", "getvariants", {"ids": ["chr9:g.107620835G>A", "chr1:g.876664G>A"], "return_raw": True}),
        ("GET", "variant", "query", {"q": "dbsnp.rsid:rs58991260", "return_raw": True}),
        (
            "POST",
            "variant",
            "querymany",
            {"qterms": ["rs58991260", "rs2500"], "scopes": "dbsnp.rsid", "return_raw": True},
        ),
        ("GET", "geneset", "getgeneset", {"_id": "WP100", "return_raw": True}),
        ("POST", "geneset", "getgenesets", {"ids": ["WP100", "WP101"], "return_raw": True}),
        ("GET", "geneset", "query", {"q": "wnt", "fields": "name,count,source,taxid", "return_raw": True}),
        (
            "POST",
            "geneset",
            "querymany",
            {"qterms": ["wnt", "jak-stat"], "fields": "name,count,source,taxid", "return_raw": True},
        ),
    ],
)
async def test_async_caching(method: str, client: str, function: str, function_arguments: dict):
    """
    Tests async caching methods for a variety of data
    """
    try:
        client_instance = get_async_client(client)
        await client_instance._build_http_client()
        await client_instance.set_caching()
        assert client_instance.caching_enabled
        await client_instance.clear_cache()

        client_callback = getattr(client_instance, function)
        assert isinstance(client_callback, Callable)
        cold_response = await client_callback(**function_arguments)
        hot_response = await client_callback(**function_arguments)

        await client_instance.stop_caching()
        forced_cold_response = await client_callback(**function_arguments)
        await client_instance.set_caching()
        cold_response2 = await client_callback(**function_arguments)
        await client_instance.clear_cache()
        forced_cold_response2 = await client_callback(**function_arguments)
        hot_response2 = await client_callback(**function_arguments)

        cold_responses = [cold_response, cold_response2, forced_cold_response, forced_cold_response2]
        hot_responses = [hot_response, hot_response2]
        for cold_response in cold_responses:
            assert cold_response.status_code == 200
            assert not cold_response.extensions.get("from_cache", False)
            assert not cold_response.extensions.get("revalidated", False)

        for hot_response in hot_responses:
            assert hot_response.status_code == 200
            assert hot_response.extensions["from_cache"]
            assert not hot_response.extensions["revalidated"]
            assert isinstance(hot_response.extensions["cache_metadata"]["created_at"], datetime.datetime)
            assert hot_response.extensions["cache_metadata"]["number_of_uses"] >= 1
            assert all(hot_response.elapsed < cold_response.elapsed for cold_response in cold_responses)

    except Exception as gen_exc:
        await client_instance.clear_cache()
        logger.exception(gen_exc)
        raise gen_exc
