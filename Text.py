import NewsEs
import datetime as dt
import Public
import redis
import os
import News
import time

def Launch():
    dbConfig = Public.GetPara(os.path.join('.', 'config', 'db.txt'))
    conn = redis.StrictRedis(host=dbConfig['host'], port=dbConfig['port'], db=int(dbConfig['db']),
                             decode_responses=True)

    News.WriteLog('LAUNCH')

    NewsEs.Launch(conn)
    ddd = 0

while True:
    if dt.datetime.now().hour == 7 and dt.datetime.now().minute <= 10:
        print(str(dt.datetime.now()) + ' LAUNCH')
        Launch()
    time.sleep(60)
    print('sleep to ' + str(dt.datetime.now()))