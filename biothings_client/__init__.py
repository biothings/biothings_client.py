"""
Generic client for Biothings APIs
"""

import types
from copy import copy

import httpx
import requests

from biothings_client.client.async import AsyncBiothingClient
from biothings_client.client.base import BiothingClient
from biothings_client.docstring.chem import DOCSTRING as CHEM_DOCSTRING
from biothings_client.docstring.gene import DOCSTRING as GENE_DOCSTRING
from biothings_client.docstring.variant import DOCSTRING as VARIANT_DOCSTRING
from biothings_client.mixins.gene import MyGeneClientMixin
from biothings_client.mixins.variant import MyVariantClientMixin
from biothings_client.utils.variant import MYVARIANT_TOP_LEVEL_JSONLD_URIS


__version__ = "0.3.1"



def copy_func(f, name=None):
    """
    return a function with same code, globals, defaults, closure, and
    name (or provide a new name)
    """
    fn = types.FunctionType(f.__code__, f.__globals__, name or f.__name__, f.__defaults__, f.__closure__)
    # in case f was given attrs (note this dict is a shallow copy):
    fn.__dict__.update(f.__dict__)
    return fn






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
