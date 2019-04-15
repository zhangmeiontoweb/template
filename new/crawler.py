#-*- coding:utf-8 -*-
import urllib2
from bs4 import BeautifulSoup
import re
import random
import datetime
import os
random.seed(datetime.datetime.now())

def getLink(url):
    html = urllib2.urlopen("https://en.wikipedia.org"+url)
    bsObj = BeautifulSoup(html)
    ps = bsObj.find_all('p')

    # try:
    #     f = open(url+".txt","a")
    # except:
    #     os.mkdir(url+".txt")
    # reObj = re.compile(r'([).*(])')
    with open("D_entities/"+url.replace("/","_")+".txt", "w") as f:
        for p in ps:
            f.write(re.sub(u"\\[.*?]", "",p.get_text()).encode('utf-8').replace()+"\r\n")

    # return bsObj.find('div', id="bodyContent").find_all('a', href=re.compile("^(/wiki/)((?!;)S)*$"))

if __name__ == '__main__':
    f= open("D_entities.txt","r")
    line = f.readline()
    while line:
        # print(line)
        if len(line)>0:
            # print(line)
            url = "/wiki/"+line.replace("http://dbpedia.org/resource/","")
            print(url)
            if os.path.exists("E_entities/"+url.replace("/","_")+".txt"):
                line = f.readline()
                continue
            # url = "/wiki/Barack_Obama"
            try:
                getLink(url)
            except:
                line = f.readline()
                continue
        line = f.readline()


# while len(links)>0:
#     newArticle = links[random.randint(0,len(links)-1)].attrs['href']
#     file.write(newArticle + "\n")
#     print newArticle
#     links = getLink(newArticle)
# file.close()
