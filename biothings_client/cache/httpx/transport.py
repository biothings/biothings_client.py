import httpx


DEFAULT_CACHE_TIMEOUT = 7 * 24 * 60 * 60


class ForcedCacheTransport(httpx.HTTPTransport):
    """
    Taken from https://github.com/Kaggle/kaggle-benchmarks/blob/ci/src/kaggle_benchmarks/utils.py#L15C1-L63C1
    """

    def __init__(self, cache_timeout_seconds: int = None) -> None:
        super().__init__()

        if cache_timeout_seconds is None:
            cache_timeout_seconds = DEFAULT_CACHE_TIMEOUT
        self.cache_timeout_seconds = cache_timeout_seconds

    def handle_request(self, request: httpx.Request):
        response: httpx.Response = super().handle_request(request)

        # Force the header to be cacheable for 1 week
        # This overrides whatever the server said (e.g. no-store)
        response.headers["Cache-Control"] = f"public, max-age={self.cache_timeout_seconds}"

        # Remove 'Expires' or 'Pragma' if they exist to avoid conflicts
        response.headers.pop("Pragma", None)
        response.headers.pop("Expires", None)

        return response


class ForcedCacheAsyncTransport(httpx.AsyncHTTPTransport):
    """
    Asynchronous version of the ForcedCacheTransport
    """

    def __init__(self, cache_timeout_seconds: int = None) -> None:
        super().__init__()

        if cache_timeout_seconds is None:
            cache_timeout_seconds = DEFAULT_CACHE_TIMEOUT
        self.cache_timeout_seconds = cache_timeout_seconds

    async def handle_async_request(self, request: httpx.Request):
        response: httpx.Response = await super().handle_async_request(request)

        # Force the header to be cacheable for 1 week
        # This overrides whatever the server said (e.g. no-store)
        response.headers["Cache-Control"] = f"public, max-age={self.cache_timeout_seconds}"

        # Remove 'Expires' or 'Pragma' if they exist to avoid conflicts
        response.headers.pop("Pragma", None)
        response.headers.pop("Expires", None)

        return response
