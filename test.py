# -*- coding: utf-8 -*-
from nltk.tokenize import sent_tokenize
from itertools import islice
import spotlight
from SPARQLWrapper import SPARQLWrapper,JSON
import re
import json
from pynlp import StanfordCoreNLP
def nl_pattern_generation():
    #截取短句：1.设置最长长度进行限制，2.两个实体之间的关系（前后实体不考虑）
    #如何确定判断截取的短句描述的就是该triple
    annotators = 'tokenize, ssplit, pos, lemma, ner, entitymentions, coref, sentiment, quote, openie'
    options = {'openie.resolve_coref': True}
    nlp = StanfordCoreNLP(annotators=annotators, options=options)

    f= open("_wiki_HBO.txt","r",encoding="UTF-8")
    lines = f.readline()
    count = 1
    templates = list()
    f_output = open("_wiki_HBO_templates.txt","w",encoding="UTF-8")
    while lines is not None :
        if lines == "":
            lines = f.readline()
            continue

        for line in re.split('\.|\?|\!|\,|\;',str(lines)):
            # print line
            if len(line.strip().split(' '))<3:
                continue
            # prases = line.split(". ")
            # for prase in prases:
            #     print(prase)
            # print (line)
            entities = get_entities_by_line(nlp,line)
            if len(entities)<2:
                # print("NL:" + line)
                count = count + 1
                continue
            else:
                add_templates = add_template_by_line(entities,line)
                if len(add_templates)==0:
                    # print("NL:" + line)
                    # print(entities)
                    count = count + 1
                    continue
                else:
                    f_output.write("NL:" + line)
                    for template in add_templates:
                        print(template)
                        f_output.write("\r\ntemplate:"+str(template))
                        templates.append(template)
                    f_output.write("\r\n")
                    count = count + 1
        lines = f.readline()

def get_entities_by_line(nlp,line):

    try:
        annotations = spotlight.annotate('http://api.dbpedia-spotlight.org/en/annotate', line,
                                         confidence=0.4, support=20)
        # annotations = spotlight.annotate('http://model.dbpedia-spotlight.org/en/annotate', line,
        #                                  confidence=0.4, support=20)
        entities = list()
        for re_ano in annotations:
            entity = dict()
            entity['URI'] = "<" + re_ano['URI'] + ">"
            entity['surfaceForm'] = re_ano['surfaceForm']
            entity['types'] = ""
            for ent in nlp(line).entities:
                if str(ent) == entity['surfaceForm']:
                    entity['types'] = str(ent.type)
            if len(entity['types']) == 0:
                continue
            entity['start'] = re_ano['offset']
            entity['end'] = entity['start'] + len(entity['surfaceForm'])
            entities.append(entity)
        # for entity in nlp(line).entities:
        #     for entity in entities
        return entities
    except:
        print (line)
        print ("spotlight exception")
        return ""

def add_template_by_line(entities,line):
    templates = list()
    i = 0
    while i < len(entities) -1:
        j = i + 1
        if (entities[i]['start'] < entities[j]['start']):
            sub_line = line[entities[i]['start']:entities[j]['end']]
        else:
            sub_line = line[entities[j]['start']:entities[i]['end']]
        left_word = sub_line.replace(entities[i]['start'],'').replace(entities[j]['start'],'')
        if len(left_word.strip())<2 or left_word.strip()=='and':
            continue
        sub_line = line.replace(entities[i]['surfaceForm'],entities[i]['URI']).replace(entities[j]['surfaceForm'],entities[j]['URI'])
        if len(sub_line) == 0:
            continue
        final_patterns = list()
        patterns = sub_line.replace(entities[i]['surfaceForm'], ("<" + entities[i]['types'] + ">"))
        final_patterns.append(patterns.replace(entities[j]['surfaceForm'], ("<" + entities[j]['types'] + ">")))

        # if len(entities[i]['types']) > 0:
        #     types = entities[i]['types'].split('.')
        #     # print(get_type_psarql(entities[i]['URI']))
        #     new_types ="<" +  ",".join(types)+ ">"
        #     patterns.append(sub_line.replace(entities[i]['surfaceForm'], new_types))
        # else:
        #     results = get_type_sparql(entities[i]['URI'])
        #     new_types = "<"
        #     if len(results['bindings'])>0:
        #         for r in results['bindings']:
        #             if r['c']['value'] != 'http://www.w3.org/2002/07/owl#Thing' :
        #                 new_types = new_types + "," + r['c']['value']
        #         if "," not in new_types:
        #             print (entities[j]['URI'])
        #             patterns.append(sub_line)
        #         else:
        #             new_types = new_types + ">"
        #             patterns.append(sub_line.replace(entities[i]['surfaceForm'], new_types))
        #     else:
        #         patterns.append(sub_line)
        #         print (entities[i]['URI'])

        # if len(entities[j]['types']) > 0:
        #     types = entities[j]['types'].split('.')
        #     new_types ="<" + ",".join(types) + ">"
        #     for pt in patterns:
        #         final_patterns.append(pt.replace(entities[j]['surfaceForm'], new_types))
        # else:
        #     results = get_type_sparql(entities[j]['URI'])
        #     if len(results['bindings'])>0:
        #         new_types = "<"
        #         for r in results['bindings']:
        #             if r['c']['value'] != 'http://www.w3.org/2002/07/owl#Thing' :
        #                 new_types = new_types+"," + r['c']['value']
        #         if "," not in new_types:
        #             print (entities[j]['URI'])
        #             final_patterns = patterns
        #         else:
        #             new_types = new_types + ">"
        #             for pt in patterns:
        #                 final_patterns.append(pt.replace(entities[j]['surfaceForm'], new_types))
        #     else:
        #         print (entities[j]['URI'])
        #         final_patterns = patterns
        pro_re1 = get_property(entities[i]['URI'], entities[j]['URI'])
        if len(pro_re1['bindings']) > 0:
            for p in pro_re1['bindings']:
                if "wikiPageWikiLink" in p['p']['value'] or "http://www.w3.org/2000/01/rdf-schema#seeAlso" in \
                        p['p']['value']:
                    continue
                template = dict()
                template['nl_pattern'] = final_patterns
                template['triple_pattern'] = (entities[i]['URI'], p['p']['value'], entities[j]['URI'])
                templates.append(template)
        # pro_re2 = get_property(entities[j]['URI'], entities[i]['URI'])
        # if len(pro_re2['bindings']) > 0:
        #     for p in pro_re2['bindings']:
        #         if "wikiPageWikiLink" in p['p']['value'] or "http://www.w3.org/2000/01/rdf-schema#seeAlso" in \
        #                 p['p']['value']:
        #             continue
        #         template = dict()
        #         template['nl_pattern'] = final_patterns
        #         template['triple_pattern'] = (entities[j]['URI'], p['p']['value'], entities[i]['URI'])
        #         templates.append(template)
        i = i + 1
    return templates

def get_type_sparql(e):
    # print (e)
    sparql = SPARQLWrapper("https://dbpedia.org/sparql")
    query = "SELECT distinct ?c WHERE { "+e+" <https://www.w3.org/1999/02/22-rdf-syntax-ns#type> ?c}"
    # query = "SELECT DISTINCT ?p WHERE { <http://dbpedia.org/resource/HBO> ?p <http://dbpedia.org/resource/Cinemax>}"
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    try:
        results = sparql.query().convert()
        # print(results)
        if len(results['results']['bindings'])==0:
            query = "SELECT distinct ?c WHERE { " + e + " <http://dbpedia.org/property/type> ?c}"
            sparql.setQuery(query)
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()
            if len(results['results']['bindings']) == 0:
                query = "SELECT distinct ?c WHERE { " + e + " <http://dbpedia.org/ontology/type> ?c}"
                sparql.setQuery(query)
                sparql.setReturnFormat(JSON)
                results = sparql.query().convert()
                if len(results['results']['bindings']) == 0:
                    query = "SELECT distinct ?c WHERE { " + e + " <http://purl.org/linguistics/gold/hypernym> ?c}"
                    sparql.setQuery(query)
                    sparql.setReturnFormat(JSON)
                    results = sparql.query().convert()

        return results['results']
    except:
        print("exception")
        return json.loads('{"bindings": []}')

def get_property(e1, e2):
    sparql = SPARQLWrapper("https://dbpedia.org/sparql")
    if e1 == e2:
        return json.loads('{"bindings": []}')
    query = "SELECT distinct ?p WHERE { "+e1+" ?p "+e2+"}"
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    try:
        results = sparql.query().convert()
        return results['results']
    except:
        print("exception")
        return json.loads('{"bindings": []}')

def get_type_abstract(e):

    sparql = SPARQLWrapper("https://dbpedia.org/sparql")
    query = "SELECT distinct ?c WHERE { "+e+" <http://www.w3.org/2002/07/owl#sameAs> ?c}"
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    try:
        results = sparql.query().convert()
        print(results)
        return results['results']
    except:
        print("exception")
        return json.loads('{"bindings": []}')

def main():
    # nl_pattern_generation()
    # annotations = spotlight.annotate('http://api.dbpedia-spotlight.org/en/annotate', "Barack Hussein Obama II  born August 4, 1961 is an American attorney and politician who served as the 44th President of the United States from 2009 to 2017.",
    #                                  confidence=0.4, support=20)
    # print (annotations)
    # get_type_abstract("<http://dbpedia.org/resource/Mainland_China>")
    # get_type_sparql("<http://dbpedia.org/page/Taiwan>")
    annotators = 'tokenize, ssplit, pos, lemma, ner, entitymentions, coref, sentiment, quote, openie'
    options = {'openie.resolve_coref': True}
    nlp = StanfordCoreNLP(annotators=annotators, options=options)
    text = ('GOP Sen. Rand Paul was assaulted in his home in Bowling Green, Kentucky, on Friday, '
            'according to Kentucky State Police. State troopers responded to a call to the senator\'s '
            'residence at 3:21 p.m. Friday. Police arrested a man named Rene Albert Boucher, who they '
            'allege "intentionally assaulted" Paul, causing him "minor injury". Boucher, 59, of Bowling '
            'Green was charged with one count of fourth-degree assault. As of Saturday afternoon, he '
            'was being held in the Warren County Regional Jail on a $5,000 bond.')

    document = nlp(text)
    chain = document.coref_chains
    print (chain)
    for item in chain:
        print (item.chain_id)

        print (item.referent)
        print (str(item).replace(item.chain_id,item.referent))

    # print (chain)
    # annotators = 'tokenize, ssplit, pos, lemma, ner, entitymentions, coref, sentiment, quote, openie'
    # options = {'openie.resolve_coref': True}
    # nlp = StanfordCoreNLP(annotators=annotators, options=options)
    # line = "Barack Hussein Obama II  born August 4, 1961 is an American attorney and politician who served as the 44th President of the United States from 2009 to 2017."
    # print (get_entities_by_line(nlp,line))
    #
    # for ent in nlp(line).entities:
    #     print (ent)

if __name__ == '__main__':
    main()