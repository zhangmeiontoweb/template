# -*- coding: utf-8 -*-
# import json
from gensim.test.utils import common_texts,get_tmpfile
import numpy as np
from gensim.models import Word2Vec,KeyedVectors
import re
# from scipy.linalg import norm
from gensim.scripts.glove2word2vec import glove2word2vec
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords

lemmatizer = WordNetLemmatizer()

max_len = 20
Max_sim = 0.8
Min_sim = 0.4
wmd_dis = 2

# file = '/mnt/d/data/wiki-news-300d-1M.vec'
file = '/mnt/d/data/glove/glove.6B.50d.txt'

glove2word2vec(glove_input_file=file, word2vec_output_file="gensim_glove_vectors.txt")
model = KeyedVectors.load_word2vec_format("gensim_glove_vectors.txt", binary=False)
# model = KeyedVectors.load_word2vec_format(file, binary=False)

def main():
    f = open("_wiki_Barack_Obama_templates.txt", "rt",encoding="utf-8")

    templates = list()
    candidate = list()
    # file = 'D:/data/glove.6B.50d.txt'
    # file = '/mnt/d/data/glove.840B.300d.txt'

    # model = KeyedVectors.load_word2vec_format("/mnt/d/data/crawl-300d-2M.vec", binary=False)
    # print(model.similarity('one','two'))
    # s1 = 'the first sentence'
    # s2 = 'the second text'
    for line in f.readlines():
        if line.startswith("template:"):
            template = eval(line.replace("template:",''))
            # print(template)
            nl_pattern = template['nl_pattern'][0]
            start, end = re.search(r'>(.*)<',nl_pattern).span()
            phrase = nl_pattern[start+2:end-2]
            phrase = re.sub('[0-9’!"#$%&\'()*+,-./:;<=>?@，。?★、…【】《》？“”‘’！[\\]^_`{|}~]+','', phrase)
            phrase = [ x.lower() for x in phrase.split(' ') if x!='' and x not in stopwords.words('english')]
            predicate = template['triple_pattern'][1].split('/')[-1]
            # phrase = 'born in in'
            # predicate = 'birth place'
            # print(phrase)
            # print(predicate)
            fin,count = vector_distance_sim(phrase,[x for x in split_pre(predicate) if x not in stopwords.words('english')])
            if not fin:
                if count == 0:
                    continue
                else:
                    candidate.append(template)
            i = 0
            if len(templates) == 0:
                templates.append(template)
            flag = 0
            while i < len(templates):
                if template['triple_pattern'] == templates[i]['triple_pattern'] :
                    if len(nl_pattern.split(' ')) < max_len and nl_pattern not in templates[i]['nl_pattern']:
                        templates[i]['nl_pattern'].append(nl_pattern)
                    flag = 1
                i = i + 1
            if flag==0 and len(nl_pattern.split(' ')) < max_len:
                templates.append(template)
    for t in templates:
        print(t)

def vector_distance_sim(words, pre):
    min_dis = 100
    max_sim = 0
    print(words)
    for word in words:
        for p in pre:
            dis = model.wmdistance(lemmatizer.lemmatize(word,'v'),p)
            try:
                sim = model.similarity(lemmatizer.lemmatize(word,'v'), p)
                if sim>max_sim:
                    max_sim = sim
            except:
                sim = 0
            print(lemmatizer.lemmatize(word,'v')+' '+p+' '+str(sim))
            if dis<min_dis:
                min_dis = dis
    count = 1
    if max_sim>Max_sim or min_dis<0.5:
        return True,count
    if max_sim<Min_sim:
        count = 0
    return False, count

def split_pre(pre):
    ind = 0
    i = 0
    pre_list = list()
    while i<len(pre):
        if pre[i].isupper():
            if i - ind>1:
                pre_list.append(pre[ind:i].lower())
                ind = i
            # else:
            #     return list(pre)
        i = i + 1
    if len(pre_list)==0:
        pre_list.append(pre)
    else:
        pre_list.append(pre[ind:].lower())
        # print(pre_list)
    return pre_list
# def vector_similarity(model,s1, s2):
#     def sentence_vector(s):
#         words = s.split(' ')
#         v = np.zeros(300)
#         for word in words:
#             v = v+model[word]
#         v /= len(words)
#         return v
#     v1, v2 = sentence_vector(s1), sentence_vector(s2)
#     return np.dot(v1, v2) / (norm(v1) * norm(v2))


if __name__ == '__main__':
    main()

