import urllib.request
import bs4
import os
import datetime as dt
import chardet
import hashlib

def SenVec(sentence, parseModel = 2):
    vec = []
    if isinstance(parseModel, int):
        for i in range(len(sentence) - 1):
            vec.append(sentence[i : i + parseModel])
        return vec
    else:
        temp = parseModel.cut(sentence)
        for t in temp:
            vec.append(t[0])
    return vec

def SimHash(senVec, length = 64):
    accum = [0] * length
    simhash = ''
    for word in senVec:
        m16 = hashlib.md5(word.encode('utf-8')).hexdigest()
        m10 = int(int(m16, 16) / (2 ** (128 - length)))
        m2 = bin(m10)[2 : ]
        wordHash = [0] * (length - len(m2))
        wordHash.extend(m2)

        for i in range(len(wordHash)):
            if wordHash[i] == '0':
                accum[i] -= 1
            elif wordHash[i] == '1':
                accum[i] += 1
    for i in range(len(accum)):
        simhash += ('1' if accum[i] > 1 else '0')

class News:
    def __init__(self, url, time, title, source, abstract, content, sectionList, label = ''):
        self.url = url
        self.time = time
        self.title = title
        self.source = source
        self.abstract = abstract
        self.content = content
        self.sectionList = sectionList
        self.label = label

class Section:
    def __init__(self, title, content, news, url, seq):
        self.title = title
        self.content = content
        self.news = news
        self.url = url
        self.seq = seq

def Decode(byte):
    try:
        return byte.decode('UTF-8')
    except Exception as e:
        return byte.decode('GBK')

def OpenUrl(url, retry = 0):
    if retry >= 2:
        return Decode(urllib.request.urlopen(url).read())
    try:
        return Decode(urllib.request.urlopen(url).read())
    except Exception as e:
        WriteLog(str(e) + ', retry time is ' + str(retry) + ', url = ' + url)
        return OpenUrl(url, retry + 1)

def GetSoup(url, resolver = 'lxml'):
    html = OpenUrl(url)
    # charset = chardet.detect(html)
    # htmlDec = html.decode(charset['encoding'])
    soup = bs4.BeautifulSoup(html, resolver)
    return soup

def WriteLog(logStr):
    file = open(os.path.join('.', 'log', 'log' + str(dt.datetime.now().date()) + '.txt'), 'a')
    file.write(str(dt.datetime.now()) + '  ' + logStr + os.linesep)
    file.flush()
    file.close()

