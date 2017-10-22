# 句子摘要
import os
import Public
import numpy as np
import pymongo as pm
import gensim as gs
import datetime as dt

dbConfig = Public.GetPara(os.path.join('.', 'config', 'db.txt'))
mc = pm.MongoClient(dbConfig['mongoConn'])
db = mc['text']
theme = '东旭光电'
days = 30
themeSecId = db['themeCluster' + str(days)].find_one({'_id': theme})
senList = []
for secId in themeSecId['sections']:
    sentence = db['sentence'].find_one({'_id': secId[0]})
    for seq, sen in sentence.items():
        if seq == '_id':
            continue
        words = []
        for word in sen['parseFilter1']:
            words.append(word)
        senList.append(words)