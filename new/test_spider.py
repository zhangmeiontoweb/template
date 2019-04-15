import requests
import re
from threading import Thread
from urllib.parse import urljoin
from bs4 import BeautifulSoup
file_path = 'A_entities.txt'
with open(file_path, encoding='utf-8') as fp:
    keys = fp.readlines()
values = list(set(keys))
headers = {'User-Agent': "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"}


def write(data):
    for uri in data:
        url = urljoin('https://en.wikipedia.org', "/wiki/" + uri.strip())
        print(url)
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            bs = BeautifulSoup(r.text)
            ps = bs.find_all('p')
            with open('A_entities/{}.txt'.format(uri.replace("/","_").strip()), 'w', encoding='utf-8') as tt:
                for p in ps:
                    text = re.sub(u"\\[.*?]", "", p.get_text())
                    # print(text)
                    tt.write(text + '\r\n')

if __name__ == '__main__':
    for i in range(0, int(len(values)/1000)):
        t = Thread(target=write, args=(values[i*1000: (i+1)*1000],))
        t.start()
