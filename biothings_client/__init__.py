# -*- coding: utf-8 -*-
"""
Generic client for Biothings APIs
"""
from .utils import BiothingClient
from .utils.variant import MYVARIANT_TOP_LEVEL_JSONLD_URIS
from .utils.gene import MyGeneClientMixin
from copy import copy


# ***********************************************
# *  Aliases. 
# *
# *  (key, value) pairs where the function named "key" in utils.BiothingClient
# *  is aliased as "value" in the returned client class.
# ***********************************************

# Function aliases common to all clients
COMMON_ALIASES = {
    '_metadata': 'metadata',
    '_set_caching': 'set_caching',
    '_stop_caching': 'stop_caching',
    '_clear_cache': 'clear_cache',
    '_get_fields': 'get_fields',
    '_query': 'query',
    '_querymany': 'querymany'
}

# Set project specific aliases
MYGENE_ALIASES = copy(COMMON_ALIASES)
MYGENE_ALIASES.update({'_getannotation':'getgene', '_getannotations': 'getgenes'})
MYVARIANT_ALIASES = copy(COMMON_ALIASES)
MYVARIANT_ALIASES.update({'_getannotation': 'getvariant', '_getannotations': 'getvariants'})
MYDRUG_ALIASES = copy(COMMON_ALIASES)
MYDRUG_ALIASES.update({'_getannotation': 'getdrug', '_getannotations': 'getdrugs'})
MYTAXON_ALIASES = copy(COMMON_ALIASES)
MYTAXON_ALIASES.update({'_getannotation': 'gettaxon', '_getannotations': 'gettaxa'})

# ***********************************************
# *  Kwargs. 
# *
# *  These keyword arguments are attached to the returned client class
# *  on class creation.
# ***********************************************

# Object creation kwargs common to all clients
COMMON_KWARGS = {
    "_query_endpoint": "/query/",
    "_metadata_endpoint": "/metadata",
    "_metadata_fields_endpoint": "/metadata/fields",
    "_top_level_jsonld_uris": []
}
# project specific kwargs
MYGENE_KWARGS = copy(COMMON_KWARGS)
MYGENE_KWARGS.update({"_default_url": "http://mygene.info/v3", "_pkg_user_agent_header": "MyGene.py",
    "_annotation_endpoint": "/gene/", "_optionally_plural_object_type": "gene(s)", 
    "_default_cache_file": "mygene_cache"})
MYVARIANT_KWARGS = copy(COMMON_KWARGS)
MYVARIANT_KWARGS.update({"_default_url": "http://myvariant.info/v1", "_pkg_user_agent_header": "MyVariant.py",
    "_annotation_endpoint": "/variant/", "_optionally_plural_object_type": "variant(s)", 
    "_default_cache_file": "myvariant_cache", "_top_level_jsonld_uris": MYVARIANT_TOP_LEVEL_JSONLD_URIS})
MYDRUG_KWARGS = copy(COMMON_KWARGS)
MYDRUG_KWARGS.update({"_default_url": "http://c.biothings.io/v1", "_pkg_user_agent_header": "MyDrug.py",
    "_annotation_endpoint": "/drug/", "_optionally_plural_object_type": "drug(s)", 
    "_default_cache_file": "mydrug_cache"})
MYTAXON_KWARGS = copy(COMMON_KWARGS)
MYTAXON_KWARGS.update({"_default_url": "http://t.biothings.io/v1", "_pkg_user_agent_header": "MyTaxon.py",
    "_annotation_endpoint": "/taxon/", "_optionally_plural_object_type": "taxon/taxa", 
    "_default_cache_file": "mytaxon_cache"})

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
        "class": 'MyGeneInfo',
        "class_kwargs": MYGENE_KWARGS,
        "function_aliases": MYGENE_ALIASES,
        "ancestors": (BiothingClient, MyGeneClientMixin, )
    },
    "variant": {
        "class": 'MyVariantInfo',
        "class_kwargs": MYVARIANT_KWARGS,
        "function_aliases": MYVARIANT_ALIASES,
        "ancestors": (BiothingClient, )
    },
    "taxon": {
        "class": 'MyTaxonInfo',
        "class_kwargs": MYTAXON_KWARGS,
        "function_aliases": MYTAXON_ALIASES,
        "ancestors": (BiothingClient, )
    },
    "drug": {
        "class": 'MyDrugInfo',
        "class_kwargs": MYDRUG_KWARGS,
        "function_aliases": MYDRUG_ALIASES,
        "ancestors": (BiothingClient, )
    }
}

def get_client(biothing_type, instance=True, *args, **kwargs):
    """ Function to return a new python client for a Biothings API service. 
        
        :param biothing_type: the type of biothing client, currently one of: 'gene', 'variant', 'taxon', 'drug'
        :param instance: if True, return an instance of the derived client,
                         if False, return the class of the derived client

        All other args/kwargs are passed to the derived client instantiation (if applicable) 
    """
    biothing_type = biothing_type.lower()
    if biothing_type not in CLIENT_SETTINGS:
        raise Exception("No client named '{0}', currently available clients are: {1}".format(biothing_type, list(CLIENT_SETTINGS.keys())))
    _settings = CLIENT_SETTINGS[biothing_type]
    _class = type(_settings["class"], _settings["ancestors"], _settings["class_kwargs"])
    _client = _class(*args, **kwargs) if instance else _class
    for (src_fn, target_fn) in _settings["function_aliases"].items():
        if getattr(_client, src_fn, False):
            setattr(_client, target_fn, getattr(_client, src_fn))
    return _client
