"""
Tests for exercising the sychronous biothings_client for mygeneset
"""

import logging
import types

import pytest

import biothings_client
from biothings_client.utils.score import descore
from biothings_client.client.definitions import MyGenesetInfo


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def test_metadata(geneset_client: MyGenesetInfo):
    meta = geneset_client.metadata()
    assert "src" in meta
    assert "stats" in meta
    assert "total" in meta["stats"]


def test_getgeneset(geneset_client: MyGenesetInfo):
    gs = geneset_client.getgeneset("WP100")
    assert gs["_id"] == "WP100"
    assert gs["name"] == "Glutathione metabolism"
    assert gs["source"] == "wikipathways"
    assert gs["taxid"] == "9606"
    assert len(gs["genes"]) >= 19
    assert gs["count"] == len(gs["genes"])

    assert "wikipathways" in gs
    assert gs["wikipathways"]["id"] == "WP100"
    assert gs["wikipathways"]["pathway_name"] == "Glutathione metabolism"
    assert gs["wikipathways"]["url"] == "https://www.wikipathways.org/instance/WP100"
    assert gs["wikipathways"]["_license"] == "https://www.wikipathways.org/terms.html"

    assert any((gene.get("mygene_id") == "2937" and gene.get("symbol") == "GSS") for gene in gs["genes"])


def test_query_fetch_all(geneset_client: MyGenesetInfo):
    """
    pdb --> reactome
    q = source:reactome
    _exists_:pdb ---> source:reactome
    """
    qres = geneset_client.query("source:reactome")
    total = qres["total"]

    qres = geneset_client.query("source:reactome", fields="source,count,name", fetch_all=True)
    assert isinstance(qres, types.GeneratorType)
    assert total == len(list(qres))


def test_query_with_fields_as_list(geneset_client: MyGenesetInfo):
    qres1 = geneset_client.query("genes.ncbigene:1017", fields="name,source,taxid")
    qres2 = geneset_client.query("genes.ncbigene:1017", fields=["name", "source", "taxid"])
    assert "hits" in qres1
    assert len(qres1["hits"]) == 10
    assert descore(qres1["hits"]) == descore(qres2["hits"])


def test_getgeneset_with_fields(geneset_client: MyGenesetInfo):
    gs = geneset_client.getgeneset("WP100", fields="name,source,taxid,genes.mygene_id,genes.symbol")

    assert "_id" in gs
    assert "name" in gs
    assert "source" in gs
    assert "taxid" in gs

    assert any((gene.get("mygene_id") == "2937" and gene.get("symbol") == "GSS") for gene in gs["genes"])
    assert not any(gene.get("name") for gene in gs["genes"])


def test_getgenesets(geneset_client: MyGenesetInfo):
    gs_li = geneset_client.getgenesets(["WP100", "WP101", "WP103"])

    assert len(gs_li) == 3
    assert gs_li[0]["_id"] == "WP100"
    assert gs_li[1]["_id"] == "WP101"
    assert gs_li[2]["_id"] == "WP103"


def test_query(geneset_client: MyGenesetInfo):
    qres = geneset_client.query("genes.mygene_id:2937", size=5)
    assert "hits" in qres
    assert len(qres["hits"]) == 5


def test_query_default_fields(geneset_client: MyGenesetInfo):
    geneset_client.query(q="glucose")


def test_query_field(geneset_client: MyGenesetInfo):
    geneset_client.query(q="genes.ncbigene:1017")


def test_species_filter_plus_query(geneset_client: MyGenesetInfo):
    dog = geneset_client.query(q="glucose", species="9615")
    assert dog["hits"][0]["taxid"] == "9615"


def test_query_by_id(geneset_client: MyGenesetInfo):
    query = geneset_client.query(q="_id:WP100")
    assert query["hits"][0]["_id"] == "WP100"


def test_query_by_name(geneset_client: MyGenesetInfo):
    kinase = geneset_client.query(q="name:kinase")
    assert "kinase" in kinase["hits"][0]["name"].lower()


def test_query_by_description(geneset_client: MyGenesetInfo):
    desc = geneset_client.query(q="description:cytosine deamination")
    assert "cytosine" in desc["hits"][0]["description"].lower()
    assert "deamination" in desc["hits"][0]["description"].lower()


def test_query_by_source_go(geneset_client: MyGenesetInfo):
    go = geneset_client.query(q="source:go", fields="all")
    assert "go" in go["hits"][0].keys()
    assert go["hits"][0]["source"] == "go"


def test_query_by_source_ctd(geneset_client: MyGenesetInfo):
    ctd = geneset_client.query(q="source:ctd", fields="all")
    assert "ctd" in ctd["hits"][0].keys()
    assert ctd["hits"][0]["source"] == "ctd"


def test_query_by_source_msigdb(geneset_client: MyGenesetInfo):
    msigdb = geneset_client.query(q="source:msigdb", fields="all")
    assert "msigdb" in msigdb["hits"][0].keys()
    assert msigdb["hits"][0]["source"] == "msigdb"


@pytest.mark.xfail(reason="We removed kegg data source for now")
def test_query_by_source_kegg(geneset_client: MyGenesetInfo):
    kegg = geneset_client.query(q="source:kegg", fields="all")
    assert "kegg" in kegg["hits"][0].keys()
    assert kegg["hits"][0]["source"] == "kegg"


def test_query_by_source_do(geneset_client: MyGenesetInfo):
    do = geneset_client.query(q="source:do", fields="all")
    assert "do" in do["hits"][0].keys()
    assert do["hits"][0]["source"] == "do"


def test_query_by_source_reactome(geneset_client: MyGenesetInfo):
    reactome = geneset_client.query(q="source:reactome", fields="all")
    assert "reactome" in reactome["hits"][0].keys()
    assert reactome["hits"][0]["source"] == "reactome"


def test_query_by_source_smpdb(geneset_client: MyGenesetInfo):
    smpdb = geneset_client.query(q="source:smpdb", fields="all")
    assert "smpdb" in smpdb["hits"][0].keys()
    assert smpdb["hits"][0]["source"] == "smpdb"
