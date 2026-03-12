"""Gene specific utils."""

from collections import OrderedDict
from typing import Any, Dict, Iterable, List, Protocol, Union, cast

from biothings_client import get_client


class _GeneClient(Protocol):
    def getgenes(
        self, gene_list: Iterable[Union[str, int]], **kwargs: Any
    ) -> List[Dict[str, Any]]: ...


def get_homologs(
    gene_list: Iterable[Union[str, int]],
    fields: Union[str, Iterable[str]] = "all",
    species: str = "all",
) -> List[Dict[str, Any]]:
    """Return the gene-objects for homologs in species for each gene in the input *gene_list*."""
    gene_client = cast(_GeneClient, get_client("gene"))
    clean_species = [int(s) for s in species.split(",")] if species != "all" else []
    initial: "OrderedDict[str, Dict[int, List[Union[str, int]]]]" = OrderedDict()
    qset = set()

    for gene in gene_client.getgenes(gene_list, fields="homologene", species="all"):
        if gene["_id"] in initial:
            continue
        initial[gene["_id"]] = {}
        for taxid, geneid in gene.get("homologene", {}).get("genes", []):
            if not clean_species or taxid in clean_species:
                initial[gene["_id"]].setdefault(taxid, []).append(geneid)
                qset.add(geneid)
    gene_dict = {
        g["_id"]: g
        for g in gene_client.getgenes(iter(qset), fields=fields, species="all")
    }

    ret: List[Dict[str, Any]] = []
    for geneid, homolog_dict in initial.items():
        _ret: Dict[str, Any] = {"gene": geneid, "homologs": []}
        for taxid, glist in homolog_dict.items():
            _d: Dict[str, Any] = {"taxid": taxid, "genes": []}
            for g in glist:
                if str(g) in gene_dict:
                    _d["genes"].append(gene_dict[str(g)])
            if len(_d["genes"]) > 0:
                _ret["homologs"].append(_d)
        ret.append(_ret)

    return ret
