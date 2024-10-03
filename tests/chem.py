import importlib.util
import os
import sys
import types
import unittest

sys.path.insert(0, os.path.split(os.path.split(os.path.abspath(__file__))[0])[0])

try:
    from utils import cache_request, descore
except ImportError:
    from tests.utils import descore, cache_request

import biothings_client

sys.stdout.write(
    '"biothings_client {0}" loaded from "{1}"\n'.format(biothings_client.__version__, biothings_client.__file__)
)

pandas_available = importlib.util.find_spec("pandas") is not None
requests_cache_available = importlib.util.find_spec("requests_cache") is not None


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
            ("57966", "CHEMBL.COMPOUND:57966", "chembl.molecule_chembl_id:57966"),
            (57966, "chembl.compound:57966", "chembl.molecule_chembl_id:57966"),
            (57966, "CheMBL.compOUND:57966", "chembl.molecule_chembl_id:57966"),
            ("120933777", "PUBCHEM.COMPOUND:120933777", "pubchem.cid:120933777"),
            (120933777, "pubchem.compound:120933777", "pubchem.cid:120933777"),
            ("120933777", "PuBcHEm.COMPound:120933777", "pubchem.cid:120933777"),
            (57966, "CHEBI:57966", "chebi.id:57966"),
            ("57966", "chebi:57966", "chebi.id:57966"),
            (57966, "CheBi:57966", "chebi.id:57966"),
            ("11P2JDE17B", "UNII:11P2JDE17B", "unii.unii:11P2JDE17B"),
            ("11P2JDE17B", "unii:11P2JDE17B", "unii.unii:11P2JDE17B"),
            ("11P2JDE17B", "uNIi:11P2JDE17B", "unii.unii:11P2JDE17B"),
            ("dB03107", "DRUGBANK:dB03107", "drugbank.id:dB03107"),
            ("dB03107", "drugbank:dB03107", "drugbank.id:dB03107"),
            ("dB03107", "DrugBaNK:dB03107", "drugbank.id:dB03107"),
        ]

        results_aggregation = []
        for id_query, biothings_query, biolink_query in curie_id_testing_collection:
            id_query_result = self.mc.getchem(_id=id_query)
            biothings_term_query_result = self.mc.getchem(_id=biothings_query)
            biolink_term_query_result = self.mc.getchem(_id=biolink_query)
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

        self.assertTrue(all(results_validation), msg="\n".join(failure_messages))

    def test_multiple_curie_id_query(self):
        """
        Tests the annotations endpoint support for the biolink CURIE ID.

        Batch query testing against the POST endpoint to verify that the CURIE ID can work with
        multiple

        If support is enabled then we should retrieve the exact same document for all the provided
        queries
        """
        curie_id_testing_collection = [
            ("57966", "CHEMBL.COMPOUND:57966", "chembl.molecule_chembl_id:57966"),
            (57966, "chembl.compound:57966", "chembl.molecule_chembl_id:57966"),
            (57966, "CheMBL.compOUND:57966", "chembl.molecule_chembl_id:57966"),
            ("120933777", "PUBCHEM.COMPOUND:120933777", "pubchem.cid:120933777"),
            (120933777, "pubchem.compound:120933777", "pubchem.cid:120933777"),
            ("120933777", "PuBcHEm.COMPound:120933777", "pubchem.cid:120933777"),
            (57966, "CHEBI:57966", "chebi.id:57966"),
            ("57966", "chebi:57966", "chebi.id:57966"),
            (57966, "CheBi:57966", "chebi.id:57966"),
            ("11P2JDE17B", "UNII:11P2JDE17B", "unii.unii:11P2JDE17B"),
            ("11P2JDE17B", "unii:11P2JDE17B", "unii.unii:11P2JDE17B"),
            ("11P2JDE17B", "uNIi:11P2JDE17B", "unii.unii:11P2JDE17B"),
            ("dB03107", "DRUGBANK:dB03107", "drugbank.id:dB03107"),
            ("dB03107", "drugbank:dB03107", "drugbank.id:dB03107"),
            ("dB03107", "DrugBaNK:dB03107", "drugbank.id:dB03107"),
        ]

        results_aggregation = []
        for id_query, biothings_query, biolink_query in curie_id_testing_collection:
            base_result = self.mc.getchem(_id=id_query)

            batch_query = [id_query, biothings_query, biolink_query]
            query_results = self.mc.getchems(ids=batch_query)
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

        self.assertTrue(all(results_validation), msg="\n".join(failure_messages))

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

    @unittest.skipIf(not requests_cache_available, "requests_cache not available")
    def test_caching(self):
        def _getchem():
            return self.mc.getchem("ZRALSGWEFCBTJO-UHFFFAOYSA-N")

        def _getdrugs():
            return self.mc.getdrugs(["ZRALSGWEFCBTJO-UHFFFAOYSA-N", "RRUDCFGSUDOHDG-UHFFFAOYSA-N"])

        def _query():
            return self.mc.query("chebi.name:albendazole", size=5)

        def _querymany():
            return self.mc.querymany(["CHEBI:31690", "CHEBI:15365"], scopes="chebi.id")

        try:
            from_cache, pre_cache_r = cache_request(_getchem)
            self.assertFalse(from_cache)

            cache_name = "mcc"
            cache_file = cache_name + ".sqlite"

            if os.path.exists(cache_file):
                os.remove(cache_file)
            self.mc.set_caching(cache_name)

            # populate cache
            from_cache, cache_fill_r = cache_request(_getchem)
            self.assertTrue(os.path.exists(cache_file))
            self.assertFalse(from_cache)
            # is it from the cache?
            from_cache, cached_r = cache_request(_getchem)
            self.assertTrue(from_cache)

            self.mc.stop_caching()
            # same query should be live - not cached
            from_cache, post_cache_r = cache_request(_getchem)
            self.assertFalse(from_cache)

            self.mc.set_caching(cache_name)

            # same query should still be sourced from cache
            from_cache, recached_r = cache_request(_getchem)
            self.assertTrue(from_cache)

            self.mc.clear_cache()
            # cache was cleared, same query should be live
            from_cache, clear_cached_r = cache_request(_getchem)
            self.assertFalse(from_cache)

            # all requests should be identical except the _score, which can vary slightly
            for x in [pre_cache_r, cache_fill_r, cached_r, post_cache_r, recached_r, clear_cached_r]:
                x.pop("_score", None)

            self.assertTrue(
                all(
                    [
                        x == pre_cache_r
                        for x in [pre_cache_r, cache_fill_r, cached_r, post_cache_r, recached_r, clear_cached_r]
                    ]
                )
            )

            # test getvariants POST caching
            from_cache, first_getgenes_r = cache_request(_getdrugs)
            del first_getgenes_r
            self.assertFalse(from_cache)
            # should be from cache this time
            from_cache, second_getgenes_r = cache_request(_getdrugs)
            del second_getgenes_r
            self.assertTrue(from_cache)

            # test query GET caching
            from_cache, first_query_r = cache_request(_query)
            del first_query_r
            self.assertFalse(from_cache)
            # should be from cache this time
            from_cache, second_query_r = cache_request(_query)
            del second_query_r
            self.assertTrue(from_cache)

            # test querymany POST caching
            from_cache, first_querymany_r = cache_request(_querymany)
            del first_querymany_r
            self.assertFalse(from_cache)
            # should be from cache this time
            from_cache, second_querymany_r = cache_request(_querymany)
            del second_querymany_r
            self.assertTrue(from_cache)

        finally:
            self.mc.stop_caching()
            if os.path.exists(cache_file):
                os.remove(cache_file)


def suite():
    return unittest.defaultTestLoader.loadTestsFromTestCase(TestChemClient)


if __name__ == "__main__":
    unittest.TextTestRunner().run(suite())
