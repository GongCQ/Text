import pymongo as pm
import Public
import os
import datetime as dt

def ValidWord1(word):
    if not ('\u4e00' <= word[0] <= '\u9fff' or '\u4e00' <= word[-1] <= '\u9fff') and \
       not ('\u0041' <= word[0] <= '\u005a' or '\u0041' <= word[-1] <= '\u005a') and \
       not ('\u0061' <= word[0] <= '\u007a' or '\u0061' <= word[-1] <= '\u007a'): # 头尾都不是汉字或字母
        return False
    return True

def ValidWord(word):
    if len(word) <= 1:
        return False
    return ValidWord1(word)

def SecTheme(sec, themeSet):
    '''
    输入一个section，将此section分句，并统计词频
    :param sec: section对象
    :param themeSet: 主题词集合，包含在此集合内的词被视作主题词，一定会被统计频率（其他一些比较碎的词或者数字符号等可能不会被统计）
    :return: wordFreq: 词频, dict类型, key为词, value为词出现的次数;    sentences: 句子, dict类型, key为句子的序号, value为句子内容及句子分词
    '''
    wordFreq = {}
    sentences = {}
    seq = 0
    sentence = ''
    parse = []
    parseFilter = []
    parseFilter1 = []
    for word in sec['parse']:
        # 统计词频
        if word in themeSet or ValidWord(word):
            word = word.replace('.', '_').replace('$', '^').replace('\0', '') # mongodb中作为键的特殊字符要替换掉
            if word not in wordFreq.keys():
                wordFreq[word] = 1
            else:
                wordFreq[word] += 1
        # 分句
        if word != '\n' and word != '\u3000':
            sentence += word
            parse.append(word)
            if word in themeSet or ValidWord(word):
                parseFilter.append(word)
            if word in themeSet or ValidWord1(word):
                parseFilter1.append(word)
        if word == '。' or word == '！' or word == '？' or word == '；' or word == '\n' or word == '\u3000': # 分句符
            if len(sentence) > 0:
                sentences[str(seq)] = {'seq': seq, 'sentence': sentence,
                                       'parse': parse, 'parseFilter': parseFilter, 'parseFilter1': parseFilter1}
                seq += 1
                sentence = ''
                parse = []
                parseFilter = []
                parseFilter1 = []

    return wordFreq, sentences

def ToDB(db, themeSet, updateTime = None):
    '''
    将SecTheme中统计的wordFreq和sentences写入数据库，表名分别为这两个名字
    :param db: mongo数据库对象
    :param themeSet: 主题词集合
    :param updateTime: 上次更新时间，只对此时间之后的文档进行处理，如果将此参数设置为None，将自动从数据库中读取上次保存的更新时间
    :return:
    '''
    if updateTime is None:
        updateTime = db['CONFIG'].find_one({'_id': 'THEME_UPDATE'})['updateTime']
    sections = db['section'].find({'time': {'$gte': updateTime}})
    maxTime = dt.datetime(2000, 1, 1)
    count = 0
    for sec in sections:
        wordFreq, sentences = SecTheme(sec, themeSet)
        wordFreq['_id'] = sec['_id']
        sentences['_id'] = sec['_id']
        db['wordFreq'].save(wordFreq)
        db['sentence'].save(sentences)
        maxTime = sec['time'] if sec['time'] > maxTime else maxTime
        count += 1
    maxTime = dt.datetime.strptime(maxTime.strftime('%Y-%m-%d'), '%Y-%m-%d')  # 转换为日期
    db['CONFIG'].save({'_id': 'THEME_UPDATE', 'updateTime': maxTime})
    return count

def ThemeCluster(db, themeSet):
    '''
    主题类统计并写入数据库，每个主题词被视作一个类，统计各类下有那些section（一个section中出现了该主题词就认为属于该类）
    分别按2/7/30/90天这四个时间范围统计，对应数据库中themeCluster2/themeCluster7/themeCluster30/themeCluster90这四个集合
    :param db: mongo数据库对象
    :param themeSet: 主题词集合
    :return:
    '''
    maxDays = 90
    date = dt.datetime.now() - dt.timedelta(days = maxDays)
    sections = db['section'].find({'time': {'$gte': date}})
    themeClusterDict = {90: {}, 30: {}, 7: {}, 2: {}}
    for days, themeCluster in themeClusterDict.items():
        for theme in themeSet:
            themeCluster[theme] = []
    for sec in sections:
        if sec['masterId'] != '':  # 不记录重复的文档
            continue
        wordFreq = db['wordFreq'].find_one({'_id': sec['_id']})
        for word in wordFreq.keys():
            if word in themeSet:
                for days, themeCluster in themeClusterDict.items():
                    if sec['time'] >= dt.datetime.now() - dt.timedelta(days=days):
                        themeCluster[word].append([sec['_id'], wordFreq[word]])
    for days, themeCluster in themeClusterDict.items():
        db['themeCluster' + str(days)].drop()  # 把之前的统计全部删掉
        for word, secIdList in themeCluster.items():
            db['themeCluster' + str(days)].save({'_id': word, 'sections': secIdList})
    ddd = 0


# dbConfig = Public.GetPara(os.path.join('.', 'config', 'db.txt'))
# mc = pm.MongoClient(dbConfig['mongoConn'])
# db = mc['text']
# themeSet = Public.FileToSet(os.path.join('.', 'dict', 'dict'))
# count = ToDB(db, themeSet, updateTime = None)
# print(count)
# ThemeCluster(db, themeSet)
