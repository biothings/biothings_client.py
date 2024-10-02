"""
Settings and configuration values for the different biothings-clients
"""

from copy import copy

from biothings_client.client import AsyncBiothingClient, BiothingClient
from biothings_client.docstring.chem import DOCSTRING as CHEM_DOCSTRING
from biothings_client.docstring.gene import DOCSTRING as GENE_DOCSTRING
from biothings_client.docstring.variant import DOCSTRING as VARIANT_DOCSTRING
from biothings_client.mixins.gene import MyGeneClientMixin
from biothings_client.mixins.variant import MyVariantClientMixin
from biothings_client.utils.variant import MYVARIANT_TOP_LEVEL_JSONLD_URIS

# ***********************************************
# *  Aliases.
# *
# *  (key, value) pairs where the function named "key" in utils.BiothingClient
# *  is aliased as "value" in the returned client class.
# ***********************************************
# Function aliases common to all clients
COMMON_ALIASES = {
    "_metadata": "metadata",
    "_set_caching": "set_caching",
    "_stop_caching": "stop_caching",
    "_clear_cache": "clear_cache",
    "_get_fields": "get_fields",
    "_query": "query",
    "_querymany": "querymany",
}

# Set project specific aliases
MYGENE_ALIASES = copy(COMMON_ALIASES)
MYGENE_ALIASES.update({"_getannotation": "getgene", "_getannotations": "getgenes"})
MYVARIANT_ALIASES = copy(COMMON_ALIASES)
MYVARIANT_ALIASES.update({"_getannotation": "getvariant", "_getannotations": "getvariants"})
MYCHEM_ALIASES = copy(COMMON_ALIASES)
MYCHEM_ALIASES.update({"_getannotation": "getchem", "_getannotations": "getchems"})
MYCHEM_ALIASES.update({"getchem": "getdrug", "getchems": "getdrugs"})
MYTAXON_ALIASES = copy(COMMON_ALIASES)
MYTAXON_ALIASES.update({"_getannotation": "gettaxon", "_getannotations": "gettaxa"})
MYDISEASE_ALIASES = copy(COMMON_ALIASES)
MYDISEASE_ALIASES.update({"_getannotation": "getdisease", "_getannotations": "getdiseases"})
MYGENESET_ALIASES = copy(COMMON_ALIASES)
MYGENESET_ALIASES.update({"_getannotation": "getgeneset", "_getannotations": "getgenesets"})

# ***********************************************
# *  Kwargs.
# *
# *  These keyword arguments are attached to the returned client class
# *  on class creation.
# ***********************************************

# Object creation kwargs common to all clients
COMMON_KWARGS = {
    "_pkg_user_agent_header": "biothings_client.py",
    "_query_endpoint": "/query/",
    "_metadata_endpoint": "/metadata",
    "_metadata_fields_endpoint": "/metadata/fields",
    "_top_level_jsonld_uris": [],
    "_docstring_obj": {},
    "_delay": 1,
    "_step": 1000,
    "_scroll_size": 1000,
    "_max_query": 1000,
}
# project specific kwargs
MYGENE_KWARGS = copy(COMMON_KWARGS)
MYGENE_KWARGS.update(
    {
        "_default_url": "https://mygene.info/v3",
        "_annotation_endpoint": "/gene/",
        "_optionally_plural_object_type": "gene(s)",
        "_default_cache_file": "mygene_cache",
        "_entity": "gene",
        "_docstring_obj": GENE_DOCSTRING,
    }
)
MYVARIANT_KWARGS = copy(COMMON_KWARGS)
MYVARIANT_KWARGS.update(
    {
        "_default_url": "https://myvariant.info/v1",
        "_annotation_endpoint": "/variant/",
        "_optionally_plural_object_type": "variant(s)",
        "_default_cache_file": "myvariant_cache",
        "_entity": "variant",
        "_top_level_jsonld_uris": MYVARIANT_TOP_LEVEL_JSONLD_URIS,
        "_docstring_obj": VARIANT_DOCSTRING,
    }
)
MYCHEM_KWARGS = copy(COMMON_KWARGS)
MYCHEM_KWARGS.update(
    {
        "_default_url": "https://mychem.info/v1",
        "_annotation_endpoint": "/chem/",
        "_optionally_plural_object_type": "chem(s)",
        "_entity": "chem",
        "_default_cache_file": "mychem_cache",
        "_docstring_obj": CHEM_DOCSTRING,
    }
)
MYDISEASE_KWARGS = copy(COMMON_KWARGS)
MYDISEASE_KWARGS.update(
    {
        "_default_url": "https://mydisease.info/v1",
        "_annotation_endpoint": "/disease/",
        "_optionally_plural_object_type": "disease(s)",
        "_entity": "disease",
        "_default_cache_file": "mydisease_cache",
    }
)
MYTAXON_KWARGS = copy(COMMON_KWARGS)
MYTAXON_KWARGS.update(
    {
        "_default_url": "https://t.biothings.io/v1",
        "_annotation_endpoint": "/taxon/",
        "_optionally_plural_object_type": "taxon/taxa",
        "_entity": "taxon",
        "_default_cache_file": "mytaxon_cache",
    }
)
MYGENESET_KWARGS = copy(COMMON_KWARGS)
MYGENESET_KWARGS.update(
    {
        "_default_url": "https://mygeneset.info/v1",
        "_annotation_endpoint": "/geneset/",
        "_optionally_plural_object_type": "geneset(s)",
        "_entity": "geneset",
        "_default_cache_file": "mygeneset_cache",
    }
)

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

CLIENT_SETTINGS = {
    "gene": {
        "class_name": "MyGeneInfo",
        "class_kwargs": MYGENE_KWARGS,
        "attr_aliases": MYGENE_ALIASES,
        "base_class": BiothingClient,
        "mixins": [MyGeneClientMixin],
    },
    "variant": {
        "class_name": "MyVariantInfo",
        "class_kwargs": MYVARIANT_KWARGS,
        "attr_aliases": MYVARIANT_ALIASES,
        "base_class": BiothingClient,
        "mixins": [MyVariantClientMixin],
    },
    "taxon": {
        "class_name": "MyTaxonInfo",
        "class_kwargs": MYTAXON_KWARGS,
        "attr_aliases": MYTAXON_ALIASES,
        "base_class": BiothingClient,
        "mixins": [],
    },
    "drug": {
        "class_name": "MyChemInfo",
        "class_kwargs": MYCHEM_KWARGS,
        "attr_aliases": MYCHEM_ALIASES,
        "base_class": BiothingClient,
        "mixins": [],
    },
    "chem": {
        "class_name": "MyChemInfo",
        "class_kwargs": MYCHEM_KWARGS,
        "attr_aliases": MYCHEM_ALIASES,
        "base_class": BiothingClient,
        "mixins": [],
    },
    "compound": {
        "class_name": "MyChemInfo",
        "class_kwargs": MYCHEM_KWARGS,
        "attr_aliases": MYCHEM_ALIASES,
        "base_class": BiothingClient,
        "mixins": [],
    },
    "disease": {
        "class_name": "MyDiseaseInfo",
        "class_kwargs": MYDISEASE_KWARGS,
        "attr_aliases": MYDISEASE_ALIASES,
        "base_class": BiothingClient,
        "mixins": [],
    },
    "geneset": {
        "class_name": "MyGenesetInfo",
        "class_kwargs": MYGENESET_KWARGS,
        "attr_aliases": MYGENESET_ALIASES,
        "base_class": BiothingClient,
        "mixins": [],
    },
}

ASYNC_CLIENT_SETTINGS = {
    "gene": {
        "class_name": "MyGeneInfo",
        "class_kwargs": MYGENE_KWARGS,
        "attr_aliases": MYGENE_ALIASES,
        "base_class": AsyncBiothingClient,
        "mixins": [MyGeneClientMixin],
    },
    "variant": {
        "class_name": "MyVariantInfo",
        "class_kwargs": MYVARIANT_KWARGS,
        "attr_aliases": MYVARIANT_ALIASES,
        "base_class": AsyncBiothingClient,
        "mixins": [MyVariantClientMixin],
    },
    "taxon": {
        "class_name": "MyTaxonInfo",
        "class_kwargs": MYTAXON_KWARGS,
        "attr_aliases": MYTAXON_ALIASES,
        "base_class": AsyncBiothingClient,
        "mixins": [],
    },
    "drug": {
        "class_name": "MyChemInfo",
        "class_kwargs": MYCHEM_KWARGS,
        "attr_aliases": MYCHEM_ALIASES,
        "base_class": AsyncBiothingClient,
        "mixins": [],
    },
    "chem": {
        "class_name": "MyChemInfo",
        "class_kwargs": MYCHEM_KWARGS,
        "attr_aliases": MYCHEM_ALIASES,
        "base_class": AsyncBiothingClient,
        "mixins": [],
    },
    "compound": {
        "class_name": "MyChemInfo",
        "class_kwargs": MYCHEM_KWARGS,
        "attr_aliases": MYCHEM_ALIASES,
        "base_class": AsyncBiothingClient,
        "mixins": [],
    },
    "disease": {
        "class_name": "MyDiseaseInfo",
        "class_kwargs": MYDISEASE_KWARGS,
        "attr_aliases": MYDISEASE_ALIASES,
        "base_class": AsyncBiothingClient,
        "mixins": [],
    },
    "geneset": {
        "class_name": "MyGenesetInfo",
        "class_kwargs": MYGENESET_KWARGS,
        "attr_aliases": MYGENESET_ALIASES,
        "base_class": AsyncBiothingClient,
        "mixins": [],
    },
}

def generate_settings(biothing_type, url):
    """
    Tries to generate a settings dictionary for a client that isn't explicitly listed in CLIENT_SETTINGS.
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
        "class_name": "My" + biothing_type.title() + "Info",
        "class_kwargs": _kwargs,
        "mixins": [],
        "attr_aliases": _aliases,
        "base_class": BiothingClient,
    }
