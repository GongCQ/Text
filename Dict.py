import News
import os
import fileinput
import bs4
import Public

# 从文件获取之前的关键字，并存入关键字集合
kwSet = set()
for keyword in fileinput.input(os.path.join('.', 'dict', 'keyword')):
    if keyword[-1] == os.linesep:
        keyword = keyword[0 : len(keyword) - 1]
    kwSet.add(keyword)

# 从同花顺获取概念/行业，并追加到关键字集合
thsUrl = ['http://q.10jqka.com.cn/gn/', 'http://q.10jqka.com.cn/thshy/']
for url in thsUrl:
    soup = bs4.BeautifulSoup('', 'lxml')
    retry = 0
    while soup.text == '' and retry <= 20:
        retry += 1
        try:
            soup = News.GetSoup(url)
        except Exception as e:
            nothingtodo = 0
    cateItemList = soup.select('div[class="cate_items"]')
    for cateItem in cateItemList:
        cateList = cateItem.select('a')
        for cate in cateList:
            text = cate.text
            kwSet.add(text)
            tail = text[max(0, len(text) - 2) : len(text)]
            if tail == '行业' or tail == '概念' or tail == '板块':
                kwSet.add(text[0 : len(text) - 2])

# 从东方财富获取概念/行业/地域，并追加到关键字集合
esUrl = ['http://quote.eastmoney.com/center/BKList.html#notion_0_0?sortRule=0']
for url in esUrl:
    soup = News.GetSoup(url)
    textList = soup.select('span[class="text"]')
    for t in textList:
        text = t.text
        kwSet.add(text)
        tail = text[max(0, len(text) - 2) : len(text)]
        if tail == '行业' or tail == '概念' or tail == '板块':
            kwSet.add(text[0 : len(text) - 2])

# 将关键字集合重新写入文件
Public.SetToFile(kwSet, os.path.join('.', 'dict', 'keyword'))

# 从文件获取之前的股票，并存入股票集合
stockSet = set()
for stock in fileinput.input(os.path.join('.', 'dict', 'stock')):
    if stock[-1] == os.linesep:
        stock = stock[0 : len(stock) - 1]
    stockSet.add(stock)

# 此处获取新的股票并追加到股票集合
# --------- 待填充 ----------

# 将股票集合重新写入文件
Public.SetToFile(stockSet, os.path.join('.', 'dict', 'stock'))

# 将股票集合与关键字集合的并集写入用户字典文件
Public.SetToFile(kwSet | stockSet, os.path.join('.', 'dict', 'dict'))

ddd = 0