import News
import datetime as dt
import os
import json
# import Para

def GetNewsEs(url):
    soup = News.GetSoup(url, 'lxml')

    # 获取网页内容基本信息
    newsContent = soup.body.select('div[class="newsContent"]')[0]
    contentBody = soup.body.select('div[id="ContentBody"]')[0]
    if newsContent.parent == contentBody:  # 研报样式
        title = soup.body.select('div[class="report-title"]')[0].h1.text.strip()
        newsInfo = soup.body.select('div[class="report-infos"]')[0]
        time = dt.datetime.strptime(newsInfo.contents[3].text.strip(), '%Y年%m月%d日 %H:%M')
        source = newsInfo.contents[5].text.strip() + ' ' + newsInfo.contents[7].text.strip()
        abstract = ''
        newsBody = newsContent
    elif contentBody.parent == newsContent:  # 资讯样式
        title = newsContent.h1.text.strip()
        newsInfo = newsContent.select('div[class="Info"]')[0]
        newsBody = contentBody
        time = dt.datetime.strptime(newsInfo.select('div[class="time"]')[0].text.strip(), '%Y年%m月%d日 %H:%M')
        source = newsInfo.img['alt'] if newsInfo.img is not None else ''
        absTagList = newsBody.select('div[class="b-review"]')
        if len(absTagList) == 0:
            abstract = ''
        else:
            abstract = absTagList[0].text.strip()
    else:
        raise 'Unknown page style: url = ' + url
    sectionList = []
    news = News.News(url, time, title, source, abstract, '', sectionList)

    # 识别段落
    secTitle = ''
    secContent = ''
    for c in newsBody.contents:
        if c.name == 'p' and len(c.attrs) == 0: # 段落标题和正文都存在于<p></p>标签中，且标签无属性
            # 标题判断：<p></p>中整段文本全为加粗，即<p></p>中存在<strong></strong>标签且无非空白文本位于<strong></strong>之外，且无<span></span>子节点
            if c.strong is not None and c.strong.span is None:
                isTitle = True
                for cc in c.contents:
                    if not (isinstance(cc, str) and cc.strip() == '' or cc.name == 'strong'):
                        isTitle = False
                        break
                if c.strong.text.strip() == c.text.strip():
                    isTitle = True
                if isTitle:  # 如果发现了新的标题，则认为新段落开始，将前面已经有段落内容存入段落列表
                    if secTitle != '' or secContent != '':
                        sectionList.append(News.Section(secTitle, secContent, news, url, len(sectionList)))
                    secTitle = ''
                    secContent = ''
                    secTitle = c.text.strip()
                    continue
            # 正文判断：<p></p>中至少直接有一处非空白文本（直接位于<p></p>中，而非子标签中）
            for cc in c.contents:
                if isinstance(cc, str) and cc.strip() != '':
                    secContent += c.text + os.linesep
                    break
    if secContent != '' or secContent != '':
        sectionList.append(News.Section(secTitle, secContent, news, url, len(sectionList)))
    return news

def GetNewsUrlEs(url):
    soup = News.GetSoup(url, 'lxml')

    newsListContent = soup.body.select('ul[id="newsListContent"]')[0]
    sumList = newsListContent.select('li')
    urlList = []
    for sum in sumList:
        sumContent = sum.select('div')[-1].select('p')
        title = sumContent[0].text.strip()
        info = sumContent[1].text.strip()
        time = sumContent[2].text.strip()
        pageUrl = sumContent[0].a['href']
        urlList.append(pageUrl)
    return urlList

def GetNewsListEs(url, time = dt.datetime.min, label = '', maxOverdue = 5):
    soup = News.GetSoup(url, 'lxml')

    maxPage = int(soup.body.select('div[id="pagerNoDiv"]')[0].select('a[class="page-btn"]')[0].previous_sibling.text)
    newsList = []
    overdueCount = 0
    maxTime = dt.datetime.min
    for p in range(1, maxPage + 1):
        pageUrl = url[0 : len(url) - 5] + '_' + str(p) + '.html'
        try:
            urlList = GetNewsUrlEs(pageUrl)
        except Exception as e:
            News.WriteLog(str(e) + '. url = ' + pageUrl)
            continue
        for newsUrl in urlList:
            try:
                news = GetNewsEs(newsUrl)
                news.label = label
                # if news.time <= time:
                if news.time.date() < time.date():
                    overdueCount += 1
                else:
                    newsList.append(news)
                    maxTime = news.time if news.time > maxTime else maxTime
                    print(news.url)
                    print(news.time)
                    print(news.title)
            except Exception as e:
                News.WriteLog(str(e) + ', url = ' + newsUrl)
                continue
            if overdueCount >= maxOverdue:
                return newsList, maxTime
    return newsList, maxTime

def GetReportUrlEs(url):
    jsonText = News.OpenUrl(url)
    jsonData = json.loads(jsonText)
    data = jsonData['data']
    urlList = []
    for d in data:
        if isinstance(d, dict):
            dtStr = d['datetime']
            infoCode = d['infoCode']
        else:
            strSplit = d.split(',')
            dtStr = dt.datetime.strptime(strSplit[1], '%Y/%m/%d %H:%M:%S').strftime('%Y-%m-%dT%H:%M:%S')
            infoCode = 'hy,' + strSplit[2]
        urlList.append('http://data.eastmoney.com/report/' + dtStr[0 : 4] + dtStr[5 : 7] + dtStr[8 : 10] + '/' + infoCode + '.html?dt=' + dtStr)
    return urlList

def GetReportListEs(url, time = dt.datetime.min, label = '', maxOverdue = 5):
    maxPage = 1000
    newsList = []
    overdueCount = 0
    maxTime = dt.datetime.min
    urlList = []
    exitTraverse = False
    for i in range(1, maxPage + 1):
        jsonUrl = url.replace('&p=x&', '&p=' + str(i) + '&')
        try:
            urlSet = GetReportUrlEs(jsonUrl)
        except Exception as e:
            News.WriteLog(str(e) + '. url = ' + jsonUrl)
            continue
        for u in urlSet:
            newsTime = dt.datetime.strptime(u[len(u) - 19 : len(u) + 1], '%Y-%m-%dT%H:%M:%S')
            if newsTime.date() < time.date():
                overdueCount += 1
            if overdueCount >= maxOverdue:
                exitTraverse = True
                break
            if newsTime > time:
                urlList.append(u)
                maxTime = newsTime if newsTime > maxTime else maxTime
        if exitTraverse:
            break

    for newsUrl in urlList:
        try:
            news = GetNewsEs(newsUrl)
            news.label = label
            news.time = dt.datetime.strptime(newsUrl[len(newsUrl) - 19 : len(newsUrl) + 1], '%Y-%m-%dT%H:%M:%S')
            news.url = news.url[0 : len(news.url) - 23]
            newsList.append(news)
            print(news.url)
            print(news.time)
            print(news.title)
        except Exception as e:
            News.WriteLog(str(e) + ', url = ' + newsUrl)
            continue

    return newsList, maxTime

def Launch(conn):
    timeDict = conn.hgetall('CONFIG_ES')
    for key in timeDict.keys():
        timeDict[key] = dt.datetime.strptime(timeDict[key], '%Y-%m-%d %H:%M:%S')

    infoList = [
                {'url'   : 'http://stock.eastmoney.com/news/cbkjj.html',
                 'key'   : 'bkjj',
                 'label' : '东方财富 板块聚焦',
                 'method': GetNewsListEs},

                {'url'   : 'http://stock.eastmoney.com/news/cggdj.html',
                 'key'   : 'ggdj',
                 'label' : '东方财富 个股点睛',
                 'method': GetNewsListEs},

                {'url'   : 'http://finance.eastmoney.com/news/cgsxw.html',
                 'key'   : 'gsxw',
                 'label' : '东方财富 公司新闻',
                 'method': GetNewsListEs},

                # {'url'   : 'http://stock.eastmoney.com/news/cgspj.html',
                #  'key'   : 'gspj',
                #  'label' : '东方财富 个股评级',
                #  'method': GetNewsListEs},

                {'url'   : 'http://datainterface.eastmoney.com//EM_DataCenter/js.aspx?'
                           'type=SR&sty=GGSR&'
                           'js={%22data%22:[(x)],%22pages%22:%22(pc)%22,%22update%22:%22(ud)%22,%22count%22:%22(count)%22}'
                           '&ps=50&p=x&mkt=0&stat=0&cmd=2&code=&rt=50048771',
                 'key'   : 'ggyb',
                 'label' : '东方财富 个股研报',
                 'method': GetReportListEs},

                {'url'   : 'http://datainterface.eastmoney.com//EM_DataCenter/js.aspx?'
                           'type=SR&sty=HYSR&'
                           'js={%22data%22:[(x)],%22pages%22:%22(pc)%22,%22update%22:%22(ud)%22,%22count%22:%22(count)%22}'
                           '&ps=50&p=x&mkt=0&stat=0&cmd=2&code=&rt=50048771',
                 'key'   : 'hyyb',
                 'label' : '东方财富 行业研报',
                 'method': GetReportListEs},

                {'url'   : 'http://finance.eastmoney.com/news/cgspl.html',
                 'key'   : 'gspl',
                 'label' : '东方财富 股市评论',
                 'method': GetNewsListEs},

                {'url'   : 'http://finance.eastmoney.com/news/ccjxw.html',
                 'key'   : 'cjxw',
                 'label' : '东方财富 产经新闻',
                 'method': GetNewsListEs},

                {'url'   : 'http://finance.eastmoney.com/news/czqyw.html',
                 'key'   : 'zqyw',
                 'label' : '东方财富 证券要闻',
                 'method': GetNewsListEs},

                {'url'   : 'http://finance.eastmoney.com/news/cgnjj.html',
                 'key'   : 'gnjj',
                 'label' : '东方财富 国内经济',
                 'method': GetNewsListEs},

                {'url'   : 'http://stock.eastmoney.com/news/cbktt.html',
                 'key'   : 'bktt',
                 'label' : '东方财富 报刊头条',
                 'method': GetNewsListEs}
                ]

    newsList = []
    for info in infoList:
        key = info['key']
        if key in timeDict.keys():
            newsList, maxTime = info['method'](info['url'], timeDict[key], info['label'])
            timeDict[key] = maxTime if maxTime != dt.datetime.min else timeDict[key]
            for news in newsList:
                if not conn.exists(news.url):
                    newsDict = {'url': news.url, 'time': news.time, 'title': news.title,
                                'source': news.source, 'label': news.label,
                                'abstract': news.abstract, 'secNum': len(news.sectionList)}
                    conn.hmset(news.url, newsDict)
                    for section in news.sectionList:
                        secDict = {'url': news.url, 'time': news.time, 'title': news.title,
                                   'secTitle': section.title, 'content': section.content}
                        secKey = news.url + ',' + str(section.seq)
                        if not conn.exists(secKey):
                            conn.hmset(secKey, secDict)
                            conn.sadd('SECTION_BUFFER', secKey)
            conn.hset('CONFIG_ES', key, timeDict[key].strftime('%Y-%m-%d %H:%M:%S'))
        else:
            News.WriteLog('Can not get last update time of ' + key)

    ddd = 0