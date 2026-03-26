from typing import Any, Dict, List, Union


def descore(
    hit: Union[Dict[str, Any], List[Dict[str, Any]]],
) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
    """
    Pops the _score from a hit or hit list - _score can vary slightly between runs causing
    tests to fail.
    """
    if isinstance(hit, list):
        res = []
        for o in hit:
            o.pop("_score", None)
            res.append(o)
        return res
    else:
        hit.pop("_score", None)
        return hit
