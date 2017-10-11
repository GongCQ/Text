import NewsEs
import datetime as dt
import Public
import redis
import os
import News
import time
import pymongo as pm

def Launch():
    dbConfig = Public.GetPara(os.path.join('.', 'config', 'db.txt'))
    # conn = redis.StrictRedis(host=dbConfig['host'], port=dbConfig['port'], db=int(dbConfig['db']),
    #                          decode_responses=True)
    conn = pm.MongoClient(dbConfig['mongoConn'])  # 链接
    conn = conn['text']

    News.WriteLog('LAUNCH')

    NewsEs.Launch(conn)
    ddd = 0

Launch()
# while True:
#     if dt.datetime.now().hour == 7 and dt.datetime.now().minute <= 2:
#         print(str(dt.datetime.now()) + ' LAUNCH')
#         Launch()
#     time.sleep(30)
#     print('sleep to ' + str(dt.datetime.now()))