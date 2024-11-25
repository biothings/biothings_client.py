"""
Mirror of the gene tests but two main differences:
> asynchronous
> implemented in pytest for asyncio marker
"""

import logging
import types

import pytest


import biothings_client
from biothings_client.client.definitions import AsyncMyGeneInfo
from biothings_client.utils.score import descore


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


@pytest.mark.asyncio
async def test_metadata(async_gene_client: AsyncMyGeneInfo):
    gene_metadata = await async_gene_client.metadata()
    assert "stats" in gene_metadata
    assert "total_genes" in gene_metadata["stats"]


@pytest.mark.asyncio
async def test_getgene(async_gene_client: AsyncMyGeneInfo):
    g = await async_gene_client.getgene("1017")
    assert g["_id"] == "1017"
    assert g["symbol"] == "CDK2"


@pytest.mark.asyncio
async def test_getgene_with_fields(async_gene_client: AsyncMyGeneInfo):
    g = await async_gene_client.getgene("1017", fields="name,symbol,refseq")
    assert "_id" in g
    assert "name" in g
    assert "symbol" in g
    assert "refseq" in g
    assert "summary" not in g


@pytest.mark.asyncio
async def test_curie_id_query(async_gene_client: AsyncMyGeneInfo):
    """
    Tests the annotation endpoint support for the biolink CURIE ID.

    If support is enabled then we should retrieve the exact same document for all the provided
    queries
    """
    curie_id_testing_collection = [
        ("1017", "entrezgene:1017", "NCBIgene:1017"),
        (1017, "entrezgene:1017", "ncbigene:1017"),
        ("1017", "entrezgene:1017", "NCBIGENE:1017"),
        ("1018", "ensembl.gene:ENSG00000250506", "ENSEMBL:ENSG00000250506"),
        (1018, "ensembl.gene:ENSG00000250506", "ensembl:ENSG00000250506"),
        ("5995", "uniprot.Swiss-Prot:P47804", "UniProtKB:P47804"),
        (5995, "uniprot.Swiss-Prot:P47804", "UNIPROTKB:P47804"),
        ("5995", "uniprot.Swiss-Prot:P47804", "uniprotkb:P47804"),
    ]

    results_aggregation = []
    for id_query, biothings_query, biolink_query in curie_id_testing_collection:
        id_query_result = await async_gene_client.getgene(_id=id_query)
        biothings_term_query_result = await async_gene_client.getgene(_id=biothings_query)
        biolink_term_query_result = await async_gene_client.getgene(_id=biolink_query)
        results_aggregation.append(
            (
                id_query_result == biothings_term_query_result,
                id_query_result == biolink_term_query_result,
                biothings_term_query_result == biolink_term_query_result,
            )
        )

    results_validation = []
    failure_messages = []
    for result, test_query in zip(results_aggregation, curie_id_testing_collection):
        cumulative_result = all(result)
        if not cumulative_result:
            failure_messages.append(f"Query Failure: {test_query} | Results: {result}")
        results_validation.append(cumulative_result)

    assert all(results_validation), "\n".join(failure_messages)


@pytest.mark.asyncio
async def test_multiple_curie_id_query(async_gene_client: AsyncMyGeneInfo):
    """
    Tests the annotations endpoint support for the biolink CURIE ID.

    Batch query testing against the POST endpoint to verify that the CURIE ID can work with
    multiple

    If support is enabled then we should retrieve the exact same document for all the provided
    queries
    """
    curie_id_testing_collection = [
        ("1017", "entrezgene:1017", "NCBIgene:1017"),
        (1017, "entrezgene:1017", "ncbigene:1017"),
        ("1017", "entrezgene:1017", "NCBIGENE:1017"),
        ("1018", "ensembl.gene:ENSG00000250506", "ENSEMBL:ENSG00000250506"),
        (1018, "ensembl.gene:ENSG00000250506", "ensembl:ENSG00000250506"),
        ("5995", "uniprot.Swiss-Prot:P47804", "UniProtKB:P47804"),
        (5995, "uniprot.Swiss-Prot:P47804", "UNIPROTKB:P47804"),
        ("5995", "uniprot.Swiss-Prot:P47804", "uniprotkb:P47804"),
    ]

    results_aggregation = []
    for id_query, biothings_query, biolink_query in curie_id_testing_collection:
        base_result = await async_gene_client.getgene(_id=id_query)

        batch_query = [id_query, biothings_query, biolink_query]
        query_results = await async_gene_client.getgenes(ids=batch_query)
        assert len(query_results) == len(batch_query)

        batch_id_query = query_results[0]
        batch_biothings_query = query_results[1]
        batch_biolink_query = query_results[2]

        batch_id_query_return_value = batch_id_query.pop("query")
        assert batch_id_query_return_value == str(id_query)

        batch_biothings_query_return_value = batch_biothings_query.pop("query")
        assert batch_biothings_query_return_value == str(biothings_query)

        batch_biolink_query_return_value = batch_biolink_query.pop("query")
        assert batch_biolink_query_return_value == str(biolink_query)

        batch_result = (
            base_result == batch_id_query,
            base_result == batch_biothings_query,
            base_result == batch_biolink_query,
        )
        results_aggregation.append(batch_result)

    results_validation = []
    failure_messages = []
    for result, test_query in zip(results_aggregation, curie_id_testing_collection):
        cumulative_result = all(result)
        if not cumulative_result:
            failure_messages.append(f"Query Failure: {test_query} | Results: {result}")
        results_validation.append(cumulative_result)

    assert all(results_validation), "\n".join(failure_messages)


@pytest.mark.asyncio
async def test_getgene_with_fields_as_list(async_gene_client: AsyncMyGeneInfo):
    g1 = await async_gene_client.getgene("1017", fields="name,symbol,refseq")
    g2 = await async_gene_client.getgene("1017", fields=["name", "symbol", "refseq"])
    assert g1 == g2


@pytest.mark.asyncio
async def test_getgenes(async_gene_client: AsyncMyGeneInfo):
    g_li = await async_gene_client.getgenes([1017, 1018, "ENSG00000148795"])
    assert len(g_li) == 3
    assert g_li[0]["_id"] == "1017"
    assert g_li[1]["_id"] == "1018"
    assert g_li[2]["_id"] == "1586"


@pytest.mark.asyncio
async def test_query(async_gene_client: AsyncMyGeneInfo):
    qres = await async_gene_client.query("cdk2", size=5)
    assert "hits" in qres
    assert len(qres["hits"]) == 5


@pytest.mark.asyncio
async def test_query_with_fields_as_list(async_gene_client: AsyncMyGeneInfo):
    qres1 = await async_gene_client.query("entrezgene:1017", fields="name,symbol,refseq")
    qres2 = await async_gene_client.query("entrezgene:1017", fields=["name", "symbol", "refseq"])
    assert "hits" in qres1
    assert len(qres1["hits"]) == 1
    assert descore(qres1["hits"]) == descore(qres2["hits"])


@pytest.mark.asyncio
async def test_query_reporter(async_gene_client: AsyncMyGeneInfo):
    qres = await async_gene_client.query("reporter:1000_at")
    assert "hits" in qres
    assert len(qres["hits"]) == 1
    assert qres["hits"][0]["_id"] == "5595"


@pytest.mark.asyncio
async def test_query_symbol(async_gene_client: AsyncMyGeneInfo):
    qres = await async_gene_client.query("symbol:cdk2", species="mouse")
    assert "hits" in qres
    assert len(qres["hits"]) == 1
    assert qres["hits"][0]["_id"] == "12566"


@pytest.mark.asyncio
async def test_query_fetch_all(async_gene_client: AsyncMyGeneInfo):
    qres = await async_gene_client.query("_exists_:pdb")
    total = qres["total"]

    qres_generator = await async_gene_client.query("_exists_:pdb", fields="pdb", fetch_all=True)
    assert isinstance(qres_generator, types.AsyncGeneratorType)

    async_count = 0
    async for async_res in qres_generator:
        async_count += 1
    assert total == async_count


@pytest.mark.asyncio
async def test_querymany(async_gene_client: AsyncMyGeneInfo):
    qres = await async_gene_client.querymany([1017, "695"], verbose=False)
    assert len(qres) == 2

    qres = await async_gene_client.querymany("1017,695", verbose=False)
    assert len(qres) == 2


@pytest.mark.asyncio
async def test_querymany_with_scopes(async_gene_client: AsyncMyGeneInfo):
    qres = await async_gene_client.querymany([1017, "695"], scopes="entrezgene", verbose=False)
    assert len(qres) == 2

    qres = await async_gene_client.querymany([1017, "BTK"], scopes="entrezgene,symbol", verbose=False)
    assert len(qres) >= 2


@pytest.mark.asyncio
async def test_querymany_species(async_gene_client: AsyncMyGeneInfo):
    qres = await async_gene_client.querymany([1017, "695"], scopes="entrezgene", species="human", verbose=False)
    assert len(qres) == 2

    qres = await async_gene_client.findgenes([1017, "695"], scopes="entrezgene", species=9606, verbose=False)
    assert len(qres) == 2

    qres = await async_gene_client.findgenes([1017, "CDK2"], scopes="entrezgene,symbol", species=9606, verbose=False)
    assert len(qres) == 2


@pytest.mark.asyncio
async def test_querymany_fields(async_gene_client: AsyncMyGeneInfo):
    qres1 = await async_gene_client.findgenes(
        [1017, "CDK2"], scopes="entrezgene,symbol", fields=["uniprot", "unigene"], species=9606, verbose=False
    )
    assert len(qres1) == 2

    qres2 = await async_gene_client.findgenes(
        "1017,CDK2", scopes="entrezgene,symbol".split(","), fields="uniprot,unigene", species=9606, verbose=False
    )
    assert len(qres2) == 2
    assert descore(qres1) == descore(qres2)


@pytest.mark.asyncio
async def test_querymany_notfound(async_gene_client: AsyncMyGeneInfo):
    qres = await async_gene_client.findgenes([1017, "695", "NA_TEST"], scopes="entrezgene", species=9606)
    assert len(qres) == 3
    assert qres[2] == {"query": "NA_TEST", "notfound": True}


@pytest.mark.asyncio
@pytest.mark.skipif(not biothings_client._PANDAS, reason="requires the pandas library")
async def test_querymany_dataframe(async_gene_client: AsyncMyGeneInfo):
    from pandas import DataFrame

    query_list = [
        "1007_s_at",
        "1053_at",
        "117_at",
        "121_at",
        "1255_g_at",
        "1294_at",
        "1316_at",
        "1320_at",
        "1405_i_at",
        "1431_at",
    ]

    qres = await async_gene_client.querymany(query_list, scopes="reporter", as_dataframe=True)
    assert isinstance(qres, DataFrame)
    assert "name" in qres.columns
    assert set(query_list), set(qres.index)


@pytest.mark.asyncio
async def test_querymany_step(async_gene_client: AsyncMyGeneInfo):
    query_list = [
        "1007_s_at",
        "1053_at",
        "117_at",
        "121_at",
        "1255_g_at",
        "1294_at",
        "1316_at",
        "1320_at",
        "1405_i_at",
        "1431_at",
    ]
    qres1 = await async_gene_client.querymany(query_list, scopes="reporter")
    default_step = async_gene_client.step
    async_gene_client.step = 3
    qres2 = await async_gene_client.querymany(query_list, scopes="reporter")
    async_gene_client.step = default_step
    qres1 = descore(sorted(qres1, key=lambda doc: doc["_id"]))
    qres2 = descore(sorted(qres2, key=lambda doc: doc["_id"]))
    assert qres1 == qres2


@pytest.mark.asyncio
async def test_get_fields(async_gene_client: AsyncMyGeneInfo):
    fields = await async_gene_client.get_fields()
    assert "uniprot" in fields.keys()
    assert "exons" in fields.keys()

    fields = await async_gene_client.get_fields("kegg")
    assert "pathway.kegg" in fields.keys()
