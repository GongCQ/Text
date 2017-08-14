import NewsEs
import datetime as dt
import Public
import redis
import os
import News


dbConfig = Public.GetPara(os.path.join('.', 'config', 'db.txt'))
conn = redis.StrictRedis(host=dbConfig['host'], port = dbConfig['port'], db = int(dbConfig['db']), decode_responses = True)

News.WriteLog('LAUNCH')

NewsEs.Launch(conn)
ddd = 0