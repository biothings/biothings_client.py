from biothings_client.client import get_client, get_async_client


### MYGENE CLIENTS
class MyGeneInfo(get_client("gene", instance=False)):
    pass


class AsyncMyGeneInfo(get_async_client("gene", instance=False)):
    pass


### MYVARIANT CLIENTS
class MyVariantInfo(get_client("variant", instance=False)):
    pass


class AsyncMyVariantInfo(get_async_client("variant", instance=False)):
    pass


### MYCHEM CLIENTS
class MyChemInfo(get_client("chem", instance=False)):
    pass


class AsyncMyChemInfo(get_async_client("chem", instance=False)):
    pass


### MYDISEASE CLIENTS
class MyDiseaseInfo(get_client("disease", instance=False)):
    pass


class AsyncMyDiseaseInfo(get_async_client("disease", instance=False)):
    pass


### MYTAXON CLIENTS
class MyTaxonInfo(get_client("taxon", instance=False)):
    pass


class AsyncMyTaxonInfo(get_async_client("taxon", instance=False)):
    pass


### MYGENESET CLIENTS
class MyGenesetInfo(get_client("geneset", instance=False)):
    pass


class AsyncMyGenesetInfo(get_async_client("geneset", instance=False)):
    pass
