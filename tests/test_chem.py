import importlib.util
import logging
import json
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

pandas_available = importlib.util.find_spec("pandas") is not None


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class TestChemClient(unittest.TestCase):
    def setUp(self):
        self.mc = biothings_client.get_client("chem")
        self.query_list1 = [
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

    def test_metadata(self):
        meta = self.mc.metadata()
        self.assertTrue("src" in meta)
        self.assertTrue("stats" in meta)
        self.assertTrue("total" in meta["stats"])

    def test_getchem(self):
        c = self.mc.getchem("ZRALSGWEFCBTJO-UHFFFAOYSA-N")
        self.assertEqual(c["_id"], "ZRALSGWEFCBTJO-UHFFFAOYSA-N")
        self.assertEqual(c["chebi"]["name"], "guanidine")

    def test_getchem_with_fields(self):
        c = self.mc.getchem("7AXV542LZ4", fields="chebi.name,chembl.inchi_key,pubchem.cid")
        self.assertTrue("_id" in c)
        self.assertTrue("chebi" in c)
        self.assertTrue("name" in c["chebi"])
        self.assertTrue("chembl" in c)
        self.assertTrue("inchi_key" in c["chembl"])
        self.assertTrue("pubchem" in c)
        self.assertTrue("cid" in c["pubchem"])

    def test_curie_id_query(self):
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
                query_result = self.mc.getchem(_id=similar_query)
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

    def test_multiple_curie_id_query(self):
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
            base_result = self.mc.getchem(_id=query_collection[0])
            query_results = self.mc.getchems(ids=query_collection)
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

    @unittest.expectedFailure
    def get_getdrug(self):
        c = self.mc.getdrug("CHEMBL1308")
        self.assertEqual(c["_id"], "ZRALSGWEFCBTJO-UHFFFAOYSA-N")
        c = self.mc.getdrug("7AXV542LZ4")
        self.assertEqual(c["_id"], "ZRALSGWEFCBTJO-UHFFFAOYSA-N")
        c = self.mc.getdrug("CHEBI:6431")
        self.assertEqual(c["_id"], "ZRALSGWEFCBTJO-UHFFFAOYSA-N")

        # PubChem CID
        # not working yet
        c = self.mc.getdrug("CID:1990")
        self.assertEqual(c["_id"], "ZRALSGWEFCBTJO-UHFFFAOYSA-N")
        c = self.mc.getdrug("1990")
        self.assertEqual(c["_id"], "ZRALSGWEFCBTJO-UHFFFAOYSA-N")

    def test_getchems(self):
        c_li = self.mc.getchems(
            ["KTUFNOKKBVMGRW-UHFFFAOYSA-N", "HXHWSAZORRCQMX-UHFFFAOYSA-N", "DQMZLTXERSFNPB-UHFFFAOYSA-N"]
        )
        self.assertEqual(len(c_li), 3)
        self.assertEqual(c_li[0]["_id"], "KTUFNOKKBVMGRW-UHFFFAOYSA-N")
        self.assertEqual(c_li[1]["_id"], "HXHWSAZORRCQMX-UHFFFAOYSA-N")
        self.assertEqual(c_li[2]["_id"], "DQMZLTXERSFNPB-UHFFFAOYSA-N")

    def test_query(self):
        qres = self.mc.query("chebi.name:albendazole", size=5)
        self.assertTrue("hits" in qres)
        self.assertEqual(len(qres["hits"]), 5)

    @unittest.skip("Drugbank was removed")
    def test_query_drugbank(self):
        qres = self.mc.query("drugbank.id:DB00536")
        self.assertTrue("hits" in qres)
        self.assertEqual(len(qres["hits"]), 1)
        self.assertEqual(qres["hits"][0]["_id"], "ZRALSGWEFCBTJO-UHFFFAOYSA-N")

    def test_query_chebi(self):
        qres = self.mc.query(r"chebi.id:CHEBI\:42820")
        self.assertTrue("hits" in qres)
        self.assertEqual(len(qres["hits"]), 1)
        self.assertEqual(qres["hits"][0]["_id"], "ZRALSGWEFCBTJO-UHFFFAOYSA-N")

    def test_query_chembl(self):
        qres = self.mc.query('chembl.smiles:"CC(=O)NO"')
        self.assertTrue("hits" in qres)
        self.assertEqual(len(qres["hits"]), 1)
        self.assertEqual(qres["hits"][0]["_id"], "RRUDCFGSUDOHDG-UHFFFAOYSA-N")

    @unittest.expectedFailure
    def test_query_drugcentral(self):
        qres = self.mc.query("drugcentral.drug_use.contraindication.umls_cui:C0023530", fields="drugcentral", size=50)
        self.assertTrue("hits" in qres)
        self.assertEqual(len(qres["hits"]), 50)

        # not working yet
        qres = self.mc.query("drugcentral.xrefs.kegg_drug:D00220")
        self.assertTrue("hits" in qres)
        self.assertEqual(len(qres["hits"]), 1)
        self.assertEqual(qres["hits"][0]["_id"], "ZRALSGWEFCBTJO-UHFFFAOYSA-N")

    def test_query_pubchem(self):
        qres = self.mc.query("pubchem.molecular_formula:C2H5NO2", fields="pubchem", size=20)
        self.assertTrue("hits" in qres)
        self.assertEqual(len(qres["hits"]), 20)

        qres = self.mc.query('pubchem.inchi:"InChI=1S/CH5N3/c2-1(3)4/h(H5,2,3,4)"')
        self.assertTrue("hits" in qres)
        self.assertEqual(len(qres["hits"]), 1)
        self.assertEqual(qres["hits"][0]["_id"], "ZRALSGWEFCBTJO-UHFFFAOYSA-N")

    def test_query_ginas(self):
        qres = self.mc.query("ginas.approvalID:JU58VJ6Y3B")
        self.assertTrue("hits" in qres)
        self.assertEqual(len(qres["hits"]), 1)
        self.assertEqual(qres["hits"][0]["_id"], "ZRALSGWEFCBTJO-UHFFFAOYSA-N")

    def test_query_pharmgkb(self):
        qres = self.mc.query("pharmgkb.id:PA164781028")
        self.assertTrue("hits" in qres)
        self.assertEqual(len(qres["hits"]), 1)
        self.assertEqual(qres["hits"][0]["_id"], "ZRALSGWEFCBTJO-UHFFFAOYSA-N")

    def test_query_ndc(self):
        qres = self.mc.query('ndc.productndc:"27437-051"')
        self.assertTrue("hits" in qres)
        self.assertEqual(len(qres["hits"]), 1)
        self.assertEqual(qres["hits"][0]["_id"], "KPQZUUQMTUIKBP-UHFFFAOYSA-N")

    @unittest.expectedFailure
    def test_query_sider(self):
        qres = self.mc.query("sider.meddra.umls_id:C0232487", fields="sider", size=5)
        self.assertTrue("hits" in qres)
        self.assertEqual(len(qres["hits"]), 5)
        # Temp disable this check till we fix the data issue
        self.assertEqual(qres["hits"][0]["_id"], "ZRALSGWEFCBTJO-UHFFFAOYSA-N")

    def test_query_unii(self):
        qres = self.mc.query("unii.unii:JU58VJ6Y3B")
        self.assertTrue("hits" in qres)
        self.assertEqual(len(qres["hits"]), 1)
        self.assertEqual(qres["hits"][0]["_id"], "ZRALSGWEFCBTJO-UHFFFAOYSA-N")

    def test_query_aeolus(self):
        qres = self.mc.query("aeolus.rxcui:50675")
        self.assertTrue("hits" in qres)
        self.assertEqual(len(qres["hits"]), 1)
        self.assertEqual(qres["hits"][0]["_id"], "ZRALSGWEFCBTJO-UHFFFAOYSA-N")

    def test_query_fetch_all(self):
        # fetch_all won't work when caching is used.
        self.mc.stop_caching()
        q = "drugcentral.drug_use.contraindication.umls_cui:C0023530"
        qres = self.mc.query(q, size=0)
        total = qres["total"]

        qres = self.mc.query(q, fields="drugcentral.drug_use", fetch_all=True)
        self.assertTrue(isinstance(qres, types.GeneratorType))
        self.assertEqual(total, len(list(qres)))

    def test_querymany(self):
        qres = self.mc.querymany(["ZRALSGWEFCBTJO-UHFFFAOYSA-N", "RRUDCFGSUDOHDG-UHFFFAOYSA-N"], verbose=False)
        self.assertEqual(len(qres), 2)

        qres = self.mc.querymany("ZRALSGWEFCBTJO-UHFFFAOYSA-N,RRUDCFGSUDOHDG-UHFFFAOYSA-N", verbose=False)
        self.assertEqual(len(qres), 2)

    def test_querymany_with_scopes(self):
        qres = self.mc.querymany(["CHEBI:31690", "CHEBI:15365"], scopes="chebi.id", verbose=False)
        self.assertEqual(len(qres), 2)

        qres = self.mc.querymany(
            ["CHEMBL374515", "4RZ82L2GY5"], scopes="chembl.molecule_chembl_id,unii.unii", verbose=False
        )
        self.assertTrue(len(qres) >= 2)

    def test_querymany_fields(self):
        qres1 = self.mc.querymany(
            ["CHEBI:31690", "CHEBI:15365"],
            scopes="chebi.id",
            fields=["chebi.name", "unii.registry_number"],
            verbose=False,
        )
        self.assertEqual(len(qres1), 2)

        qres2 = self.mc.querymany(
            ["CHEBI:31690", "CHEBI:15365"], scopes="chebi.id", fields="chebi.name,unii.registry_number", verbose=False
        )
        self.assertEqual(len(qres2), 2)

        self.assertEqual(descore(qres1), descore(qres2))

    def test_querymany_notfound(self):
        qres = self.mc.querymany(["CHEBI:31690", "CHEBI:15365", "NA_TEST"], scopes="chebi.id")
        self.assertEqual(len(qres), 3)
        self.assertEqual(qres[2], {"query": "NA_TEST", "notfound": True})

    @unittest.skipIf(not pandas_available, "pandas not available")
    def test_querymany_dataframe(self):
        from pandas import DataFrame

        qres = self.mc.querymany(self.query_list1, scopes="_id", fields="pubchem", as_dataframe=True)
        self.assertTrue(isinstance(qres, DataFrame))
        self.assertTrue("pubchem.inchi" in qres.columns)
        self.assertEqual(set(self.query_list1), set(qres.index))

    def test_querymany_step(self):
        qres1 = self.mc.querymany(self.query_list1, scopes="_id", fields="pubchem")
        default_step = self.mc.step
        self.mc.step = 3
        qres2 = self.mc.querymany(self.query_list1, scopes="_id", fields="pubchem")
        self.mc.step = default_step
        qres1 = descore(sorted(qres1, key=lambda doc: doc["_id"]))
        qres2 = descore(sorted(qres2, key=lambda doc: doc["_id"]))
        self.assertEqual(qres1, qres2)

    def test_get_fields(self):
        fields = self.mc.get_fields()
        self.assertTrue("chembl.inchi_key" in fields.keys())
        self.assertTrue("pharmgkb.trade_names" in fields.keys())

        fields = self.mc.get_fields("unii")
        self.assertTrue("unii.molecular_formula" in fields.keys())
