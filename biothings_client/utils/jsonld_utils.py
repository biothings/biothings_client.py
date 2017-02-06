from pyld import jsonld

def nquads_transform(doc):
    t = jsonld.JsonLdProcessor()
    nquads = t.parse_nquads(jsonld.to_rdf(doc, {'format': 'application/nquads'}))['@default']
    
    return nquads

def get_value_and_node(nquads, uri):
    return tuple(zip(*[(i['subject']['value'], i['object']['value']) for i in nquads 
                            if i['predicate']['value'] == uri]))

def find_top_level_uri(nquads_id, nquads, top_level_uris):
    for item in nquads:
        if item['object']['value'] == nquads_id:
            if item['predicate']['value'] in top_level_uris:
                uri = item['predicate']['value']
            elif item['predicate']['value'] not in top_level_uris:
                uri = find_top_level_uri(item['subject']['value'], nquads, top_level_uris)
            else:
                print("couldn't find top level uri")
    return uri

def fetch_value_source(client, _id, uri):
    doc = client._getannotation(_id, jsonld=True)
    nquads = nquads_transform(doc)
    (node, value) = get_value_and_node(nquads, uri)
    source = [find_top_level_uri(item, nquads, client._top_level_jsonld_uris) for item in node]
    result = [i + ' ' + j for i,j in zip(value, source)]
    return result
