import urllib.request
import bs4
import os
import datetime as dt
import chardet

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

