"""
Settings and configuration values for the different biothings-clients
"""

from copy import copy

from biothings_client.docstring.chem import DOCSTRING as CHEM_DOCSTRING
from biothings_client.docstring.gene import DOCSTRING as GENE_DOCSTRING
from biothings_client.docstring.variant import DOCSTRING as VARIANT_DOCSTRING
from biothings_client.utils.variant import MYVARIANT_TOP_LEVEL_JSONLD_URIS


# ***********************************************
# *  Aliases.
# *
# *  (key, value) pairs where the function named "key" in utils.BiothingClient
# *  is aliased as "value" in the returned client class.
# ***********************************************
# Function aliases common to all clients
COMMON_ALIASES = {
    "_clear_cache": "clear_cache",
    "_get_fields": "get_fields",
    "_metadata": "metadata",
    "_query": "query",
    "_querymany": "querymany",
    "_set_caching": "set_caching",
    "_stop_caching": "stop_caching",
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
    "_delay": 1,
    "_docstring_obj": {},
    "_max_query": 1000,
    "_metadata_endpoint": "/metadata",
    "_metadata_fields_endpoint": "/metadata/fields",
    "_pkg_user_agent_header": "biothings_client.py",
    "_query_endpoint": "/query/",
    "_scroll_size": 1000,
    "_step": 1000,
    "_top_level_jsonld_uris": [],
}
# project specific kwargs
MYGENE_KWARGS = copy(COMMON_KWARGS)
MYGENE_KWARGS.update(
    {
        "_annotation_endpoint": "/gene/",
        "_default_cache_file": "mygene_cache",
        "_default_url": "https://mygene.info/v3",
        "_docstring_obj": GENE_DOCSTRING,
        "_entity": "gene",
        "_optionally_plural_object_type": "gene(s)",
    }
)
MYVARIANT_KWARGS = copy(COMMON_KWARGS)
MYVARIANT_KWARGS.update(
    {
        "_annotation_endpoint": "/variant/",
        "_default_cache_file": "myvariant_cache",
        "_default_url": "https://myvariant.info/v1",
        "_docstring_obj": VARIANT_DOCSTRING,
        "_entity": "variant",
        "_optionally_plural_object_type": "variant(s)",
        "_top_level_jsonld_uris": MYVARIANT_TOP_LEVEL_JSONLD_URIS,
    }
)
MYCHEM_KWARGS = copy(COMMON_KWARGS)
MYCHEM_KWARGS.update(
    {
        "_annotation_endpoint": "/chem/",
        "_default_cache_file": "mychem_cache",
        "_default_url": "https://mychem.info/v1",
        "_docstring_obj": CHEM_DOCSTRING,
        "_entity": "chem",
        "_optionally_plural_object_type": "chem(s)",
    }
)
MYDISEASE_KWARGS = copy(COMMON_KWARGS)
MYDISEASE_KWARGS.update(
    {
        "_annotation_endpoint": "/disease/",
        "_default_cache_file": "mydisease_cache",
        "_default_url": "https://mydisease.info/v1",
        "_entity": "disease",
        "_optionally_plural_object_type": "disease(s)",
    }
)
MYTAXON_KWARGS = copy(COMMON_KWARGS)
MYTAXON_KWARGS.update(
    {
        "_annotation_endpoint": "/taxon/",
        "_default_cache_file": "mytaxon_cache",
        "_default_url": "https://t.biothings.io/v1",
        "_entity": "taxon",
        "_optionally_plural_object_type": "taxon/taxa",
    }
)
MYGENESET_KWARGS = copy(COMMON_KWARGS)
MYGENESET_KWARGS.update(
    {
        "_annotation_endpoint": "/geneset/",
        "_default_cache_file": "mygeneset_cache",
        "_default_url": "https://mygeneset.info/v1",
        "_entity": "geneset",
        "_optionally_plural_object_type": "geneset(s)",
    }
)
