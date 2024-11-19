import importlib.util
import os
import sys
import types
import unittest

sys.path.insert(0, os.path.split(os.path.split(os.path.abspath(__file__))[0])[0])

from biothings_client.utils.score import descore
import biothings_client


sys.stdout.write(
    '"biothings_client {0}" loaded from "{1}"\n'.format(biothings_client.__version__, biothings_client.__file__)
)


class TestGenesetClient(unittest.TestCase):
    def setUp(self):
        self.mgs = biothings_client.get_client("geneset")

    def test_metadata(self):
        meta = self.mgs.metadata()
        self.assertTrue("src" in meta)
        self.assertTrue("stats" in meta)
        self.assertTrue("total" in meta["stats"])

    def test_getgeneset(self):
        gs = self.mgs.getgeneset("WP100")
        self.assertEqual(gs["_id"], "WP100")
        self.assertEqual(gs["name"], "Glutathione metabolism")
        self.assertEqual(gs["source"], "wikipathways")
        self.assertEqual(gs["taxid"], "9606")
        self.assertGreaterEqual(len(gs["genes"]), 19)
        self.assertEqual(gs["count"], len(gs["genes"]))

        self.assertTrue("wikipathways" in gs)
        self.assertEqual(gs["wikipathways"]["id"], "WP100")
        self.assertEqual(gs["wikipathways"]["pathway_name"], "Glutathione metabolism")
        self.assertEqual(gs["wikipathways"]["url"], "https://www.wikipathways.org/instance/WP100")
        self.assertEqual(gs["wikipathways"]["_license"], "https://www.wikipathways.org/terms.html")

        self.assertTrue(any((gene.get("mygene_id") == "2937" and gene.get("symbol") == "GSS") for gene in gs["genes"]))

    def test_query_fetch_all(self):
        # pdb-->reactome
        # q=source:reactome
        # _exists_:pdb ---> source:reactome

        # fetch_all won't work when caching is used.
        self.mgs.stop_caching()
        qres = self.mgs.query("source:reactome")
        total = qres["total"]

        qres = self.mgs.query("source:reactome", fields="source,count,name", fetch_all=True)
        self.assertTrue(isinstance(qres, types.GeneratorType))
        self.assertEqual(total, len(list(qres)))

    def test_query_with_fields_as_list(self):
        qres1 = self.mgs.query("genes.ncbigene:1017", fields="name,source,taxid")
        qres2 = self.mgs.query("genes.ncbigene:1017", fields=["name", "source", "taxid"])
        self.assertTrue("hits" in qres1)
        self.assertEqual(len(qres1["hits"]), 10)
        self.assertEqual(descore(qres1["hits"]), descore(qres2["hits"]))

    def test_getgeneset_with_fields(self):
        gs = self.mgs.getgeneset("WP100", fields="name,source,taxid,genes.mygene_id,genes.symbol")

        self.assertTrue("_id" in gs)
        self.assertTrue("name" in gs)
        self.assertTrue("source" in gs)
        self.assertTrue("taxid" in gs)

        self.assertTrue(any((gene.get("mygene_id") == "2937" and gene.get("symbol") == "GSS") for gene in gs["genes"]))
        self.assertFalse(any(gene.get("name") for gene in gs["genes"]))

    def test_getgenesets(self):
        gs_li = self.mgs.getgenesets(["WP100", "WP101", "WP103"])

        self.assertEqual(len(gs_li), 3)
        self.assertEqual(gs_li[0]["_id"], "WP100")
        self.assertEqual(gs_li[1]["_id"], "WP101")
        self.assertEqual(gs_li[2]["_id"], "WP103")

    def test_query(self):
        qres = self.mgs.query("genes.mygene_id:2937", size=5)
        self.assertTrue("hits" in qres)
        self.assertEqual(len(qres["hits"]), 5)

    def test_query_default_fields(self):
        self.mgs.query(q="glucose")

    def test_query_field(self):
        self.mgs.query(q="genes.ncbigene:1017")

    def test_species_filter_plus_query(self):
        dog = self.mgs.query(q="glucose", species="9615")
        self.assertEqual(dog["hits"][0]["taxid"], "9615")

    def test_query_by_id(self):
        query = self.mgs.query(q="_id:WP100")
        self.assertEqual(query["hits"][0]["_id"], "WP100")

    def test_query_by_name(self):
        kinase = self.mgs.query(q="name:kinase")
        self.assertIn("kinase", kinase["hits"][0]["name"].lower())

    def test_query_by_description(self):
        desc = self.mgs.query(q="description:cytosine deamination")
        self.assertIn("cytosine", desc["hits"][0]["description"].lower())
        self.assertIn("deamination", desc["hits"][0]["description"].lower())

    def test_query_by_source_go(self):
        go = self.mgs.query(q="source:go", fields="all")
        self.assertIn("go", go["hits"][0].keys())
        self.assertEqual(go["hits"][0]["source"], "go")

    def test_query_by_source_ctd(self):
        ctd = self.mgs.query(q="source:ctd", fields="all")
        self.assertIn("ctd", ctd["hits"][0].keys())
        self.assertEqual(ctd["hits"][0]["source"], "ctd")

    def test_query_by_source_msigdb(self):
        msigdb = self.mgs.query(q="source:msigdb", fields="all")
        self.assertIn("msigdb", msigdb["hits"][0].keys())
        self.assertEqual(msigdb["hits"][0]["source"], "msigdb")

    @unittest.skip("We removed kegg data source for now")
    def test_query_by_source_kegg(self):
        kegg = self.mgs.query(q="source:kegg", fields="all")
        self.assertIn("kegg", kegg["hits"][0].keys())
        self.assertEqual(kegg["hits"][0]["source"], "kegg")

    def test_query_by_source_do(self):
        do = self.mgs.query(q="source:do", fields="all")
        self.assertIn("do", do["hits"][0].keys())
        self.assertEqual(do["hits"][0]["source"], "do")

    def test_query_by_source_reactome(self):
        reactome = self.mgs.query(q="source:reactome", fields="all")
        self.assertIn("reactome", reactome["hits"][0].keys())
        self.assertEqual(reactome["hits"][0]["source"], "reactome")

    def test_query_by_source_smpdb(self):
        smpdb = self.mgs.query(q="source:smpdb", fields="all")
        self.assertIn("smpdb", smpdb["hits"][0].keys())
        self.assertEqual(smpdb["hits"][0]["source"], "smpdb")
