"""
Tests our async client creation process
"""

import os
import sys

import biothings_client


def test_get_async_client():
    breakpoint()
    gene_client = biothings_client.get_client("gene")
    assert type(gene_client).__name__, "MyGeneInfo"

    variant_client = biothings_client.get_client("variant")
    assert type(variant_client).__name__, "MyVariantInfo"

    chem_client = biothings_client.get_client("chem")
    assert type(chem_client).__name__, "MyChemInfo"

    # drug_client as an alias of chem_client
    drug_client = biothings_client.get_client("drug")
    assert type(drug_client).__name__, "MyChemInfo"

    disease_client = biothings_client.get_client("disease")
    assert type(disease_client).__name__, "MyDiseaseInfo"

    taxon_client = biothings_client.get_client("taxon")
    assert type(taxon_client).__name__, "MyTaxonInfo"

    geneset_client = biothings_client.get_client("geneset")
    assert type(geneset_client).__name__, "MyGenesetInfo"

    geneset_client = biothings_client.get_client(url="https://mygeneset.info/v1")
    assert type(geneset_client).__name__, "MyGenesetInfo"
