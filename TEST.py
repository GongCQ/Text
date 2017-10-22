import News
import os
import Public
import numpy as np
import thulac
import pymongo as pm
import gensim as gs
import datetime as dt

dbConfig = Public.GetPara(os.path.join('.', 'config', 'db.txt'))
mc = pm.MongoClient(dbConfig['mongoConn'])
db = mc['text']

sections = db['section'].find({'time': {'$gte': dt.datetime(2017,10,14)}})
slaves = []
masters = []
for sec in sections:
    if sec['masterId'] != '':
        slaves.append(sec)
    else:
        masters.append(sec)

ddd = 0