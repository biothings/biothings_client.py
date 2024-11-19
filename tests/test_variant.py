import importlib.util
import os
import sys
import types
import unittest

sys.path.insert(0, os.path.split(os.path.split(os.path.abspath(__file__))[0])[0])

from biothings_client.utils.score import descore
import biothings_client


sys.stderr.write(
    '"biothings_client {0}" loaded from "{1}"\n'.format(biothings_client.__version__, biothings_client.__file__)
)

pandas_available = importlib.util.find_spec("pandas") is not None


class TestVariantClient(unittest.TestCase):
    def setUp(self):
        self.mv = biothings_client.get_client("variant")
        self.query_list1 = [
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
        self.query_list2 = [
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

    def test_format_hgvs(self):
        self.assertEqual(self.mv.format_hgvs("1", 35366, "C", "T"), "chr1:g.35366C>T")
        self.assertEqual(self.mv.format_hgvs("chr2", 17142, "G", "GA"), "chr2:g.17142_17143insA")
        self.assertEqual(self.mv.format_hgvs("1", 10019, "TA", "T"), "chr1:g.10020del")
        self.assertEqual(self.mv.format_hgvs("MT", 8270, "CACCCCCTCT", "C"), "chrMT:g.8271_8279del")
        self.assertEqual(self.mv.format_hgvs("7", 15903, "G", "GC"), "chr7:g.15903_15904insC")
        self.assertEqual(self.mv.format_hgvs("X", 107930849, "GGA", "C"), "chrX:g.107930849_107930851delinsC")
        self.assertEqual(self.mv.format_hgvs("20", 1234567, "GTC", "GTCT"), "chr20:g.1234569_1234570insT")

    def test_metadata(self):
        meta = self.mv.metadata()
        self.assertTrue("stats" in meta)
        self.assertTrue("total" in meta["stats"])

    def test_getvariant(self):
        v = self.mv.getvariant("chr9:g.107620835G>A")
        self.assertEqual(v["_id"], "chr9:g.107620835G>A")
        self.assertEqual(v["snpeff"]["ann"]["genename"], "ABCA1")

        v = self.mv.getvariant("'chr1:g.1A>C'")  # something does not exist
        self.assertEqual(v, None)

    def test_getvariant_with_fields(self):
        v = self.mv.getvariant("chr9:g.107620835G>A", fields="dbnsfp,cadd,cosmic")
        self.assertTrue("_id" in v)
        self.assertTrue("dbnsfp" in v)
        self.assertTrue("cadd" in v)
        self.assertTrue("cosmic" in v)

    def test_getvariants(self):
        v_li = self.mv.getvariants(self.query_list1)
        self.assertEqual(len(v_li), 9)
        self.assertEqual(v_li[0]["_id"], self.query_list1[0])
        self.assertEqual(v_li[1]["_id"], self.query_list1[1])
        self.assertEqual(v_li[2]["_id"], self.query_list1[2])

        self.mv.step = 4
        # test input is a string of comma-separated ids
        v_li2 = self.mv.getvariants(",".join(self.query_list1))
        self.assertEqual(v_li, v_li2)
        # test input is a tuple
        v_li2 = self.mv.getvariants(tuple(self.query_list1))
        self.assertEqual(v_li, v_li2)

        # test input is a generator
        def _input(li):
            for x in li:
                yield x

        v_li2 = self.mv.getvariants(_input(self.query_list1))
        self.assertEqual(v_li, v_li2)
        self.mv.step = 1000

    def test_query(self):
        qres = self.mv.query("dbnsfp.genename:cdk2", size=5)
        self.assertTrue("hits" in qres)
        self.assertEqual(len(qres["hits"]), 5)

    def test_query_hgvs(self):
        qres = self.mv.query('"NM_000048.4:c.566A>G"', size=5)
        # should match clinvar.hgvs.coding field from variant "chr7:g.65551772A>G"
        # sometime we need to update ".4" part if clinvar data updated.
        self.assertTrue("hits" in qres)
        self.assertEqual(len(qres["hits"]), 1)

    def test_query_rsid(self):
        qres = self.mv.query("dbsnp.rsid:rs58991260")
        self.assertTrue("hits" in qres)
        self.assertEqual(len(qres["hits"]), 1)
        self.assertEqual(qres["hits"][0]["_id"], "chr1:g.218631822G>A")
        qres2 = self.mv.query("rs58991260")
        # exclude _score field before comparison
        qres["hits"][0].pop("_score")
        qres2["hits"][0].pop("_score")
        self.assertEqual(qres["hits"], qres2["hits"])

    def test_query_symbol(self):
        qres = self.mv.query("snpeff.ann.genename:cdk2")
        self.assertTrue("hits" in qres)
        self.assertTrue(qres["total"] > 5000)
        self.assertEqual(qres["hits"][0]["snpeff"]["ann"][0]["genename"], "CDK2")

    def test_query_genomic_range(self):
        qres = self.mv.query("chr1:69000-70000")
        self.assertTrue("hits" in qres)
        self.assertTrue(qres["total"] >= 3)

    def test_query_fetch_all(self):
        # fetch_all won't work when caching is used.
        self.mv.stop_caching()
        qres = self.mv.query("chr1:69500-70000", fields="chrom")
        total = qres["total"]

        qres = self.mv.query("chr1:69500-70000", fields="chrom", fetch_all=True)
        self.assertTrue(isinstance(qres, types.GeneratorType))
        self.assertEqual(total, len(list(qres)))

    def test_querymany(self):
        qres = self.mv.querymany(self.query_list1, verbose=False)
        self.assertEqual(len(qres), 9)

        self.mv.step = 4
        # test input as a string
        qres2 = self.mv.querymany(",".join(self.query_list1), verbose=False)
        self.assertEqual(qres, qres2)
        # test input as a tuple
        qres2 = self.mv.querymany(tuple(self.query_list1), verbose=False)
        self.assertEqual(qres, qres2)
        # test input as a iterator
        qres2 = self.mv.querymany(iter(self.query_list1), verbose=False)
        self.assertEqual(qres, qres2)
        self.mv.step = 1000

    def test_querymany_with_scopes(self):
        qres = self.mv.querymany(["rs58991260", "rs2500"], scopes="dbsnp.rsid", verbose=False)
        self.assertEqual(len(qres), 2)

        qres = self.mv.querymany(
            ["RCV000083620", "RCV000083611", "RCV000083584"], scopes="clinvar.rcv_accession", verbose=False
        )
        self.assertEqual(len(qres), 3)

        qres = self.mv.querymany(
            ["rs2500", "RCV000083611", "COSM1392449"],
            scopes="clinvar.rcv_accession,dbsnp.rsid,cosmic.cosmic_id",
            verbose=False,
        )
        self.assertEqual(len(qres), 3)

    def test_querymany_fields(self):
        ids = ["COSM1362966", "COSM990046", "COSM1392449"]
        qres1 = self.mv.querymany(
            ids, scopes="cosmic.cosmic_id", fields=["cosmic.tumor_site", "cosmic.cosmic_id"], verbose=False
        )
        self.assertEqual(len(qres1), 3)

        qres2 = self.mv.querymany(
            ids, scopes="cosmic.cosmic_id", fields="cosmic.tumor_site,cosmic.cosmic_id", verbose=False
        )
        self.assertEqual(len(qres2), 3)

        self.assertEqual(descore(qres1), descore(qres2))

    def test_querymany_notfound(self):
        qres = self.mv.querymany(["rs58991260", "rs2500", "NA_TEST"], scopes="dbsnp.rsid", verbose=False)
        self.assertEqual(len(qres), 3)
        self.assertEqual(qres[2], {"query": "NA_TEST", "notfound": True})

    @unittest.skipIf(not pandas_available, "pandas not available")
    def test_querymany_dataframe(self):
        from pandas import DataFrame

        qres = self.mv.querymany(
            self.query_list2, scopes="dbsnp.rsid", fields="dbsnp", as_dataframe=True, verbose=False
        )
        self.assertTrue(isinstance(qres, DataFrame))
        self.assertTrue("dbsnp.vartype" in qres.columns)
        self.assertEqual(set(self.query_list2), set(qres.index))

    def test_querymany_step(self):
        qres1 = self.mv.querymany(self.query_list2, scopes="dbsnp.rsid", fields="dbsnp.rsid", verbose=False)
        default_step = self.mv.step
        self.mv.step = 3
        qres2 = self.mv.querymany(self.query_list2, scopes="dbsnp.rsid", fields="dbsnp.rsid", verbose=False)
        self.mv.step = default_step
        # self.assertEqual(qres1, qres2, (qres1, qres2))
        self.assertEqual(descore(qres1), descore(qres2))

    def test_get_fields(self):
        fields = self.mv.get_fields()
        self.assertTrue("dbsnp.chrom" in fields.keys())
        self.assertTrue("clinvar.chrom" in fields.keys())
