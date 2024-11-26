"""
Tests for exercising the sychronous biothings_client for mygene
"""

import logging
import types

import pytest

import biothings_client
from biothings_client.utils.score import descore
from biothings_client.client.definitions import MyVariantInfo

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def test_format_hgvs(variant_client: MyVariantInfo):
    assert variant_client.format_hgvs("1", 35366, "C", "T") == "chr1:g.35366C>T"
    assert variant_client.format_hgvs("chr2", 17142, "G", "GA") == "chr2:g.17142_17143insA"
    assert variant_client.format_hgvs("1", 10019, "TA", "T") == "chr1:g.10020del"
    assert variant_client.format_hgvs("MT", 8270, "CACCCCCTCT", "C") == "chrMT:g.8271_8279del"
    assert variant_client.format_hgvs("7", 15903, "G", "GC") == "chr7:g.15903_15904insC"
    assert variant_client.format_hgvs("X", 107930849, "GGA", "C") == "chrX:g.107930849_107930851delinsC"
    assert variant_client.format_hgvs("20", 1234567, "GTC", "GTCT") == "chr20:g.1234569_1234570insT"


def test_metadata(variant_client: MyVariantInfo):
    meta = variant_client.metadata()
    assert "stats" in meta
    assert "total" in meta["stats"]


def test_getvariant(variant_client: MyVariantInfo):
    v = variant_client.getvariant("chr9:g.107620835G>A")
    assert v["_id"] == "chr9:g.107620835G>A"
    assert v["snpeff"]["ann"]["genename"] == "ABCA1"

    v = variant_client.getvariant("'chr1:g.1A>C'")  # something does not exist
    assert v is None


def test_getvariant_with_fields(variant_client: MyVariantInfo):
    v = variant_client.getvariant("chr9:g.107620835G>A", fields="dbnsfp,cadd,cosmic")
    assert "_id" in v
    assert "dbnsfp" in v
    assert "cadd" in v
    assert "cosmic" in v


def test_getvariants(variant_client: MyVariantInfo):
    query_list1 = [
        "chr1:g.866422C>T",
        "chr1:g.876664G>A",
        "chr1:g.69635G>C",
        "chr1:g.69869T>A",
        "chr1:g.881918G>A",
        "chr1:g.865625G>A",
        "chr1:g.69892T>C",
        "chr1:g.879381C>T",
        "chr1:g.878330C>G",
    ]
    v_li = variant_client.getvariants(query_list1)
    assert len(v_li) == 9
    assert v_li[0]["_id"] == query_list1[0]
    assert v_li[1]["_id"] == query_list1[1]
    assert v_li[2]["_id"] == query_list1[2]

    variant_client.step = 4
    # test input is a string of comma-separated ids
    v_li2 = variant_client.getvariants(",".join(query_list1))
    assert v_li == v_li2
    # test input is a tuple
    v_li2 = variant_client.getvariants(tuple(query_list1))
    assert v_li == v_li2

    # test input is a generator
    def _input(li):
        for x in li:
            yield x

    v_li2 = variant_client.getvariants(_input(query_list1))
    assert v_li == v_li2
    variant_client.step = 1000


def test_query(variant_client: MyVariantInfo):
    qres = variant_client.query("dbnsfp.genename:cdk2", size=5)
    assert "hits" in qres
    assert len(qres["hits"]) == 5


def test_query_hgvs(variant_client: MyVariantInfo):
    qres = variant_client.query('"NM_000048.4:c.566A>G"', size=5)
    # should match clinvar.hgvs.coding field from variant "chr7:g.65551772A>G"
    # sometime we need to update ".4" part if clinvar data updated.
    assert "hits" in qres
    assert len(qres["hits"]) == 1


def test_query_rsid(variant_client: MyVariantInfo):
    qres = variant_client.query("dbsnp.rsid:rs58991260")
    assert "hits" in qres
    assert len(qres["hits"]) == 1
    assert qres["hits"][0]["_id"] == "chr1:g.218631822G>A"
    qres2 = variant_client.query("rs58991260")

    # exclude _score field before comparison
    qres["hits"][0].pop("_score")
    qres2["hits"][0].pop("_score")
    assert qres["hits"] == qres2["hits"]


def test_query_symbol(variant_client: MyVariantInfo):
    qres = variant_client.query("snpeff.ann.genename:cdk2")
    assert "hits" in qres
    assert qres["total"] > 5000
    assert qres["hits"][0]["snpeff"]["ann"][0]["genename"] == "CDK2"


def test_query_genomic_range(variant_client: MyVariantInfo):
    qres = variant_client.query("chr1:69000-70000")
    assert "hits" in qres
    assert qres["total"] >= 3


def test_query_fetch_all(variant_client: MyVariantInfo):
    qres = variant_client.query("chr1:69500-70000", fields="chrom")
    total = qres["total"]

    qres = variant_client.query("chr1:69500-70000", fields="chrom", fetch_all=True)
    assert isinstance(qres, types.GeneratorType)
    assert total == len(list(qres))


def test_querymany(variant_client: MyVariantInfo):
    query_list1 = [
        "chr1:g.866422C>T",
        "chr1:g.876664G>A",
        "chr1:g.69635G>C",
        "chr1:g.69869T>A",
        "chr1:g.881918G>A",
        "chr1:g.865625G>A",
        "chr1:g.69892T>C",
        "chr1:g.879381C>T",
        "chr1:g.878330C>G",
    ]
    qres = variant_client.querymany(query_list1, verbose=False)
    assert len(qres) == 9

    variant_client.step = 4

    # test input as a string
    qres2 = variant_client.querymany(",".join(query_list1), verbose=False)
    assert qres == qres2

    # test input as a tuple
    qres2 = variant_client.querymany(tuple(query_list1), verbose=False)
    assert qres == qres2

    # test input as a iterator
    qres2 = variant_client.querymany(iter(query_list1), verbose=False)
    assert qres == qres2
    variant_client.step = 1000


def test_querymany_with_scopes(variant_client: MyVariantInfo):
    qres = variant_client.querymany(["rs58991260", "rs2500"], scopes="dbsnp.rsid", verbose=False)
    assert len(qres) == 2

    qres = variant_client.querymany(
        ["RCV000083620", "RCV000083611", "RCV000083584"], scopes="clinvar.rcv_accession", verbose=False
    )
    assert len(qres) == 3

    qres = variant_client.querymany(
        ["rs2500", "RCV000083611", "COSM1392449"],
        scopes="clinvar.rcv_accession,dbsnp.rsid,cosmic.cosmic_id",
        verbose=False,
    )
    assert len(qres) == 3


def test_querymany_fields(variant_client: MyVariantInfo):
    ids = ["COSM1362966", "COSM990046", "COSM1392449"]
    qres1 = variant_client.querymany(
        ids, scopes="cosmic.cosmic_id", fields=["cosmic.tumor_site", "cosmic.cosmic_id"], verbose=False
    )
    assert len(qres1) == 3

    qres2 = variant_client.querymany(
        ids, scopes="cosmic.cosmic_id", fields="cosmic.tumor_site,cosmic.cosmic_id", verbose=False
    )
    assert len(qres2) == 3

    assert descore(qres1) == descore(qres2)


def test_querymany_notfound(variant_client: MyVariantInfo):
    qres = variant_client.querymany(["rs58991260", "rs2500", "NA_TEST"], scopes="dbsnp.rsid", verbose=False)
    assert len(qres) == 3
    assert qres[2] == {"query": "NA_TEST", "notfound": True}


@pytest.mark.skipif(not biothings_client._PANDAS, reason="pandas library not installed")
def test_querymany_dataframe(variant_client: MyVariantInfo):
    from pandas import DataFrame

    query_list2 = [
        "rs374802787",
        "rs1433078",
        "rs1433115",
        "rs377266517",
        "rs587640013",
        "rs137857980",
        "rs199710579",
        "rs186823979",
        # 'rs2276240',
        "rs34521797",
        "rs372452565",
    ]

    qres = variant_client.querymany(query_list2, scopes="dbsnp.rsid", fields="dbsnp", as_dataframe=True, verbose=False)
    assert isinstance(qres, DataFrame)
    assert "dbsnp.vartype" in qres.columns
    assert set(query_list2) == set(qres.index)


def test_querymany_step(variant_client: MyVariantInfo):
    query_list2 = [
        "rs374802787",
        "rs1433078",
        "rs1433115",
        "rs377266517",
        "rs587640013",
        "rs137857980",
        "rs199710579",
        "rs186823979",
        # 'rs2276240',
        "rs34521797",
        "rs372452565",
    ]
    qres1 = variant_client.querymany(query_list2, scopes="dbsnp.rsid", fields="dbsnp.rsid", verbose=False)
    default_step = variant_client.step
    variant_client.step = 3
    qres2 = variant_client.querymany(query_list2, scopes="dbsnp.rsid", fields="dbsnp.rsid", verbose=False)
    variant_client.step = default_step
    # assert qres1, qres2, (qres1, qres2))
    assert descore(qres1) == descore(qres2)


def test_get_fields(variant_client: MyVariantInfo):
    fields = variant_client.get_fields()
    assert "dbsnp.chrom" in fields.keys()
    assert "clinvar.chrom" in fields.keys()
