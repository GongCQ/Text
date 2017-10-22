import redis
import pymongo as pm
import thulac
import os
import Public

dbConfig = Public.GetPara(os.path.join('.', 'config', 'db.txt'))
conn = redis.StrictRedis(host=dbConfig['host'], port=dbConfig['port'], db=int(dbConfig['db']),
                             decode_responses=True)
mc = pm.MongoClient('mongodb://gongcq:gcq@localhost:27017/text')
db = mc['text']
tl = thulac.thulac(user_dict = os.path.join('.', 'dict', 'dict'), filt = False, seg_only=True)

config = conn.hgetall('CONFIG_ES')
config['_id'] = 'CONFIG_ES'
db['CONFIG'].save(config)
keys = conn.keys()
count = 0
for key in keys:
    if len(key) <= 7 or key[0 : 7] != 'http://':
        continue
    try:
        item = conn.hgetall(key)
    except Exception as e:
        ddd = 0
    item['_id'] = key
    if key[len(key) - 2] == ',' or key[len(key) - 3] == ',': # parse
        parse = []
        cut = tl.cut(item['content'])
        for c in cut:
            parse.append(c[0])
        item['parse'] = parse
        item['type'] = 'section'
        col = db['section']
        col.save(item)
    else:
        item['type'] = 'news'
        col = db['news']
        col.save(item)
    count += 1
    print(count)

