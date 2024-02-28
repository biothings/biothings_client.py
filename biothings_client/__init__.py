"""
Generic client for Biothings APIs
"""

import types
from copy import copy

import requests

from .base import BiothingClient, str_types, __version__, df_avail, caching_avail
from .settings import CLIENT_SETTINGS, COMMON_KWARGS, COMMON_ALIASES


def copy_func(f, name=None):
    """
    return a function with same code, globals, defaults, closure, and
    name (or provide a new name)
    """
    fn = types.FunctionType(f.__code__, f.__globals__, name or f.__name__, f.__defaults__, f.__closure__)
    # in case f was given attrs (note this dict is a shallow copy):
    fn.__dict__.update(f.__dict__)
    return fn


def _generate_settings(biothing_type, url):
    """Tries to generate a settings dictionary for a client that isn't explicitly listed in CLIENT_SETTINGS."""

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
        "class_name": "My" + biothing_type.title() + "Info",
        "class_kwargs": _kwargs,
        "mixins": [],
        "attr_aliases": _aliases,
        "base_class": BiothingClient,
    }


def get_client(biothing_type=None, instance=True, *args, **kwargs):
    """Function to return a new python client for a Biothings API service.

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
            res = requests.get(url)
            dic = res.json()
            biothing_type = dic.get("biothing_type")
            if isinstance(biothing_type, list):
                if len(biothing_type) == 1:
                    # if a list with only one item, use that item
                    biothing_type = biothing_type[0]
                else:
                    raise RuntimeError("Biothing_type in metadata url is not unique.")
            if not isinstance(biothing_type, str_types):
                raise RuntimeError("Biothing_type in metadata url is not a valid string.")
        except requests.RequestException:
            raise RuntimeError("Cannot access metadata url to determine biothing_type.")
    else:
        biothing_type = biothing_type.lower()
    if biothing_type not in CLIENT_SETTINGS and not kwargs.get("url", False):
        raise Exception(
            "No client named '{0}', currently available clients are: {1}".format(
                biothing_type, list(CLIENT_SETTINGS.keys())
            )
        )
    _settings = (
        CLIENT_SETTINGS[biothing_type]
        if biothing_type in CLIENT_SETTINGS
        else _generate_settings(biothing_type, kwargs.get("url"))
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


class MyGeneInfo(get_client("gene", instance=False)):
    pass


class MyVariantInfo(get_client("variant", instance=False)):
    pass


class MyChemInfo(get_client("chem", instance=False)):
    pass


class MyDiseaseInfo(get_client("disease", instance=False)):
    pass


class MyTaxonInfo(get_client("taxon", instance=False)):
    pass


class MyGenesetInfo(get_client("geneset", instance=False)):
    pass
