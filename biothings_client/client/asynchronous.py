"""
Async Python Client for generic Biothings API services
"""

from collections.abc import Iterable
from copy import copy
from pathlib import Path
from typing import Dict, Union, Tuple
import logging
import platform
import warnings


import httpx

from biothings_client.client.settings import (
    COMMON_ALIASES,
    COMMON_KWARGS,
    MYCHEM_ALIASES,
    MYCHEM_KWARGS,
    MYDISEASE_ALIASES,
    MYDISEASE_KWARGS,
    MYGENESET_ALIASES,
    MYGENESET_KWARGS,
    MYGENE_ALIASES,
    MYGENE_KWARGS,
    MYTAXON_ALIASES,
    MYTAXON_KWARGS,
    MYVARIANT_ALIASES,
    MYVARIANT_KWARGS,
)
from biothings_client.__version__ import __version__
from biothings_client._dependencies import _CACHING, _CACHING_NOT_SUPPORTED, _PANDAS
from biothings_client.client.exceptions import CachingNotSupportedError, OptionalDependencyImportError
from biothings_client.mixins.gene import MyGeneClientMixin
from biothings_client.mixins.variant import MyVariantClientMixin
from biothings_client.utils.copy import copy_func
from biothings_client.utils.iteration import concatenate_list, iter_n, list_itemcnt

if _PANDAS:
    import pandas

if _CACHING:
    import hishel
    from biothings_client.cache.storage import AsyncBiothingsClientSqlite3Cache

logger = logging.getLogger("biothings.client")
logger.setLevel(logging.INFO)


PROXY_MOUNT = Dict[str, Union[httpx.BaseTransport, None]]


# Future work:
# Consider use "verbose" settings to control default logging output level
# by doing this instead of using branching throughout the application,
# the business logic can be more concise and more readable.
class AsyncBiothingClient:
    """
    async http client class for accessing the biothings web services
    """

    def __init__(self, url: str = None):
        if url is None:
            url = self._default_url
        self.url = url
        if self.url[-1] == "/":
            self.url = self.url[:-1]

        self.max_query = self._max_query

        # delay and step attributes are for batch queries.
        self.delay = self._delay  # delay is ignored when requests made from cache.
        self.step = self._step

        self.scroll_size = self._scroll_size

        # raise httpx.HTTPError for status_code > 400
        # > but not for 404 on getvariant
        # > set to False to suppress the exceptions.
        self.raise_for_status = True

        self.default_user_agent = (
            "{package_header}/{client_version} (" "python:{python_version} " "httpx:{httpx_version}" ")"
        ).format(
            **{
                "package_header": self._pkg_user_agent_header,
                "client_version": __version__,
                "python_version": platform.python_version(),
                "httpx_version": httpx.__version__,
            }
        )
        self.http_client = None
        self.cache_storage = None
        self.http_client_setup = False
        self.caching_enabled = False

    async def _build_http_client(self, cache_db: Union[str, Path] = None) -> None:
        """
        Builds the async client instance for usage through the lifetime
        of the biothings_client

        This modifies the state of the BiothingsClient instance
        to set the values for the http_client property

        For the moment, we have disabled timeouts. This matches our prior
        behavior we had with the requests library, which by default did not
        specify a timeout when making a request. In the future this should
        be modified to prevent indefinite hanging with potentially bad network
        connections

        Inputs:
        :param cache_db: pathlike object to the local sqlite3 cache database file

        Outputs:
        :return: None
        """
        if not self.http_client_setup:
            self.http_client = httpx.AsyncClient()
            self.http_client = httpx.AsyncClient(timeout=None)
            self.http_client_setup = True
            self.http_cache_client_setup = False

    async def _build_cache_http_client(self, cache_db: Union[str, Path] = None) -> None:
        """
        Builds the client instance used for caching biothings requests.
        We rebuild the client whenever we enable to caching to ensure
        that we don't create a database files unless the user explicitly
        wants to leverage request caching

        This modifies the state of the BiothingsClient instance
        to set the values for the http_client property and the cache_storage property

        For the moment, we have disabled timeouts. This matches our prior
        behavior we had with the requests library, which by default did not
        specify a timeout when making a request. In the future this should
        be modified to prevent indefinite hanging with potentially bad network
        connections

        Inputs:
        :param cache_db: pathlike object to the local sqlite3 cache database file

        Outputs:
        :return: None
        """
        if not self.http_client_setup:
            if cache_db is None:
                cache_db = self._default_cache_file
            cache_db = Path(cache_db).resolve().absolute()

            self.cache_storage = AsyncBiothingsClientSqlite3Cache()
            await self.cache_storage.setup_database_connection(cache_db)

            async_http_transport = httpx.AsyncHTTPTransport()
            cache_transport = hishel.AsyncCacheTransport(transport=async_http_transport, storage=self.cache_storage)
            cache_controller = hishel.Controller(cacheable_methods=["GET", "POST"])

            # Have to manually build the proxy mounts as httpx will not auto-discover
            # proxies if we provide our own HTTPTransport to the Client constructor
            proxy_mounts = self._build_caching_proxy_mounts()
            self.http_client = hishel.AsyncCacheClient(
                controller=cache_controller,
                transport=cache_transport,
                storage=self.cache_storage,
                mounts=proxy_mounts,
                timeout=None,
            )
            self.http_client_setup = True

    def _build_caching_proxy_mounts(self) -> PROXY_MOUNT:
        """
        Builds the proxy mounts for case where we have a CacheTransport.
        Autodiscovery of proxies only works when don't provide a transport
        to the client so this method acts as a replacement for that
        """
        proxy_map = httpx._utils.get_environment_proxies()
        proxy_mounts: PROXY_MOUNT = {}
        for key, proxy in proxy_map.items():
            proxy_transport = None
            if proxy is not None:
                proxy_transport = httpx.AsyncHTTPTransport(
                    verify=True,
                    cert=None,
                    trust_env=True,
                    http1=True,
                    http2=False,
                    limits=httpx._config.DEFAULT_LIMITS,
                    proxy=proxy,
                )
            proxy_mounts[key] = proxy_transport
        proxy_mounts = dict(sorted(proxy_mounts.items()))
        return proxy_mounts

    async def __del__(self):
        """
        Destructor for the client to ensure that we close any potential
        connections to the cache database
        """
        try:
            if self.http_client is not None:
                await self.http_client.aclose()
        except Exception as gen_exc:
            logger.exception(gen_exc)
            logger.error("Unable to close the httpx client instance %s", self.http_client)

    def use_http(self):
        """
        Use http instead of https for API calls.
        """
        if self.url:
            self.url = self.url.replace("https://", "http://")

    def use_https(self):
        """
        Use https instead of http for API calls. This is the default.
        """
        if self.url:
            self.url = self.url.replace("http://", "https://")

    @staticmethod
    async def _dataframe(obj, dataframe, df_index=True):
        """
        Converts object to DataFrame (pandas)
        """
        if _PANDAS:
            # if dataframe not in ["by_source", "normal"]:
            if dataframe not in [1, 2]:
                raise ValueError("dataframe must be either 1 (using json_normalize) or 2 (using DataFrame.from_dict")

            if "hits" in obj:
                if dataframe == 1:
                    df = pandas.json_normalize(obj["hits"])
                else:
                    df = pandas.DataFrame.from_dict(obj)
            else:
                if dataframe == 1:
                    df = pandas.json_normalize(obj)
                else:
                    df = pandas.DataFrame.from_dict(obj)
            if df_index:
                df = df.set_index("query")
            return df
        else:
            dataframe_library_error = OptionalDependencyImportError(
                optional_function_access="enable dataframe conversion", optional_group="dataframe", libraries=["pandas"]
            )
            raise dataframe_library_error

    async def _get(
        self, url: str, params: dict = None, none_on_404: bool = False, verbose: bool = True
    ) -> Tuple[bool, httpx.Response]:
        """
        Wrapper around the httpx.get method
        """
        await self._build_http_client()
        if params is None:
            params = {}

        debug = params.pop("debug", False)
        return_raw = params.pop("return_raw", False)
        headers = {"user-agent": self.default_user_agent}
        response = await self.http_client.get(
            url=url, params=params, headers=headers, extensions={"cache_disabled": not self.caching_enabled}
        )

        response_extensions = response.extensions
        from_cache = response_extensions.get("from_cache", False)

        if from_cache:
            logger.debug("Cached response %s from %s", response, url)

        if response.is_success:
            if debug or return_raw:
                get_response = (from_cache, response)
            else:
                get_response = (from_cache, response.json())
        else:
            if none_on_404 and response.status_code == 404:
                get_response = (from_cache, None)
            elif self.raise_for_status:
                response.raise_for_status()  # raise httpx._exceptions.HTTPStatusError
        return get_response

    async def _post(self, url: str, params: dict, verbose: bool = True) -> Tuple[bool, httpx.Response]:
        """
        Wrapper around the httpx.post method
        """
        await self._build_http_client()

        if params is None:
            params = {}
        return_raw = params.pop("return_raw", False)
        headers = {"user-agent": self.default_user_agent}
        response = await self.http_client.post(
            url=url, data=params, headers=headers, extensions={"cache_disabled": not self.caching_enabled}
        )

        response_extensions = response.extensions
        from_cache = response_extensions.get("from_cache", False)

        if from_cache:
            logger.debug("Cached response %s from %s", response, url)

        if response.is_success:
            if return_raw:
                post_response = (from_cache, response)
            else:
                response.read()
                post_response = (from_cache, response.json())
        else:
            if self.raise_for_status:
                response.raise_for_status()
            else:
                post_response = (from_cache, response)
        return post_response

    async def _handle_common_kwargs(self, kwargs):
        # handle these common parameters accept field names as the value
        for kw in ["fields", "always_list", "allow_null"]:
            if kw in kwargs:
                kwargs[kw] = concatenate_list(kwargs[kw], quoted=False)
        return kwargs

    async def _repeated_query(self, query_fn, query_li, verbose=True, **fn_kwargs):
        """
        Run query_fn for input query_li in a batch (self.step).
        return a generator of query_result in each batch.
        input query_li can be a list/tuple/iterable
        """
        step = min(self.step, self.max_query)
        i = 0
        for batch, cnt in iter_n(query_li, step, with_cnt=True):
            if verbose:
                logger.info("querying {0}-{1}...".format(i + 1, cnt))
            i = cnt
            _, query_result = await query_fn(batch, **fn_kwargs)
            yield query_result

    async def _metadata(self, verbose=True, **kwargs):
        """
        Return a dictionary of Biothing metadata.
        """
        _url = self.url + self._metadata_endpoint
        _, ret = await self._get(_url, params=kwargs, verbose=verbose)
        return ret

    async def _set_caching(self, cache_db: Union[str, Path] = None, **kwargs) -> None:
        """
        Enable the client caching and creates a local cache database
        for all future requests

        If caching is already enabled then we no-opt

        Inputs:
        :param cache_db: pathlike object to the local sqlite3 cache database file

        Outputs:
        :return: None
        """
        if _CACHING_NOT_SUPPORTED:
            raise CachingNotSupportedError("Caching is only supported for Python 3.8+")

        if _CACHING:
            if not self.caching_enabled:
                try:
                    self.caching_enabled = True
                    self.http_client_setup = False
                    await self._build_cache_http_client()
                    logger.debug("Reset the HTTP client to leverage caching %s", self.http_client)
                    logger.info(
                        (
                            "Enabled client caching: %s\n" 'Future queries will be cached in "%s"',
                            self,
                            self.cache_storage.cache_filepath,
                        )
                    )
                except Exception as gen_exc:
                    logger.exception(gen_exc)
                    logger.error("Unable to enable caching")
                    raise gen_exc
            else:
                logger.warning("Caching already enabled. Skipping for now ...")
        else:
            caching_library_error = OptionalDependencyImportError(
                optional_function_access="enable biothings-client caching",
                optional_group="caching",
                libraries=["anysqlite", "hishel"],
            )
            raise caching_library_error

    async def _stop_caching(self) -> None:
        """
        Disable client caching. The local cache database will be maintained,
        but we will disable cache access when sending requests

        If caching is already disabled then we no-opt

        Inputs:
        :param None

        Outputs:
        :return: None
        """
        if _CACHING_NOT_SUPPORTED:
            raise CachingNotSupportedError("Caching is only supported for Python 3.8+")

        if _CACHING:
            if self.caching_enabled:
                try:
                    await self.cache_storage.clear_cache()
                except Exception as gen_exc:
                    logger.exception(gen_exc)
                    logger.error("Error attempting to clear the local cache database")
                    raise gen_exc

                self.caching_enabled = False
                self.http_client_setup = False
                self._build_http_client()
                logger.debug("Reset the HTTP client to disable caching %s", self.http_client)
                logger.info("Disabled client caching: %s", self)
            else:
                logger.warning("Caching already disabled. Skipping for now ...")
        else:
            caching_library_error = OptionalDependencyImportError(
                optional_function_access="disable biothings-client caching",
                optional_group="caching",
                libraries=["anysqlite", "hishel"],
            )
            raise caching_library_error

    async def _clear_cache(self) -> None:
        """
        Clear the globally installed cache. Caching will stil be enabled,
        but the data stored in the cache stored will be dropped
        """
        if _CACHING_NOT_SUPPORTED:
            raise CachingNotSupportedError("Caching is only supported for Python 3.8+")

        if _CACHING:
            if self.caching_enabled:
                try:
                    await self.cache_storage.clear_cache()
                except Exception as gen_exc:
                    logger.exception(gen_exc)
                    logger.error("Error attempting to clear the local cache database")
                    raise gen_exc
            else:
                logger.warning("Caching already disabled. No local cache database to clear. Skipping for now ...")
        else:
            caching_library_error = OptionalDependencyImportError(
                optional_function_access="clear biothings-client cache",
                optional_group="caching",
                libraries=["anysqlite", "hishel"],
            )
            raise caching_library_error

    async def _get_fields(self, search_term=None, verbose=True):
        """
        Wrapper for /metadata/fields

        **search_term** is a case insensitive string to search for in available field names.
        If not provided, all available fields will be returned.

        .. Hint:: This is useful to find out the field names you need to pass to **fields** parameter of other methods.

        """
        _url = self.url + self._metadata_fields_endpoint
        if search_term:
            params = {"search": search_term}
        else:
            params = {}
        _, ret = await self._get(_url, params=params, verbose=verbose)
        for k, v in ret.items():
            del k
            # Get rid of the notes column information
            if "notes" in v:
                del v["notes"]
        return ret

    async def _getannotation(self, _id, fields=None, **kwargs):
        """
        Return the object given id.
        This is a wrapper for GET query of the biothings annotation service.

        :param _id: an entity id.
        :param fields: fields to return, a list or a comma-separated string.
                       If not provided or **fields="all"**, all available fields
                       are returned.

        :return: an entity object as a dictionary, or None if _id is not found.
        """
        verbose = kwargs.pop("verbose", True)
        if fields:
            kwargs["fields"] = fields
        kwargs = await self._handle_common_kwargs(kwargs)
        _url = self.url + self._annotation_endpoint + str(_id)
        _, ret = await self._get(_url, kwargs, none_on_404=True, verbose=verbose)
        return ret

    async def _getannotations_inner(self, ids, verbose=True, **kwargs):
        id_collection = concatenate_list(ids)
        _kwargs = {"ids": id_collection}
        _kwargs.update(kwargs)
        _url = self.url + self._annotation_endpoint
        return await self._post(_url, _kwargs, verbose=verbose)

    async def _annotations_generator(self, query_fn, ids, verbose=True, **kwargs):
        """
        Function to yield a batch of hits one at a time.
        """
        for hits in self._repeated_query(query_fn, ids, verbose=verbose):
            for hit in hits:
                yield hit

    async def _getannotations(self, ids, fields=None, **kwargs):
        """
        Return the list of annotation objects for the given list of ids.
        This is a wrapper for POST query of the biothings annotation service.

        :param ids: a list/tuple/iterable or a string of ids.
        :param fields: fields to return, a list or a comma-separated string.
                       If not provided or **fields="all"**, all available fields
                       are returned.
        :param as_generator: if True, will yield the results in a generator.
        :param as_dataframe: if True or 1 or 2, return object as DataFrame (requires Pandas).
                                  True or 1: using json_normalize
                                  2        : using DataFrame.from_dict
                                  otherwise: return original json
        :param df_index: if True (default), index returned DataFrame by 'query',
                         otherwise, index by number. Only applicable if as_dataframe=True.

        :return: a list of objects or a pandas DataFrame object (when **as_dataframe** is True)

        .. Hint:: A large list of more than 1000 input ids will be sent to the backend
                  web service in batches (1000 at a time), and then the results will be
                  concatenated together. So, from the user-end, it's exactly the same as
                  passing a shorter list. You don't need to worry about saturating our
                  backend servers.

        .. Hint:: If you need to pass a very large list of input ids, you can pass a generator
                  instead of a full list, which is more memory efficient.
        """
        if isinstance(ids, str):
            ids = ids.split(",") if ids else []
        if not (isinstance(ids, (list, tuple, Iterable))):
            raise ValueError('input "ids" must be a list, tuple or iterable.')
        if fields:
            kwargs["fields"] = fields
        kwargs = await self._handle_common_kwargs(kwargs)
        verbose = kwargs.pop("verbose", True)
        dataframe = kwargs.pop("as_dataframe", None)
        df_index = kwargs.pop("df_index", True)
        generator = kwargs.pop("as_generator", False)
        if dataframe in [True, 1]:
            dataframe = 1
        elif dataframe != 2:
            dataframe = None
        return_raw = kwargs.get("return_raw", False)
        if return_raw:
            dataframe = None

        async def query_fn(ids):
            return await self._getannotations_inner(ids, verbose=verbose, **kwargs)

        if generator:
            return self._annotations_generator(query_fn, ids, verbose=verbose, **kwargs)
        out = []
        async for hits in self._repeated_query(query_fn, ids, verbose=verbose):
            if return_raw:
                out.append(hits)  # hits is the raw response text
            else:
                out.extend(hits)
        if return_raw and len(out) == 1:
            out = out[0]
        if dataframe:
            out = await self._dataframe(out, dataframe, df_index=df_index)
        return out

    async def _query(self, q: str, **kwargs):
        """
        Return the query result.
        This is a wrapper for GET query of biothings query service.

        :param q: a query string.
        :param fields: fields to return, a list or a comma-separated string.
                       If not provided or **fields="all"**, all available fields
                       are returned.
        :param size:   the maximum number of results to return (with a cap
                       of 1000 at the moment). Default: 10.
        :param skip:   the number of results to skip. Default: 0.
        :param sort:   Prefix with "-" for descending order, otherwise in ascending order.
                       Default: sort by matching scores in decending order.
        :param as_dataframe: if True or 1 or 2, return object as DataFrame (requires Pandas).
                                  True or 1: using json_normalize
                                  2        : using DataFrame.from_dict
                                  otherwise: return original json
        :param fetch_all: if True, return a generator to all query results (unsorted).  This can provide a very fast
                          return of all hits from a large query.
                          Server requests are done in blocks of 1000 and yielded individually.  Each 1000 block of
                          results must be yielded within 1 minute, otherwise the request will expire at server side.

        :return: a dictionary with returned variant hits or a pandas DataFrame object (when **as_dataframe** is True)
                 or a generator of all hits (when **fetch_all** is True)

        .. Hint:: By default, **query** method returns the first 10 hits if the matched hits are >10.
                  If the total number of hits are less than 1000, you can increase the value for
                  **size** parameter. For a query that returns more than 1000 hits, you can pass
                  "fetch_all=True" to return a `generator <http://www.learnpython.org/en/Generators>`_
                  of all matching hits (internally, those hits are requested from the server in blocks of 1000).
        """
        _url = self.url + self._query_endpoint
        verbose = kwargs.pop("verbose", True)
        kwargs = await self._handle_common_kwargs(kwargs)
        kwargs.update({"q": q})
        fetch_all = kwargs.get("fetch_all")
        if fetch_all in [True, 1]:
            if kwargs.get("as_dataframe", None) in [True, 1]:
                warnings.warn(
                    "Ignored 'as_dataframe' because 'fetch_all' is specified. "
                    "Too many documents to return as a Dataframe."
                )
            return self._fetch_all(url=_url, verbose=verbose, **kwargs)
        dataframe = kwargs.pop("as_dataframe", None)
        if dataframe in [True, 1]:
            dataframe = 1
        elif dataframe != 2:
            dataframe = None
        _, out = await self._get(_url, kwargs, verbose=verbose)
        if dataframe:
            out = await self._dataframe(out, dataframe, df_index=False)
        return out

    async def _fetch_all(self, url: str, verbose: bool = True, **kwargs):
        """
        Function that returns a generator to results. Assumes that 'q' is in kwargs.
        Implicitly disables caching to ensure we actually hit the endpoint rather than
        pulling from local cache
        """
        logger.warning("fetch_all implicitly disables HTTP request caching")
        restore_caching = False
        if self.caching_enabled:
            restore_caching = True
            try:
                await self.stop_caching()
            except OptionalDependencyImportError as optional_import_error:
                logger.exception(optional_import_error)
                logger.debug("No cache to disable for fetch all. Continuing ...")
            except Exception as gen_exc:
                logger.exception(gen_exc)
                logger.error("Unknown error occured while attempting to disable caching")
                raise gen_exc

        _, batch = await self._get(url, params=kwargs, verbose=verbose)
        if verbose:
            logger.info("Fetching {0} {1} . . .".format(batch["total"], self._optionally_plural_object_type))
        for key in ["q", "fetch_all"]:
            kwargs.pop(key)
        while not batch.get("error", "").startswith("No results to return"):
            if "error" in batch:
                logger.error(batch["error"])
                break
            if "_warning" in batch and verbose:
                logger.warning(batch["_warning"])
            for hit in batch["hits"]:
                yield hit
            kwargs.update({"scroll_id": batch["_scroll_id"]})
            _, batch = await self._get(url, params=kwargs, verbose=verbose)

        if restore_caching:
            logger.debug("re-enabling the client HTTP caching")
            try:
                await self.set_caching()
            except OptionalDependencyImportError as optional_import_error:
                logger.exception(optional_import_error)
                logger.debug("No cache to disable for fetch all. Continuing ...")
            except Exception as gen_exc:
                logger.exception(gen_exc)
                logger.error("Unknown error occured while attempting to disable caching")
                raise gen_exc

    async def _querymany_inner(self, qterms, verbose=True, **kwargs):
        query_term_collection = concatenate_list(qterms)
        _kwargs = {"q": query_term_collection}
        _kwargs.update(kwargs)
        _url = self.url + self._query_endpoint
        return await self._post(_url, params=_kwargs, verbose=verbose)

    async def _querymany(self, qterms, scopes=None, **kwargs):
        """
        Return the batch query result.
        This is a wrapper for POST query of "/query" service.

        :param qterms: a list/tuple/iterable of query terms, or a string of comma-separated query terms.
        :param scopes: specify the type (or types) of identifiers passed to **qterms**,
                       either a list or a comma-separated fields to specify type of input qterms.
        :param fields: fields to return, a list or a comma-separated string.
                       If not provided or **fields="all"**, all available fields
                       are returned.
        :param returnall:   if True, return a dict of all related data, including dup. and missing qterms
        :param verbose:     if True (default), print out information about dup and missing qterms
        :param as_dataframe: if True or 1 or 2, return object as DataFrame (requires Pandas).
                                  True or 1: using json_normalize
                                  2        : using DataFrame.from_dict
                                  otherwise: return original json
        :param df_index: if True (default), index returned DataFrame by 'query',
                         otherwise, index by number. Only applicable if as_dataframe=True.
        :return: a list of matching objects or a pandas DataFrame object.

        .. Hint:: Passing a large list of ids (>1000) to :py:meth:`querymany` is perfectly fine.

        .. Hint:: If you need to pass a very large list of input qterms, you can pass a generator
                  instead of a full list, which is more memory efficient.

        """
        if isinstance(qterms, str):
            qterms = qterms.split(",") if qterms else []
        if not (isinstance(qterms, (list, tuple, Iterable))):
            raise ValueError('input "qterms" must be a list, tuple or iterable.')

        if scopes:
            kwargs["scopes"] = concatenate_list(scopes, quoted=False)
        kwargs = await self._handle_common_kwargs(kwargs)
        returnall = kwargs.pop("returnall", False)
        verbose = kwargs.pop("verbose", True)
        dataframe = kwargs.pop("as_dataframe", None)
        if dataframe in [True, 1]:
            dataframe = 1
        elif dataframe != 2:
            dataframe = None
        df_index = kwargs.pop("df_index", True)
        return_raw = kwargs.get("return_raw", False)
        if return_raw:
            dataframe = None

        out = []
        li_missing = []
        li_dup = []
        li_query = []

        async def query_fn(qterms):
            return await self._querymany_inner(qterms, verbose=verbose, **kwargs)

        async for hits in self._repeated_query(query_fn, qterms, verbose=verbose):
            if return_raw:
                out.append(hits)  # hits is the raw response text
            else:
                out.extend(hits)
                for hit in hits:
                    if hit.get("notfound", False):
                        li_missing.append(hit["query"])
                    else:
                        li_query.append(hit["query"])

        if verbose:
            logger.info("Finished.")
        if return_raw:
            if len(out) == 1:
                out = out[0]
            return out

        # check dup hits
        if li_query:
            li_dup = [(query, cnt) for query, cnt in list_itemcnt(li_query) if cnt > 1]
            del li_query

        if dataframe:
            out = await self._dataframe(out, dataframe, df_index=df_index)
            li_dup_df = pandas.DataFrame.from_records(li_dup, columns=["query", "duplicate hits"])
            li_missing_df = pandas.DataFrame(li_missing, columns=["query"])

        if verbose:
            if li_dup:
                logger.warning("{0} input query terms found dup hits:".format(len(li_dup)) + "\t" + str(li_dup)[:100])
            if li_missing:
                logger.warning(
                    "{0} input query terms found no hit:".format(len(li_missing)) + "\t" + str(li_missing)[:100]
                )

        if returnall:
            if dataframe:
                return {"out": out, "dup": li_dup_df, "missing": li_missing_df}
            else:
                return {"out": out, "dup": li_dup, "missing": li_missing}
        else:
            if verbose and (li_dup or li_missing):
                logger.info('Pass "returnall=True" to return complete lists of duplicate or missing query terms.')
            return out


def get_async_client(biothing_type: str = None, instance: bool = True, *args, **kwargs):
    """
    Function to return a new python asynchronous client for a Biothings API service.

    :param biothing_type: the type of biothing client, currently one of: 'gene', 'variant', 'taxon', 'chem', 'disease', 'geneset'
    :param instance: if True, return an instance of the derived client,
                     if False, return the class of the derived client

    All other args/kwargs are passed to the derived client instantiation (if applicable)
    """
    if not biothing_type:
        url = kwargs.get("url", False)
        if not url:
            raise RuntimeError("No biothings_type or url specified.")
        try:
            url += "metadata" if url.endswith("/") else "/metadata"
            res = httpx.get(url)
            dic = res.json()
            biothing_type = dic.get("biothing_type")
            if isinstance(biothing_type, list):
                if len(biothing_type) == 1:
                    # if a list with only one item, use that item
                    biothing_type = biothing_type[0]
                else:
                    raise RuntimeError("Biothing_type in metadata url is not unique.")
            if not isinstance(biothing_type, str):
                raise RuntimeError("Biothing_type in metadata url is not a valid string.")
        except httpx.RequestError as request_error:
            raise RuntimeError("Cannot access metadata url to determine biothing_type.") from request_error
    else:
        biothing_type = biothing_type.lower()
    if biothing_type not in ASYNC_CLIENT_SETTINGS and not kwargs.get("url", False):
        raise TypeError(
            f"No client named '{biothing_type}', currently available clients are: {list(ASYNC_CLIENT_SETTINGS.keys())}"
        )
    _settings = (
        ASYNC_CLIENT_SETTINGS[biothing_type]
        if biothing_type in ASYNC_CLIENT_SETTINGS
        else generate_async_settings(biothing_type, kwargs.get("url"))
    )
    _class = type(
        _settings["class_name"], tuple([_settings["base_class"]] + _settings["mixins"]), _settings["class_kwargs"]
    )
    for src_attr, target_attr in _settings["attr_aliases"].items():
        if getattr(_class, src_attr, False):
            setattr(_class, target_attr, copy_func(getattr(_class, src_attr), name=target_attr))
    for _name, _docstring in _settings["class_kwargs"]["_docstring_obj"].items():
        _func = getattr(_class, _name, None)
        if _func:
            try:
                _func.__doc__ = _docstring
            except AttributeError:
                _func.__func__.__doc__ = _docstring
    _client = _class(*args, **kwargs) if instance else _class
    return _client


# ***********************************************
# *  Client settings
# *
# *  This object contains the client-specific settings necessary to
# *  instantiate a new biothings client.  The currently supported
# *  clients are the keys of this object.
# *
# *  class - the client Class name
# *  class_kwargs - keyword arguments passed to Class on creation
# *  function_aliases - client specific function aliases in Class
# *  ancestors - a list of classes that Class inherits from
# ***********************************************
ASYNC_CLIENT_SETTINGS = {
    "gene": {
        "class_name": "AsyncMyGeneInfo",
        "class_kwargs": MYGENE_KWARGS,
        "attr_aliases": MYGENE_ALIASES,
        "base_class": AsyncBiothingClient,
        "mixins": [MyGeneClientMixin],
    },
    "variant": {
        "class_name": "AsyncMyVariantInfo",
        "class_kwargs": MYVARIANT_KWARGS,
        "attr_aliases": MYVARIANT_ALIASES,
        "base_class": AsyncBiothingClient,
        "mixins": [MyVariantClientMixin],
    },
    "taxon": {
        "class_name": "AsyncMyTaxonInfo",
        "class_kwargs": MYTAXON_KWARGS,
        "attr_aliases": MYTAXON_ALIASES,
        "base_class": AsyncBiothingClient,
        "mixins": [],
    },
    "drug": {
        "class_name": "AsyncMyChemInfo",
        "class_kwargs": MYCHEM_KWARGS,
        "attr_aliases": MYCHEM_ALIASES,
        "base_class": AsyncBiothingClient,
        "mixins": [],
    },
    "chem": {
        "class_name": "AsyncMyChemInfo",
        "class_kwargs": MYCHEM_KWARGS,
        "attr_aliases": MYCHEM_ALIASES,
        "base_class": AsyncBiothingClient,
        "mixins": [],
    },
    "compound": {
        "class_name": "AsyncMyChemInfo",
        "class_kwargs": MYCHEM_KWARGS,
        "attr_aliases": MYCHEM_ALIASES,
        "base_class": AsyncBiothingClient,
        "mixins": [],
    },
    "disease": {
        "class_name": "AsyncMyDiseaseInfo",
        "class_kwargs": MYDISEASE_KWARGS,
        "attr_aliases": MYDISEASE_ALIASES,
        "base_class": AsyncBiothingClient,
        "mixins": [],
    },
    "geneset": {
        "class_name": "AsyncMyGenesetInfo",
        "class_kwargs": MYGENESET_KWARGS,
        "attr_aliases": MYGENESET_ALIASES,
        "base_class": AsyncBiothingClient,
        "mixins": [],
    },
}


def generate_async_settings(biothing_type: str, url: str) -> Dict:
    """
    Tries to generate a settings dictionary for a client that isn't explicitly listed in
    {CLIENT_SETTTINGS, ASYNC_CLIENT_SETTINGS}

    :param biothing_type: The biothing type to target when generating settings
    :param url: The web url specified in the settings via `default_url`

    :return: Returns a dictionary mapping of the client settings
    :rtype: dict
    """

    def _pluralize(s, optional=True):
        _append = "({})" if optional else "{}"
        return s + _append.format("es") if s.endswith("s") else s + _append.format("s")

    _kwargs = copy(COMMON_KWARGS)
    _aliases = copy(COMMON_ALIASES)
    _kwargs.update(
        {
            "_default_url": url,
            "_annotation_endpoint": "/" + biothing_type.lower() + "/",
            "_optionally_plural_object_type": _pluralize(biothing_type.lower()),
            "_default_cache_file": "my" + biothing_type.lower() + "_cache",
        }
    )
    _aliases.update(
        {
            "_getannotation": "get" + biothing_type.lower(),
            "_getannotations": "get" + _pluralize(biothing_type.lower(), optional=False),
        }
    )
    return {
        "class_name": "Async" + "My" + biothing_type.title() + "Info",
        "class_kwargs": _kwargs,
        "mixins": [],
        "attr_aliases": _aliases,
        "base_class": AsyncBiothingClient,
    }
