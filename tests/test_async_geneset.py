"""
Mirror of the geneset tests but two main differences:
> asynchronous
> implemented in pytest for asyncio marker
"""

import logging
import types

import pytest


from biothings_client.client.definitions import AsyncMyGenesetInfo
from biothings_client.utils.score import descore


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


@pytest.mark.asyncio
async def test_metadata(async_geneset_client: AsyncMyGenesetInfo):
    meta = await async_geneset_client.metadata()
    assert "src" in meta
    assert "stats" in meta
    assert "total" in meta["stats"]


@pytest.mark.asyncio
async def test_getgeneset(async_geneset_client: AsyncMyGenesetInfo):
    gs = await async_geneset_client.getgeneset("WP100")
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


@pytest.mark.asyncio
async def test_query_fetch_all(async_geneset_client: AsyncMyGenesetInfo):
    # pdb-->reactome
    # q=source:reactome
    # _exists_:pdb ---> source:reactome

    # fetch_all won't work when caching is used.
    # await async_geneset_client.stop_caching()
    qres = await async_geneset_client.query("source:reactome")
    total = qres["total"]

    qres_generator = await async_geneset_client.query("source:reactome", fields="source,count,name", fetch_all=True)
    assert isinstance(qres_generator, types.AsyncGeneratorType)

    async_count = 0
    async for async_res in qres_generator:
        async_count += 1
    assert total == async_count


@pytest.mark.asyncio
async def test_query_with_fields_as_list(async_geneset_client: AsyncMyGenesetInfo):
    qres1 = await async_geneset_client.query("genes.ncbigene:1017", fields="name,source,taxid")
    qres2 = await async_geneset_client.query("genes.ncbigene:1017", fields=["name", "source", "taxid"])
    assert "hits" in qres1
    assert len(qres1["hits"]) == 10
    assert descore(qres1["hits"]) == descore(qres2["hits"])


@pytest.mark.asyncio
async def test_getgeneset_with_fields(async_geneset_client: AsyncMyGenesetInfo):
    gs = await async_geneset_client.getgeneset("WP100", fields="name,source,taxid,genes.mygene_id,genes.symbol")

    assert "_id" in gs
    assert "name" in gs
    assert "source" in gs
    assert "taxid" in gs

    assert any((gene.get("mygene_id") == "2937" and gene.get("symbol") == "GSS") for gene in gs["genes"])
    assert not any(gene.get("name") for gene in gs["genes"])


@pytest.mark.asyncio
async def test_getgenesets(async_geneset_client: AsyncMyGenesetInfo):
    gs_li = await async_geneset_client.getgenesets(["WP100", "WP101", "WP103"])

    assert len(gs_li) == 3
    assert gs_li[0]["_id"] == "WP100"
    assert gs_li[1]["_id"] == "WP101"
    assert gs_li[2]["_id"] == "WP103"


@pytest.mark.asyncio
async def test_query(async_geneset_client: AsyncMyGenesetInfo):
    qres = await async_geneset_client.query("genes.mygene_id:2937", size=5)
    assert "hits" in qres
    assert len(qres["hits"]) == 5


@pytest.mark.asyncio
async def test_query_default_fields(async_geneset_client: AsyncMyGenesetInfo):
    await async_geneset_client.query(q="glucose")


@pytest.mark.asyncio
async def test_query_field(async_geneset_client: AsyncMyGenesetInfo):
    await async_geneset_client.query(q="genes.ncbigene:1017")


@pytest.mark.asyncio
async def test_species_filter_plus_query(async_geneset_client: AsyncMyGenesetInfo):
    dog = await async_geneset_client.query(q="glucose", species="9615")
    assert dog["hits"][0]["taxid"] == "9615"


@pytest.mark.asyncio
async def test_query_by_id(async_geneset_client: AsyncMyGenesetInfo):
    query = await async_geneset_client.query(q="_id:WP100")
    assert query["hits"][0]["_id"] == "WP100"


@pytest.mark.asyncio
async def test_query_by_name(async_geneset_client: AsyncMyGenesetInfo):
    kinase = await async_geneset_client.query(q="name:kinase")
    assert "kinase" in kinase["hits"][0]["name"].lower()


@pytest.mark.asyncio
async def test_query_by_description(async_geneset_client: AsyncMyGenesetInfo):
    desc = await async_geneset_client.query(q="description:cytosine deamination")
    assert "cytosine" in desc["hits"][0]["description"].lower()
    assert "deamination" in desc["hits"][0]["description"].lower()


@pytest.mark.asyncio
async def test_query_by_source_go(async_geneset_client: AsyncMyGenesetInfo):
    go = await async_geneset_client.query(q="source:go", fields="all")
    assert "go" in go["hits"][0].keys()
    assert go["hits"][0]["source"] == "go"


@pytest.mark.asyncio
async def test_query_by_source_ctd(async_geneset_client: AsyncMyGenesetInfo):
    ctd = await async_geneset_client.query(q="source:ctd", fields="all")
    assert "ctd" in ctd["hits"][0].keys()
    assert ctd["hits"][0]["source"] == "ctd"


@pytest.mark.asyncio
async def test_query_by_source_msigdb(async_geneset_client: AsyncMyGenesetInfo):
    msigdb = await async_geneset_client.query(q="source:msigdb", fields="all")
    assert "msigdb" in msigdb["hits"][0].keys()
    assert msigdb["hits"][0]["source"] == "msigdb"


@pytest.mark.skip(reason="We removed kegg data source for now")
@pytest.mark.asyncio
async def test_query_by_source_kegg(async_geneset_client: AsyncMyGenesetInfo):
    kegg = await async_geneset_client.query(q="source:kegg", fields="all")
    assert "kegg" in kegg["hits"][0].keys()
    assert kegg["hits"][0]["source"] == "kegg"


@pytest.mark.asyncio
async def test_query_by_source_do(async_geneset_client: AsyncMyGenesetInfo):
    do = await async_geneset_client.query(q="source:do", fields="all")
    assert "do" in do["hits"][0].keys()
    assert do["hits"][0]["source"] == "do"


@pytest.mark.asyncio
async def test_query_by_source_reactome(async_geneset_client: AsyncMyGenesetInfo):
    reactome = await async_geneset_client.query(q="source:reactome", fields="all")
    assert "reactome" in reactome["hits"][0].keys()
    assert reactome["hits"][0]["source"] == "reactome"


@pytest.mark.asyncio
async def test_query_by_source_smpdb(async_geneset_client: AsyncMyGenesetInfo):
    smpdb = await async_geneset_client.query(q="source:smpdb", fields="all")
    assert "smpdb" in smpdb["hits"][0].keys()
    assert smpdb["hits"][0]["source"] == "smpdb"
