"""Tests for fetch_all paging with search_after and its fallback to scrolling.

They run against a mocked BioThings API, so they don't depend on the version deployed.
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List

import httpx
import pytest

from biothings_client import get_async_client, get_client
from biothings_client.client.definitions import AsyncMyGeneInfo, MyGeneInfo

HITS = [{"_id": str(number)} for number in range(25)]

# the requests query("cdk*", fields="symbol", fetch_all=True) makes when the server pages with search_after
SEARCH_AFTER_REQUESTS = [
    {"q": "cdk*", "fields": "symbol", "search_after": "*"},
    {"q": "cdk*", "fields": "symbol", "search_after": "10"},
    {"q": "cdk*", "fields": "symbol", "search_after": "20"},
]
# and when it falls back to scrolling
SCROLL_REQUESTS = [
    {"q": "cdk*", "fields": "symbol", "search_after": "*"},
    {"q": "cdk*", "fields": "symbol", "fetch_all": "true"},
    {"fields": "symbol", "scroll_id": "10"},
    {"fields": "symbol", "scroll_id": "20"},
    {"fields": "symbol", "scroll_id": "30"},
]


@dataclass
class MockQueryAPI:
    """Serves the /query endpoint of a BioThings API with HITS, 10 hits per request.

    search_after is "supported" to page with search_after, like BioThings SDK 1.2 and later,
    "ignored" to treat it as an unknown parameter, like servers before 1.2, or "rejected" to
    respond with the 400 error 1.2 gives for options search_after does not support (facets).
    """

    search_after: str = "supported"
    requests: List[Dict[str, str]] = field(default_factory=list)

    def __call__(self, request: httpx.Request) -> httpx.Response:
        params = dict(request.url.params)
        self.requests.append(params)

        if "search_after" in params and self.search_after == "rejected":
            details = "search_after does not support facets, request them in a separate query."
            return httpx.Response(400, json={"code": 400, "success": False, "error": "ValueError", "details": details})

        if "search_after" in params and self.search_after == "supported":
            start = 0 if params["search_after"] == "*" else int(params["search_after"])
            body: Dict[str, Any] = {"total": len(HITS), "hits": HITS[start : start + 10]}
            if start + 10 < len(HITS):
                body["_search_after"] = str(start + 10)
            return httpx.Response(200, json=body)

        # scrolling, the scroll id is the index of the next hit in this mock
        if "scroll_id" in params:
            start = int(params["scroll_id"])
            if start >= len(HITS):
                return httpx.Response(200, json={"success": False, "error": "No more results to return."})
            return httpx.Response(200, json={"_scroll_id": str(start + 10), "hits": HITS[start : start + 10]})
        if params.get("fetch_all") == "true":
            return httpx.Response(200, json={"_scroll_id": "10", "total": len(HITS), "hits": HITS[:10]})

        return httpx.Response(200, json={"total": len(HITS), "hits": HITS[:10]})


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
    assert api.requests == SEARCH_AFTER_REQUESTS


@pytest.mark.parametrize("search_after", ["ignored", "rejected"])
def test_fetch_all_scroll_fallback(search_after: str, caplog: pytest.LogCaptureFixture):
    api = MockQueryAPI(search_after)
    hits = list(mock_client(api).query("cdk*", fields="symbol", fetch_all=True))

    # the first page of a server that ignores search_after is discarded, not yielded again
    assert hits == HITS
    assert api.requests == SCROLL_REQUESTS
    # the end of the scroll is not an error
    assert not [record for record in caplog.records if record.levelno >= logging.ERROR]


@pytest.mark.asyncio
async def test_async_fetch_all_search_after():
    api = MockQueryAPI()
    hits = [hit async for hit in await mock_async_client(api).query("cdk*", fields="symbol", fetch_all=True)]

    assert hits == HITS
    assert api.requests == SEARCH_AFTER_REQUESTS


@pytest.mark.asyncio
@pytest.mark.parametrize("search_after", ["ignored", "rejected"])
async def test_async_fetch_all_scroll_fallback(search_after: str):
    api = MockQueryAPI(search_after)
    hits = [hit async for hit in await mock_async_client(api).query("cdk*", fields="symbol", fetch_all=True)]

    assert hits == HITS
    assert api.requests == SCROLL_REQUESTS
