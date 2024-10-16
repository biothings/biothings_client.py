"""
Async Python Client for generic Biothings API services
"""

from collections.abc import Iterable
from copy import copy
import asyncio
import logging
import os
import platform
import time
import warnings

import httpx


try:
    from pandas import DataFrame, json_normalize

    df_avail = True
except ImportError:
    df_avail = False

from biothings_client.utils.iteration import (
    iter_n,
    list_itemcnt,
    safe_str,
)
from biothings_client.utils.copy import copy_func

from biothings_client.__version__ import __version__
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
from biothings_client.mixins.gene import MyGeneClientMixin
from biothings_client.mixins.variant import MyVariantClientMixin


logger = logging.getLogger("biothings.client")
logger.setLevel(logging.INFO)


# Future work:
# Consider use "verbose" settings to control default logging output level
# by doing this instead of using branching throughout the application,
# the business logic can be more concise and more readable.
class AsyncBiothingClient:
    """
    This is the asynchronous client for a biothing web service.
    """

    def __init__(self, url: str = None, enable_cache: bool = None):
        if url is None:
            url = self._default_url
        self.url = url
        if self.url[-1] == "/":
            self.url = self.url[:-1]

        if enable_cache is None:
            enable_cache = False
        self.enable_cache = enable_cache

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

    async def use_http(self):
        """
        Use http instead of https for API calls.
        """
        if self.url:
            self.url = self.url.replace("https://", "http://")

    async def use_https(self):
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
        if not df_avail:
            raise RuntimeError("Error: pandas module must be installed " "(or upgraded) for as_dataframe option.")
        # if dataframe not in ["by_source", "normal"]:
        if dataframe not in [1, 2]:
            raise ValueError("dataframe must be either 1 (using json_normalize) " "or 2 (using DataFrame.from_dict")
        if "hits" in obj:
            if dataframe == 1:
                df = json_normalize(obj["hits"])
            else:
                df = DataFrame.from_dict(obj)
        else:
            if dataframe == 1:
                df = json_normalize(obj)
            else:
                df = DataFrame.from_dict(obj)
        if df_index:
            df = df.set_index("query")
        return df

    async def _get(
        self, url: str, params: dict = None, none_on_404: bool = False, verbose: bool = True
    ) -> tuple[bool, httpx.Response]:
        """
        Wrapper around the httpx.get method
        """
        if params is None:
            params = {}
        debug = params.pop("debug", False)
        return_raw = params.pop("return_raw", False)

        headers = {"user-agent": self.default_user_agent}
        async with httpx.AsyncClient() as client:
            res = await client.get(url, params=params, headers=headers)
        from_cache = getattr(res, "from_cache", False)

        if debug:
            return from_cache, res
        if none_on_404 and res.status_code == 404:
            return from_cache, None
        if self.raise_for_status:
            res.raise_for_status()  # raise httpx._exceptions.HTTPStatusError
        if return_raw:
            return from_cache, res.text
        ret = res.json()
        return from_cache, ret

    async def _post(self, url: str, params: dict, verbose: bool = True):
        """
        Wrapper around the httpx.post method
        """
        return_raw = params.pop("return_raw", False)
        headers = {"user-agent": self.default_user_agent}
        async with httpx.AsyncClient() as client:
            res = await client.post(url, data=params, headers=headers)
        from_cache = getattr(res, "from_cache", False)
        if self.raise_for_status:
            res.raise_for_status()  # raise httpx._exceptions.HTTPStatusError
        if return_raw:
            return from_cache, res
        ret = res.json()
        return from_cache, ret

    @staticmethod
    async def _format_list(a_list, sep=",", quoted=True):
        if isinstance(a_list, (list, tuple)):
            if quoted:
                _out = sep.join(['"{}"'.format(safe_str(x)) for x in a_list])
            else:
                _out = sep.join(["{}".format(safe_str(x)) for x in a_list])
        else:
            _out = a_list  # a_list is already a comma separated string
        return _out

    async def _handle_common_kwargs(self, kwargs):
        # handle these common parameters accept field names as the value
        for kw in ["fields", "always_list", "allow_null"]:
            if kw in kwargs:
                kwargs[kw] = await self._format_list(kwargs[kw], quoted=False)
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
            from_cache, query_result = await query_fn(batch, **fn_kwargs)
            yield query_result
            if verbose:
                cache_str = " {0}".format(self._from_cache_notification) if from_cache else ""
                logger.info("done.{0}".format(cache_str))
            if not from_cache and self.delay:
                # no need to delay if requests are from cache.
                await asyncio.sleep(self.delay)

    @property
    async def _from_cache_notification(self):
        """
        Notification to alert user that a cached result is being returned.
        """
        return "[ from cache ]"

    async def _metadata(self, verbose=True, **kwargs):
        """
        Return a dictionary of Biothing metadata.
        """
        _url = self.url + self._metadata_endpoint
        from_cache, ret = await self._get(_url, params=kwargs, verbose=verbose)
        if verbose and from_cache:
            logger.info(self._from_cache_notification)
        return ret

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
        from_cache, ret = await self._get(_url, params=params, verbose=verbose)
        for k, v in ret.items():
            del k
            # Get rid of the notes column information
            if "notes" in v:
                del v["notes"]
        if verbose and from_cache:
            logger.info(self._from_cache_notification)
        return ret

    async def _getannotation(self, _id, fields=None, **kwargs):
        """Return the object given id.
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
        from_cache, ret = await self._get(_url, kwargs, none_on_404=True, verbose=verbose)
        if verbose and from_cache:
            logger.info(self._from_cache_notification)
        return ret

    async def _getannotations_inner(self, ids, verbose=True, **kwargs):
        id_collection = await self._format_list(ids)
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
        """Return the list of annotation objects for the given list of ids.
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
        from_cache, out = await self._get(_url, kwargs, verbose=verbose)
        if verbose and from_cache:
            logger.info(self._from_cache_notification)
        if dataframe:
            out = await self._dataframe(out, dataframe, df_index=False)
        return out

    async def _fetch_all(self, url: str, verbose: bool = True, **kwargs):
        """
        Function that returns a generator to results. Assumes that 'q' is in kwargs.
        """
        from_cache, batch = await self._get(url, params=kwargs, verbose=verbose)
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
            from_cache, batch = await self._get(url, params=kwargs, verbose=verbose)

    async def _querymany_inner(self, qterms, verbose=True, **kwargs):
        query_term_collection = await self._format_list(qterms)
        _kwargs = {"q": query_term_collection}
        _kwargs.update(kwargs)
        _url = self.url + self._query_endpoint
        return await self._post(_url, params=_kwargs, verbose=verbose)

    async def _querymany(self, qterms, scopes=None, **kwargs):
        """Return the batch query result.
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
            kwargs["scopes"] = await self._format_list(scopes, quoted=False)
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
            li_dup_df = DataFrame.from_records(li_dup, columns=["query", "duplicate hits"])
            li_missing_df = DataFrame(li_missing, columns=["query"])

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
        raise Exception(
            "No client named '{0}', currently available clients are: {1}".format(
                biothing_type, list(ASYNC_CLIENT_SETTINGS.keys())
            )
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


def generate_async_settings(biothing_type: str, url: str):
    """
    Tries to generate a settings dictionary for a client that isn't explicitly listed in
    {
        CLIENT_SETTINGS,
        ASYNC_CLIENT_SETTINGS
    }
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
