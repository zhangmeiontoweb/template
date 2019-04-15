# -*- coding: utf-8 -*-
# from nltk.tokenize import sent_tokenize,word_tokenize
# from itertools import islice
import spotlight
from SPARQLWrapper import SPARQLWrapper,JSON
import re
import json
from pynlp import StanfordCoreNLP
import os
def nl_pattern_generation(file):
    #截取短句：1.设置最长长度进行限制，2.两个实体之间的关系（前后实体不考虑）
    #如何确定判断截取的短句描述的就是该triple
    annotators = 'tokenize, ssplit, pos, lemma, ner, entitymentions, coref, sentiment, quote, openie'
    options = {'openie.resolve_coref': True}
    nlp = StanfordCoreNLP(annotators=annotators, options=options)

    f= open(file,"rt")
    lines = f.readline()
    count = 1
    templates = list()
    f_output = open("templates_"+file,"wt",encoding="UTF-8")

    while lines:
        if lines == "":
            lines = f.readline()
            continue
        # lines = get_coreference_text(nlp,lines)
        # for line in nlp(lines.encode("utf-8")):
        # for line in re.split(' \. |\;|\?|\!|\:',lines):
        for line in re.split('\. |\;|\?|\!|\:', lines):
        # for line in get_line(lines):
            try:
                if len(str(line).strip().split(' ')) < 3 or len(nlp(str(line).encode('utf-8')).entities) < 2:
                    continue
            except:
                continue
            # prases = line.split(". ")
            # for prase in prases:
            #     print(prase)
            entities = get_entities_by_line(nlp,str(line))
            if len(entities)<2:
                count = count + 1
                continue
            else:
                add_templates = add_template_by_line(entities,str(line))
                if len(add_templates)==0:
                    count = count + 1
                    continue
                else:
                    f_output.write("NL:" + str(line))
                    for template in add_templates:
                        if template is None or len(template)==0:
                            continue
                        print(template)
                        f_output.write("\r\ntemplate:"+str(template))
                        templates.append(template)
                    f_output.write("\r\n\r\n")
                    count = count + 1
        lines = f.readline()

def get_entities_by_line(nlp,line):

    try:
        annotations = spotlight.annotate('http://api.dbpedia-spotlight.org/en/annotate', line.encode("utf-8"),
                                         confidence=0.4, support=20)
        # annotations = spotlight.annotate('http://model.dbpedia-spotlight.org/en/annotate', line.encode("utf-8"),
        #                                  confidence=0.4, support=20)
        if annotations is None:
            return ""
        entities = list()
        types = dict()
        for ent in nlp(line.encode('utf-8')).entities:
            types[str(ent)] = ent.type
        for re_ano in annotations:
            entity = dict()
            entity['URI'] = "<" + re_ano['URI'] + ">"
            entity['surfaceForm'] = re_ano['surfaceForm']
            entity['types'] = ""
            if entity['surfaceForm'] in types:
                entity['types'] = types[entity['surfaceForm']]
            else:
                if re_ano['types'] != '':
                    entity['types'] = re_ano['types']
                else:
                    for key in types:
                        if entity['surfaceForm'] in key:
                            entity['types'] = types[key]
            if entity['types'] == '':
                continue
            entity['start'] = re_ano['offset']
            entity['end'] = entity['start'] + len(entity['surfaceForm'])
            entities.append(entity)
        return entities
    except:
        print ("spotlight exception")
        print (line)
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
        # print (sub_line)
        if len(sub_line) == 0:
            i = i + 1
            continue
        left_word = sub_line.replace(entities[i]['surfaceForm'],'').replace(entities[j]['surfaceForm'],'')
        if len(left_word)<4 or left_word==' and ' or left_word=="'s "or left_word==", ":
            i = i + 1
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

    try:
        sparql = SPARQLWrapper("https://dbpedia.org/sparql")
        if e1 == e2:
            return json.loads('{"bindings": []}')
        query = "SELECT distinct ?p WHERE { " + e1 + " ?p " + e2 + "}"
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        if results is None:
            return json.loads('{"bindings": []}')
        return results['results']
    except:
        print("exception")
        print (query)
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

def get_coreference_text(nlp,lines):

    try:
        document = nlp(lines.encode("utf-8"))
        new_lines = list()
        for i, sen in enumerate(document):
            new_line = list()
            j = 0
            while j < len(sen):
                new_line.append(str(document[i][j]))
                j = j + 1
            new_lines.append(new_line)
        for chain in document.coref_chains:
            for mention in chain._coref.mention:
                new_lines[mention.sentenceIndex][mention.beginIndex] = str(chain.referent)
        new_str = ""
        k = 0
        while k < len(new_lines):
            for word in new_lines[k]:
                new_str = new_str + ' ' + str(word)
            k = k + 1
        return new_str
    except:
        ss = re.split(' \. |\;|\?|\!|\:', lines)
        s1 = ""
        s2 = ""
        i = 0
        for s in ss:
            if i<len(ss)/2:
                s1 = s1 + s +". "
            else:
                s2 = s2 + s +". "
        return get_coreference_text(nlp,s1)+get_coreference_text(nlp,s2)

def get_line(lines):
    line_list = re.split('\. |\;|\?|\!|\:', lines)
    i = 0
    while i < len(line_list):
        if len(line_list[i].split(' '))>50:
            va = line_list[i]
            line_list.remove(va)
            for it in get_sub_line(va):
                line_list.append(it)
        i = i + 1
    if len(line_list)<2:
        return line_list
    if len(line_list[0].strip().split(' '))<3:
        line_list[0] = line_list[0] + '. ' + line_list[1]
        line_list.remove(line_list[1])
    if len(line_list)<3:
        return line_list
    while i< len(line_list)-1:
        # if i>len(line_list)-1:
        #     break
        if len(line_list[i+1].strip().split(' '))<5:
            line_list[i] = line_list[i]+ '. '+line_list[i+1]
            line_list.remove(line_list[i+1])
        i = i + 1
    line_list[len(line_list)-1] = line_list[len(line_list)-1] + '. '
    # i = 0
    # while i<len(line_list):
    #     print (len(line_list[i].split(' ')))
    #     if len(line_list[i].split(' '))>50:
    #         l = line_list[i].split(', ')
    #         j = 0
    #         line_list.remove(line_list[i])
    #         if len(l)<3:
    #             line_list.append(l)
    #             continue
    #         while j<len(l)-1:
    #             l[j] = l[j] + l[j+1]
    #             l.remove(l[j+1])
    #             j = j + 1
    #         line_list.append(l)
    #     i = i + 1
    return line_list

def get_sub_line(lines):
    sub_list = list()
    l = lines.split(', ')
    j = 0
    # line_list.remove(line_list[i])
    if len(l) < 3:
        return l
    while j < len(l) - 1:
        l[j] = l[j] + l[j + 1]
        l.remove(l[j + 1])
        sub_list.append(l[j])
        j = j + 1
    return sub_list

def main():
    path = "A_entities"
    path1 = "A_templates"
    files = os.listdir(path)
    files1 = os.listdir(path1)
    for file in files:
        if ("template_"+file) in files1:
            continue
        else:
            nl_pattern_generation(path+"/"+file)


    # annotations = spotlight.annotate('http://model.dbpedia-spotlight.org/en/annotate', "purchased a 20 stake in Dolan's company.",
    #                                  confidence=0.4, support=20)
    # print (annotations)
    # annotators = 'tokenize, ssplit, pos, lemma, ner, entitymentions, coref, sentiment, quote, openie'
    # options = {'openie.resolve_coref': True}
    # nlp = StanfordCoreNLP(annotators=annotators, options=options)
    # line = "The accompanying fanfare—originally composed for Score Productions by Ferdinand Jay Smith III of Jay Advertising, who adapted the theme from the Scherzo movement of Antonín Dvořák's Ninth Symphony—has become a musical signature for HBO, and has been used in feature presentation, upcoming program and evening schedule bumpers, and network IDs since 1998 with various arrangements from horns to piano being used over the years."
    # print (get_entities_by_line(nlp,line))
    # get_type_abstract("<http://dbpedia.org/resource/Mainland_China>")
    # get_type_sparql("<http://dbpedia.org/page/Taiwan>")

    # text = ('GOP Sen. Rand Paul was assaulted in his home in Bowling Green, Kentucky, on Friday, '
    #         'according to Kentucky State Police. State troopers responded to a call to the senator\'s '
    #         'residence at 3:21 p.m. Friday. Police arrested a man named Rene Albert Boucher, who they '
    #         'allege "intentionally assaulted" Paul, causing him "minor injury". Boucher, 59, of Bowling '
    #         'Green was charged with one count of fourth-degree assault. As of Saturday afternoon, he '
    #         'was being held in the Warren County Regional Jail on a $5,000 bond.')
    # line = "HBO also shows sub-runs—runs of films that have already received broadcast or syndicated television airings—of theatrical films from Paramount Pictures & Nickelodeon Movies (including content from subsidiary Republic Pictures, both for films released prior to 2004), Walt Disney Studios Motion Pictures (including content from subsidiaries Walt Disney Pictures, Touchstone Pictures, Hollywood Pictures, and former subsidiary and current independently operated studio Miramax Films), Sony Pictures Entertainment (including content from subsidiaries Columbia Pictures, Sony Pictures Classics, Screen Gems and former HBO sister company TriStar Pictures, all for films released prior to 2005), Metro-Goldwyn-Mayer (including content from subsidiaries United Artists, Orion Pictures and The Samuel Goldwyn Company), and Lions Gate Entertainment (for films released prior to 2004)."

    # print (get_line(line))
    # print (get_coreference_text(nlp,text))
    #
    # document = nlp(text)
    # for chain in document.coref_chains:
    #     for mention in chain._coref.mention:
    #         if chain.chain_id == mention.mentionID:
    #             text = text.replace(str(document[mention.sentenceIndex][mention.beginIndex]),str(chain.referent))

        # for attr in 'beginIndex':
        #     print(getattr(chain, attr))
        # ref = chain._doc.text
        # chain_referent = ''
        # for token in chain.referent._tokens:
        #     chain_referent += token.word
        # chain_id = chain.chain_id
        # id = "id="+str(chain_id)
        # print(ref.replace('"'+id+'"',chain_referent))



        # for attr in 'type', 'number', 'animacy', 'gender':
            # print(attr, getattr(ref, attr), sep=':')
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