from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple, cast

from pyld import jsonld  # type: ignore


def nquads_transform(doc: Dict[str, Any]) -> List[Dict[str, Any]]:
    t = jsonld.JsonLdProcessor()
    nquads = t.parse_nquads(jsonld.to_rdf(doc, {"format": "application/nquads"}))[
        "@default"
    ]

    return nquads


def get_value_and_node(
    nquads: Iterable[Dict[str, Any]], uri: str
) -> Tuple[Tuple[str, ...], Tuple[str, ...]]:
    pairs: List[Tuple[str, str]] = [
        (item["subject"]["value"], item["object"]["value"])
        for item in nquads
        if item["predicate"]["value"] == uri
    ]
    if not pairs:
        return ((), ())
    nodes, values = zip(*pairs)
    return (cast(Tuple[str, ...], nodes), cast(Tuple[str, ...], values))


def find_top_level_uri(
    nquads_id: str, nquads: Iterable[Dict[str, Any]], top_level_uris: Sequence[str]
) -> Optional[str]:
    uri: Optional[str] = None
    for item in nquads:
        if item["object"]["value"] == nquads_id:
            if item["predicate"]["value"] in top_level_uris:
                uri = item["predicate"]["value"]
            elif item["predicate"]["value"] not in top_level_uris:
                uri = find_top_level_uri(
                    item["subject"]["value"], nquads, top_level_uris
                )
            else:  # this can never happen?
                print("couldn't find top level uri")
    return uri


def fetch_value_source(client: Any, _id: Any, uri: str) -> List[str]:
    doc = client._getannotation(_id, jsonld=True)
    nquads = nquads_transform(doc)
    (node, value) = get_value_and_node(nquads, uri)
    source = [
        find_top_level_uri(item, nquads, client._top_level_jsonld_uris) or ""
        for item in node
    ]
    result = [i + " " + j for i, j in zip(value, source)]
    return result


def get_uri_list(context: Dict[str, Dict[str, Dict[str, str]]]) -> Dict[str, List[str]]:
    uri_path_dict: Dict[str, List[str]] = {}

    for path, v in context.items():
        for field_name, value in v["@context"].items():
            new_path = path.replace("/", ".") + "." + field_name
            if value not in uri_path_dict:
                uri_path_dict[value] = [new_path]
            else:
                uri_path_dict[value].append(new_path)
    return uri_path_dict


def query_by_uri(
    client: Any, uri: str, value: str, context: Dict[str, Dict[str, Dict[str, str]]]
) -> Any:
    context.pop("root")
    query_string = ""
    path_list = get_uri_list(context)[uri]
    for _item in path_list:
        query_string = query_string + " " + _item + ":" + value + " OR"
    query_string = query_string.strip(" OR")
    return client.query(query_string)
