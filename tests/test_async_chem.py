"""
Mirror of the chem tests but two main differences:
> asynchronous
> implemented in pytest for asyncio marker
"""

import json
import logging
import types

import pytest


import biothings_client
from biothings_client.client.definitions import AsyncMyChemInfo
from biothings_client.utils.score import descore


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


@pytest.mark.asyncio
async def test_metadata(async_chem_client: AsyncMyChemInfo):
    chem_metadata = await async_chem_client.metadata()
    assert "src" in chem_metadata
    assert "stats" in chem_metadata
    assert "total" in chem_metadata["stats"]


@pytest.mark.asyncio
async def test_getchem(async_chem_client: AsyncMyChemInfo):
    c = await async_chem_client.getchem("ZRALSGWEFCBTJO-UHFFFAOYSA-N")
    assert c["_id"] == "ZRALSGWEFCBTJO-UHFFFAOYSA-N"
    assert c["chebi"]["name"] == "guanidine"


@pytest.mark.asyncio
async def test_getchem_with_fields(async_chem_client: AsyncMyChemInfo):
    c = await async_chem_client.getchem("7AXV542LZ4", fields="chebi.name,chembl.inchi_key,pubchem.cid")
    assert "_id" in c
    assert "chebi" in c
    assert "name" in c["chebi"]
    assert "chembl" in c
    assert "inchi_key" in c["chembl"]
    assert "pubchem" in c
    assert "cid" in c["pubchem"]


@pytest.mark.asyncio
async def test_curie_id_query(async_chem_client: AsyncMyChemInfo):
    """
    Tests the annotation endpoint support for the biolink CURIE ID.

    If support is enabled then we should retrieve the exact same document for all the provided
    queries
    """
    curie_id_testing_collection = [
        (
            "UCMIRNVEIXFBKS-UHFFFAOYSA-N",
            "CHEMBL297569",
            "CHEMBL.COMPOUND:CHEMBL297569",
            "chembl.compound:CHEMBL297569",
            "cHEmbl.ComPOUND:CHEMBL297569",
            "chembl.molecule_chembl_id:CHEMBL297569",
        ),
        (
            "AKUPVPKIFATOBM-UHFFFAOYSA-N",
            "120933777",
            120933777,
            "PUBCHEM.COMPOUND:120933777",
            "pubchem.compound:120933777",
            "PuBcHEm.COMPound:120933777",
            "pubchem.cid:120933777",
        ),
        (
            "UCMIRNVEIXFBKS-UHFFFAOYSA-N",
            "CHEBI:CHEBI:57966",
            "chebi:CHEBI:57966",
            "CheBi:CHEBI:57966",
            "chebi.id:CHEBI:57966",
        ),
        (
            "UCMIRNVEIXFBKS-UHFFFAOYSA-N",
            "11P2JDE17B",
            "UNII:11P2JDE17B",
            "unii:11P2JDE17B",
            "uNIi:11P2JDE17B",
            "unii.unii:11P2JDE17B",
        ),
        (
            "UCMIRNVEIXFBKS-UHFFFAOYSA-N",
            "dB03107",
            "DRUGBANK:dB03107",
            "drugbank:dB03107",
            "DrugBaNK:dB03107",
            "drugbank.id:dB03107",
        ),
    ]

    aggregation_query_groups = []
    for query_collection in curie_id_testing_collection:
        query_result_storage = []
        for similar_query in query_collection:
            query_result = await async_chem_client.getchem(_id=similar_query)
            query_result_storage.append(query_result)

        results_aggregation = [query == query_result_storage[0] for query in query_result_storage[1:]]

        query_result_mapping = dict(zip(query_collection[1:], results_aggregation))
        logger.debug(
            "Comparison to first term %s ->\n%s", query_collection[0], json.dumps(query_result_mapping, indent=4)
        )

        if all(results_aggregation):
            logger.info("Query group %s succeeded", query_collection)
        else:
            logger.error("Query group %s failed", query_collection)

        aggregation_query_groups.append(all(results_aggregation))
    assert all(aggregation_query_groups)


@pytest.mark.asyncio
async def test_multiple_curie_id_query(async_chem_client: AsyncMyChemInfo):
    """
    Tests the annotations endpoint support for the biolink CURIE ID.

    Batch query testing against the POST endpoint to verify that the CURIE ID can work with
    multiple

    If support is enabled then we should retrieve the exact same document for all the provided
    queries
    """
    curie_id_testing_collection = [
        (
            "UCMIRNVEIXFBKS-UHFFFAOYSA-N",
            "CHEMBL297569",
            "CHEMBL.COMPOUND:CHEMBL297569",
            "chembl.compound:CHEMBL297569",
            "cHEmbl.ComPOUND:CHEMBL297569",
            "chembl.molecule_chembl_id:CHEMBL297569",
        ),
        (
            "AKUPVPKIFATOBM-UHFFFAOYSA-N",
            "120933777",
            120933777,
            "PUBCHEM.COMPOUND:120933777",
            "pubchem.compound:120933777",
            "PuBcHEm.COMPound:120933777",
            "pubchem.cid:120933777",
        ),
        (
            "UCMIRNVEIXFBKS-UHFFFAOYSA-N",
            "CHEBI:CHEBI:57966",
            "chebi:CHEBI:57966",
            "CheBi:CHEBI:57966",
            "chebi.id:CHEBI:57966",
        ),
        (
            "UCMIRNVEIXFBKS-UHFFFAOYSA-N",
            "11P2JDE17B",
            "UNII:11P2JDE17B",
            "unii:11P2JDE17B",
            "uNIi:11P2JDE17B",
            "unii.unii:11P2JDE17B",
        ),
        (
            "UCMIRNVEIXFBKS-UHFFFAOYSA-N",
            "dB03107",
            "DRUGBANK:dB03107",
            "drugbank:dB03107",
            "DrugBaNK:dB03107",
            "drugbank.id:dB03107",
        ),
    ]

    results_aggregation = []
    for query_collection in curie_id_testing_collection:
        base_result = await async_chem_client.getchem(_id=query_collection[0])
        query_results = await async_chem_client.getchems(ids=query_collection)
        assert len(query_results) == len(query_collection)

        batch_result = []
        for query_result, query_entry in zip(query_results, query_collection):
            return_query_field = query_result.pop("query")
            assert return_query_field == str(query_entry)
            batch_result.append(base_result == query_result)

        aggregate_result = all(results_aggregation)

        query_result_mapping = dict(zip(query_collection[1:], results_aggregation))
        logger.debug(
            "Comparison to first term %s ->\n%s", query_collection[0], json.dumps(query_result_mapping, indent=4)
        )

        if aggregate_result:
            logger.info("Query group %s succeeded", query_collection)
        else:
            logger.error("Query group %s failed", query_collection)

        results_aggregation.append(aggregate_result)
    assert all(results_aggregation)


@pytest.mark.asyncio
@pytest.mark.xfail
async def get_getdrug(async_chem_client: AsyncMyChemInfo):
    c = await async_chem_client.getdrug("CHEMBL1308")
    assert c["_id"] == "ZRALSGWEFCBTJO-UHFFFAOYSA-N"
    c = await async_chem_client.getdrug("7AXV542LZ4")
    assert c["_id"] == "ZRALSGWEFCBTJO-UHFFFAOYSA-N"
    c = await async_chem_client.getdrug("CHEBI:6431")
    assert c["_id"] == "ZRALSGWEFCBTJO-UHFFFAOYSA-N"

    # PubChem CID
    # not working yet
    c = await async_chem_client.getdrug("CID:1990")
    assert c["_id"] == "ZRALSGWEFCBTJO-UHFFFAOYSA-N"
    c = await async_chem_client.getdrug("1990")
    assert c["_id"] == "ZRALSGWEFCBTJO-UHFFFAOYSA-N"


@pytest.mark.asyncio
async def test_getchems(async_chem_client: AsyncMyChemInfo):
    c_li = await async_chem_client.getchems(
        ["KTUFNOKKBVMGRW-UHFFFAOYSA-N", "HXHWSAZORRCQMX-UHFFFAOYSA-N", "DQMZLTXERSFNPB-UHFFFAOYSA-N"]
    )
    assert len(c_li) == 3
    assert c_li[0]["_id"] == "KTUFNOKKBVMGRW-UHFFFAOYSA-N"
    assert c_li[1]["_id"] == "HXHWSAZORRCQMX-UHFFFAOYSA-N"
    assert c_li[2]["_id"] == "DQMZLTXERSFNPB-UHFFFAOYSA-N"


@pytest.mark.asyncio
async def test_query(async_chem_client: AsyncMyChemInfo):
    qres = await async_chem_client.query("chebi.name:albendazole", size=5)
    assert "hits" in qres
    assert len(qres["hits"]) == 5


@pytest.mark.asyncio
@pytest.mark.skip(reason="drugbank datasource removed")
async def test_query_drugbank(async_chem_client: AsyncMyChemInfo):
    qres = await async_chem_client.query("drugbank.id:DB00536")
    assert "hits" in qres
    assert len(qres["hits"]) == 1
    assert qres["hits"][0]["_id"] == "ZRALSGWEFCBTJO-UHFFFAOYSA-N"


@pytest.mark.asyncio
async def test_query_chebi(async_chem_client: AsyncMyChemInfo):
    qres = await async_chem_client.query(r"chebi.id:CHEBI\:42820")
    assert "hits" in qres
    assert len(qres["hits"]) == 1
    assert qres["hits"][0]["_id"] == "ZRALSGWEFCBTJO-UHFFFAOYSA-N"


@pytest.mark.asyncio
async def test_query_chembl(async_chem_client: AsyncMyChemInfo):
    qres = await async_chem_client.query('chembl.smiles:"CC(=O)NO"')
    assert "hits" in qres
    assert len(qres["hits"]) == 1
    assert qres["hits"][0]["_id"] == "RRUDCFGSUDOHDG-UHFFFAOYSA-N"


@pytest.mark.asyncio
@pytest.mark.xfail
async def test_query_drugcentral(async_chem_client: AsyncMyChemInfo):
    qres = await async_chem_client.query(
        "drugcentral.drug_use.contraindication.umls_cui:C0023530", fields="drugcentral", size=50
    )
    assert "hits" in qres
    assert len(qres["hits"]) == 50

    # not working yet
    qres = await async_chem_client.query("drugcentral.xrefs.kegg_drug:D00220")
    assert "hits" in qres
    assert len(qres["hits"]) == 1
    assert qres["hits"][0]["_id"] == "ZRALSGWEFCBTJO-UHFFFAOYSA-N"


@pytest.mark.asyncio
async def test_query_pubchem(async_chem_client: AsyncMyChemInfo):
    qres = await async_chem_client.query("pubchem.molecular_formula:C2H5NO2", fields="pubchem", size=20)
    assert "hits" in qres
    assert len(qres["hits"]) == 20

    qres = await async_chem_client.query('pubchem.inchi:"InChI=1S/CH5N3/c2-1(3)4/h(H5,2,3,4)"')
    assert "hits" in qres
    assert len(qres["hits"]) == 1
    assert qres["hits"][0]["_id"] == "ZRALSGWEFCBTJO-UHFFFAOYSA-N"


@pytest.mark.asyncio
async def test_query_ginas(async_chem_client: AsyncMyChemInfo):
    qres = await async_chem_client.query("ginas.approvalID:JU58VJ6Y3B")
    assert "hits" in qres
    assert len(qres["hits"]) == 1
    assert qres["hits"][0]["_id"] == "ZRALSGWEFCBTJO-UHFFFAOYSA-N"


@pytest.mark.asyncio
async def test_query_pharmgkb(async_chem_client: AsyncMyChemInfo):
    qres = await async_chem_client.query("pharmgkb.id:PA164781028")
    assert "hits" in qres
    assert len(qres["hits"]) == 1
    assert qres["hits"][0]["_id"] == "ZRALSGWEFCBTJO-UHFFFAOYSA-N"


@pytest.mark.asyncio
async def test_query_ndc(async_chem_client: AsyncMyChemInfo):
    qres = await async_chem_client.query('ndc.productndc:"27437-051"')
    assert "hits" in qres
    assert len(qres["hits"]) == 1
    assert qres["hits"][0]["_id"] == "KPQZUUQMTUIKBP-UHFFFAOYSA-N"


@pytest.mark.asyncio
@pytest.mark.xfail
async def test_query_sider(async_chem_client: AsyncMyChemInfo):
    qres = await async_chem_client.query("sider.meddra.umls_id:C0232487", fields="sider", size=5)
    assert "hits" in qres
    assert len(qres["hits"]) == 5
    # Temp disable this check till we fix the data issue
    assert qres["hits"][0]["_id"] == "ZRALSGWEFCBTJO-UHFFFAOYSA-N"


@pytest.mark.asyncio
async def test_query_unii(async_chem_client: AsyncMyChemInfo):
    qres = await async_chem_client.query("unii.unii:JU58VJ6Y3B")
    assert "hits" in qres
    assert len(qres["hits"]) == 1
    assert qres["hits"][0]["_id"] == "ZRALSGWEFCBTJO-UHFFFAOYSA-N"


@pytest.mark.asyncio
async def test_query_aeolus(async_chem_client: AsyncMyChemInfo):
    qres = await async_chem_client.query("aeolus.rxcui:50675")
    assert "hits" in qres
    assert len(qres["hits"]) == 1
    assert qres["hits"][0]["_id"] == "ZRALSGWEFCBTJO-UHFFFAOYSA-N"


@pytest.mark.asyncio
async def test_query_fetch_all(async_chem_client: AsyncMyChemInfo):
    # fetch_all won't work when caching is used.
    # async_chem_client.stop_caching()
    q = "drugcentral.drug_use.contraindication.umls_cui:C0023530"
    qres = await async_chem_client.query(q, size=0)
    total = qres["total"]

    qres_generator = await async_chem_client.query(q, fields="drugcentral.drug_use", fetch_all=True)
    assert isinstance(qres_generator, types.AsyncGeneratorType)

    async_count = 0
    async for async_res in qres_generator:
        async_count += 1
    assert total == async_count


@pytest.mark.asyncio
async def test_querymany(async_chem_client: AsyncMyChemInfo):
    qres = await async_chem_client.querymany(
        ["ZRALSGWEFCBTJO-UHFFFAOYSA-N", "RRUDCFGSUDOHDG-UHFFFAOYSA-N"], verbose=False
    )
    assert len(qres) == 2

    qres = await async_chem_client.querymany("ZRALSGWEFCBTJO-UHFFFAOYSA-N,RRUDCFGSUDOHDG-UHFFFAOYSA-N", verbose=False)
    assert len(qres) == 2


@pytest.mark.asyncio
async def test_querymany_with_scopes(async_chem_client: AsyncMyChemInfo):
    qres = await async_chem_client.querymany(["CHEBI:31690", "CHEBI:15365"], scopes="chebi.id", verbose=False)
    assert len(qres) == 2

    qres = await async_chem_client.querymany(
        ["CHEMBL374515", "4RZ82L2GY5"], scopes="chembl.molecule_chembl_id,unii.unii", verbose=False
    )
    assert len(qres) >= 2


@pytest.mark.asyncio
async def test_querymany_fields(async_chem_client: AsyncMyChemInfo):
    qres1 = await async_chem_client.querymany(
        ["CHEBI:31690", "CHEBI:15365"],
        scopes="chebi.id",
        fields=["chebi.name", "unii.registry_number"],
        verbose=False,
    )
    assert len(qres1) == 2

    qres2 = await async_chem_client.querymany(
        ["CHEBI:31690", "CHEBI:15365"], scopes="chebi.id", fields="chebi.name,unii.registry_number", verbose=False
    )
    assert len(qres2) == 2

    assert descore(qres1) == descore(qres2)


@pytest.mark.asyncio
async def test_querymany_notfound(async_chem_client: AsyncMyChemInfo):
    qres = await async_chem_client.querymany(["CHEBI:31690", "CHEBI:15365", "NA_TEST"], scopes="chebi.id")
    assert len(qres) == 3
    assert qres[2] == {"query": "NA_TEST", "notfound": True}


@pytest.mark.asyncio
@pytest.mark.skipif(not biothings_client._PANDAS, reason="requires the pandas library")
async def test_querymany_dataframe(async_chem_client: AsyncMyChemInfo):
    from pandas import DataFrame

    query_list1 = [
        "QCYGXOCMWHSXSU-UHFFFAOYSA-N",
        "ADFOMBKCPIMCOO-BTVCFUMJSA-N",
        "DNUTZBZXLPWRJG-UHFFFAOYSA-N",
        "DROLRDZYPMOKLM-BIVLZKPYSA-N",
        "KPBZROQVTHLCDU-GOSISDBHSA-N",
        "UTUUIUQHGDRVPU-UHFFFAOYSA-K",
        "WZWDUEKBAIXVCC-IGHBBLSQSA-N",
        "IAJIIJBMBCZPSW-BDAKNGLRSA-N",
        "NASIOHFAYPRIAC-JTQLQIEISA-N",
        "VGWIQFDQAFSSKA-UHFFFAOYSA-N",
    ]

    qres = await async_chem_client.querymany(query_list1, scopes="_id", fields="pubchem", as_dataframe=True)
    assert isinstance(qres, DataFrame)
    assert "pubchem.inchi" in qres.columns
    assert set(query_list1) == set(qres.index)


@pytest.mark.asyncio
async def test_querymany_step(async_chem_client: AsyncMyChemInfo):
    query_list1 = [
        "QCYGXOCMWHSXSU-UHFFFAOYSA-N",
        "ADFOMBKCPIMCOO-BTVCFUMJSA-N",
        "DNUTZBZXLPWRJG-UHFFFAOYSA-N",
        "DROLRDZYPMOKLM-BIVLZKPYSA-N",
        "KPBZROQVTHLCDU-GOSISDBHSA-N",
        "UTUUIUQHGDRVPU-UHFFFAOYSA-K",
        "WZWDUEKBAIXVCC-IGHBBLSQSA-N",
        "IAJIIJBMBCZPSW-BDAKNGLRSA-N",
        "NASIOHFAYPRIAC-JTQLQIEISA-N",
        "VGWIQFDQAFSSKA-UHFFFAOYSA-N",
    ]

    qres1 = await async_chem_client.querymany(query_list1, scopes="_id", fields="pubchem")
    default_step = async_chem_client.step
    async_chem_client.step = 3
    qres2 = await async_chem_client.querymany(query_list1, scopes="_id", fields="pubchem")
    async_chem_client.step = default_step
    qres1 = descore(sorted(qres1, key=lambda doc: doc["_id"]))
    qres2 = descore(sorted(qres2, key=lambda doc: doc["_id"]))
    assert qres1 == qres2


@pytest.mark.asyncio
async def test_get_fields(async_chem_client: AsyncMyChemInfo):
    fields = await async_chem_client.get_fields()
    assert "chembl.inchi_key" in fields.keys()
    assert "pharmgkb.trade_names" in fields.keys()

    fields = await async_chem_client.get_fields("unii")
    assert "unii.molecular_formula" in fields.keys()
