"""
Tests for paging through fetch_all results with search_after, and the fallback to
scrolling, against a mocked BioThings API so they don't depend on the deployed version
"""

import logging
from typing import Any, Dict, List

import httpx
import pytest

from biothings_client import get_async_client, get_client
from biothings_client.client.definitions import AsyncMyGeneInfo, MyGeneInfo

HITS = [{"_id": str(number)} for number in range(25)]


class MockQueryAPI:
    """
    Serves the /query endpoint of a BioThings API with HITS, a page of `size` hits
    (default 10) per request.

    :param search_after: "supported" pages with search_after, like BioThings SDK 1.2 and later,
                         "ignored" treats it as an unknown parameter, like servers before 1.2,
                         "rejected" responds with the 400 error 1.2 gives for options search_after
                         does not support (facets)
    """

    def __init__(self, search_after: str = "supported") -> None:
        self.search_after = search_after
        self.requests: List[Dict[str, str]] = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        params = dict(request.url.params)
        self.requests.append(params)
        size = int(params.get("size", 10))

        if params.get("q") == "(":
            return httpx.Response(400, json={"code": 400, "success": False, "error": "Invalid query"})

        if "search_after" in params and self.search_after == "rejected":
            details = "search_after does not support facets, request them in a separate query."
            return httpx.Response(400, json={"code": 400, "success": False, "error": "ValueError", "details": details})

        if "search_after" in params and self.search_after == "supported":
            start = 0 if params["search_after"] == "*" else int(params["search_after"])
            body: Dict[str, Any] = {"total": len(HITS), "hits": HITS[start : start + size]}
            if start + size < len(HITS):
                body["_search_after"] = str(start + size)
            return httpx.Response(200, json=body)

        # scrolling, the scroll id is the index of the next hit in this mock
        if "scroll_id" in params:
            start = int(params["scroll_id"])
            if start >= len(HITS):
                return httpx.Response(200, json={"success": False, "error": "No more results to return."})
            return httpx.Response(200, json={"_scroll_id": str(start + 10), "hits": HITS[start : start + 10]})
        if params.get("fetch_all") == "true":
            return httpx.Response(200, json={"_scroll_id": "10", "total": len(HITS), "hits": HITS[:10]})

        return httpx.Response(200, json={"total": len(HITS), "hits": HITS[:size]})


def mock_client(api: MockQueryAPI) -> MyGeneInfo:
    client = get_client("gene")
    client.http_client = httpx.Client(transport=httpx.MockTransport(api))
    client.http_client_setup = True
    return client


def mock_async_client(api: MockQueryAPI) -> AsyncMyGeneInfo:
    client = get_async_client("gene")
    client.http_client = httpx.AsyncClient(transport=httpx.MockTransport(api))
    client.http_client_setup = True
    return client


def test_fetch_all_search_after():
    api = MockQueryAPI()
    hits = list(mock_client(api).query("cdk*", fields="symbol", fetch_all=True))

    assert hits == HITS
    # each page sends the same query with the _search_after value of the previous page
    assert api.requests == [
        {"q": "cdk*", "fields": "symbol", "search_after": "*"},
        {"q": "cdk*", "fields": "symbol", "search_after": "10"},
        {"q": "cdk*", "fields": "symbol", "search_after": "20"},
    ]


def test_fetch_all_search_after_size():
    api = MockQueryAPI()
    hits = list(mock_client(api).query("cdk*", size=20, fetch_all=True))

    assert hits == HITS
    assert [request["search_after"] for request in api.requests] == ["*", "20"]


def test_fetch_all_single_page():
    # all hits on the first page whether or not the server supports search_after, no fallback
    api = MockQueryAPI(search_after="ignored")
    hits = list(mock_client(api).query("cdk*", size=50, fetch_all=True))

    assert hits == HITS
    assert len(api.requests) == 1


def test_fetch_all_scroll_when_search_after_ignored(caplog: pytest.LogCaptureFixture):
    api = MockQueryAPI(search_after="ignored")
    hits = list(mock_client(api).query("cdk*", fields="symbol", fetch_all=True))

    # the first page of the regular query is discarded, not yielded again
    assert hits == HITS
    assert api.requests == [
        {"q": "cdk*", "fields": "symbol", "search_after": "*"},
        {"q": "cdk*", "fields": "symbol", "fetch_all": "true"},
        {"fields": "symbol", "scroll_id": "10"},
        {"fields": "symbol", "scroll_id": "20"},
        {"fields": "symbol", "scroll_id": "30"},
    ]
    # the end of the scroll is not an error
    assert not [record for record in caplog.records if record.levelno >= logging.ERROR]


def test_fetch_all_scroll_when_search_after_rejected(caplog: pytest.LogCaptureFixture):
    api = MockQueryAPI(search_after="rejected")
    hits = list(mock_client(api).query("cdk*", facets="taxid", fetch_all=True))

    assert hits == HITS
    assert api.requests[1] == {"q": "cdk*", "facets": "taxid", "fetch_all": "true"}
    assert "search_after does not support facets" in caplog.text


def test_fetch_all_query_error():
    # an error that isn't about search_after is raised, without scrolling
    api = MockQueryAPI()
    with pytest.raises(httpx.HTTPStatusError):
        list(mock_client(api).query("(", fetch_all=True))
    assert len(api.requests) == 1


@pytest.mark.asyncio
async def test_async_fetch_all_search_after():
    api = MockQueryAPI()
    hits = [hit async for hit in await mock_async_client(api).query("cdk*", fields="symbol", fetch_all=True)]

    assert hits == HITS
    assert [request["search_after"] for request in api.requests] == ["*", "10", "20"]


@pytest.mark.asyncio
async def test_async_fetch_all_scroll_when_search_after_ignored():
    api = MockQueryAPI(search_after="ignored")
    hits = [hit async for hit in await mock_async_client(api).query("cdk*", fetch_all=True)]

    assert hits == HITS
    assert [request.get("scroll_id") for request in api.requests] == [None, None, "10", "20", "30"]


@pytest.mark.asyncio
async def test_async_fetch_all_scroll_when_search_after_rejected():
    api = MockQueryAPI(search_after="rejected")
    hits = [hit async for hit in await mock_async_client(api).query("cdk*", facets="taxid", fetch_all=True)]

    assert hits == HITS
    assert api.requests[1] == {"q": "cdk*", "facets": "taxid", "fetch_all": "true"}
