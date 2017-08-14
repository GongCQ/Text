import News
import os
import Public
import redis
import numpy as np

dbConfig = Public.GetPara(os.path.join('.', 'config', 'db.txt'))
conn = redis.StrictRedis(host=dbConfig['host'], port = dbConfig['port'], db = int(dbConfig['db']), decode_responses = True)
kwSet = Public.FileToSet(os.path.join('.', 'dict', 'keyword'))

# lll = conn.zrevrange('KW_SET', 0, 300000)

# keys = conn.keys()
# for key in keys:
#     if (len(key) <= 4 or key[0 : 4] != 'http') and key != 'CONFIG_ES' and key != 'SECTION_BUFFER':
#         conn.delete(key)

# keys = conn.keys()
# for key in keys:
#     if key[len(key) - 2] == ',' or key[len(key) - 3] == ',':
#         conn.sadd('SECTION_BUFFER', key)
#

# file = open('text.txt', 'w')
# f = open('key.txt', 'w')
# ccc = 0
# keys = conn.keys()
# for key in keys:
#     if (len(key) <= 4 or key[0: 4] != 'http') and key != 'CONFIG_ES' and key != 'SECTION_BUFFER':
#         if key == '公司':
#             dfdsfa= 0
#         ksTuple = conn.zscan(key, count = 4000)[1]
#         count = len(ksTuple)
#         scoreArr = np.nan * np.zeros([count])
#         for i in range(count):
#             s = ksTuple[i][1]
#             scoreArr[i] = s
#         std = np.std(scoreArr / np.max(scoreArr))
#         file.write(key + ',' + str(count) + ',' + str(std) + '\n')
#         if key in kwSet:
#             f.write(key + ',' + str(count) + ',' + str(std) + '\n')
#         ddd = 0
#         print(ccc)
#         ccc += 1
# file.flush()

keys = conn.keys('http*')
for key in keys:
    lk = len(key)
    if key[lk - 2] == ',':
        bias = 2
    elif key[lk - 3] == ',':
        bias = 3
    else:
        continue
    news = conn.hgetall(key)
    title = news['title']
    secTitle = news['secTitle']
    time = news['time']
    url = news['url']
    content = news['content']
    try:
        t = os.path.join('textFile', (time.replace(':', '.') + ' ' + title + ' ' + secTitle).replace('/', '_'))
        if len(t) >= 50:
            t = t[0 : 50]
        file = open(t, 'w')
        file.write(url + '\r\n\n')
        file.write(content)
        file.flush()
    except Exception as e:
        ddf = 0