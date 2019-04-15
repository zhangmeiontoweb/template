from SPARQLWrapper import SPARQLWrapper,JSON
import json
def get_entities():
    sparql = SPARQLWrapper("https://dbpedia.org/sparql")
    query = "SELECT distinct ?x WHERE { ?x ?p ?y FILTER regex(?x, '^http://dbpedia.org/resource/F') }"
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    if results is None:
        return json.loads('{"bindings": []}')
    # print(results)
    return results['results']
    # try:
    #
    #
    # except:
    #     print("exception")
    #     print (query)
    #     return json.loads('{"bindings": []}')

if __name__ == '__main__':
    f_output = open("F_entities.txt", "w", encoding="UTF-8")
    result = get_entities()
    for r in result['bindings']:
        # print(r[])
        f_output.write(r['x']['value'].replace("http://dbpedia.org/resource/","")+'\r\n')