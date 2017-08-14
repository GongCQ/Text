import os
import Public
import redis
import thulac
import datetime as dt

dbConfig = Public.GetPara(os.path.join('.', 'config', 'db.txt'))
conn = redis.StrictRedis(host=dbConfig['host'], port = dbConfig['port'], db = int(dbConfig['db']), decode_responses = True)
conn1= redis.StrictRedis(host=dbConfig['host'], port = dbConfig['port'], db = 1, decode_responses = True)

stockSet = Public.FileToSet(os.path.join('.', 'dict', 'stock'))

tl = thulac.thulac(user_dict = os.path.join('.', 'dict', 'stock'), filt = False, seg_only=True)
# tl1= thulac.thulac(user_dict = os.path.join('.', 'dict', 'stock'), filt = True , seg_only=True)
secKeys = conn.smembers('SECTION_BUFFER')
time = dt.datetime.now()
seq = 0
for key in secKeys:
    seq += 1
    rltStock = set()
    kwSet = set()
    sec = conn.hgetall(key)
    content = sec['content']
    url = sec['url']
    cut = tl.cut(content)
    # cut1= tl1.cut(content)
    # 统计出现的股票
    for c in cut:
        kw = c[0]
        if kw in stockSet:
            rltStock.add(kw)
        else:
            kwSet.add(kw)
    # 将出现的股票加入到每个关键字的股票集合中，并记录关联的url
    for c in cut:
        kw = c[0]
        for stock in rltStock:
            conn.zincrby(kw, stock, 1)
    for kw in kwSet:
        for stock in rltStock:
            conn1.zincrby(kw, stock, 1)
            # conn.sadd(kw + '_' + stock, url)

    newTime = dt.datetime.now()
    print(seq)
    print(len(content))
    print(len(cut))
    print(newTime - time)
    time = newTime
    dd = 0