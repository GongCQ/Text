# 相似文档
import os
import Public
import numpy as np
import pymongo as pm
import gensim as gs
import datetime as dt

dbConfig = Public.GetPara(os.path.join('.', 'config', 'db.txt'))
mc = pm.MongoClient(dbConfig['mongoConn'])
db = mc['text']

days = 30
sections = db['section'].find({'time': {'$gte': dt.datetime.now() - dt.timedelta(days=days)}})
secParseList = []
secList = []
# ============================================
# 文档
for sec in sections:
    if sec['masterId'] != '':  # 重复文档，跳过
        continue
    parse = sec['parse']
    wordList = []
    for word in parse:
        if Public.ValidWord1(word):
            wordList.append(word)
    secList.append(sec)
    secParseList.append(wordList)
# --------------------------------------------
# # 主题句子
# theme = '航运'
# themeSecId = db['themeCluster' + str(days)].find_one({'_id': theme})
# for secThemeFreq in themeSecId['sections']:
#     secId = secThemeFreq[0]
#     sec = db['section'].find_one({'_id': secId})
#     if sec['masterId'] != '': # 目前重复的文档都会存入themeCluster中，将来如果重复的不存入，这个判断就可以不要
#         continue
#     sentence = db['sentence'].find_one({'_id': secId})
#     for seq, sen in sentence.items():
#         if seq == '_id':
#             continue
#         words = []
#         for word in sen['parseFilter1']:
#             words.append(word)
#         secList.append({'content': sen['sentence'], 'url': sec['url']})
#         secParseList.append(words)
# ============================================

# 将词编号
dic = gs.corpora.Dictionary(secParseList)
for token, id in dic.token2id.items():
    dic.id2token[id] = token
# 将每篇以分词向量存储的文档转换为二元组向量，二元组为(词编号,词频率)的形式
corpus = [dic.doc2bow(sec) for sec in secParseList]

# 计算各文档中词的tfidf值
tfIdf = gs.models.TfidfModel(corpus)  # tfidf模型
tiList = []
for c in range(len(corpus)): # cor in corpus:
    cor = corpus[c]
    ti = tfIdf[cor]  # 输入一个二元组向量，返回其中各词的tfidf值，这里还是在用词编号表示词
    tiDict = {}
    for i in range(len(ti)):  # 将词编号还原成词
        ti[i] = (dic.id2token[ti[i][0]], ti[i][1])
        tiDict[ti[i][0]] = ti[i][1]
    tiSort = sorted(tiDict.items(), key=lambda d:d[1], reverse=True) # 按各词的tfidf降序排序
    secList[c]['tiSort']= tiSort
    tiList.append(tiSort)

# 用lsi模型将文档转换为向量，向量长度由num_topics指定
lsi = gs.models.LsiModel(corpus, id2word = dic, num_topics=100)  # lsi模型对象
docs = lsi[corpus]  # 用来表示文档特征的num_topics维向量
index = gs.similarities.MatrixSimilarity(docs)

def GetSim(seq, num = 20, corpus = corpus, secList = secList, model = lsi, index = index):
    '''
    查询与指定文档最相似的前20个文档并打印文档内容
    :param seq: 指定文档在secList中的序号
    :param corpus:
    :param secList:
    :param model:
    :param index:
    :return:
    '''
    query = lsi[corpus[seq]]
    queryDoc = secList[seq]
    print('===' + queryDoc['content'])
    sims = index[query]
    simsSort = np.argsort(-sims)
    simDocs = []
    for s in range(num): # simSeq in simsSort[0 : 20]:
        simSeq = simsSort[s]
        simDocs.append(secList[simSeq])
        print('[' + str(s) + ', ' + str(sims[simSeq]) + ']' + secList[simSeq]['content']) #  + ' ' + secList[simSeq]['url']
    return queryDoc, simDocs

queryDocm, sunDocs = GetSim(0)

ddd = 0