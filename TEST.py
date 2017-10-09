import News
import os
import Public
import redis
import numpy as np
import thulac

dbConfig = Public.GetPara(os.path.join('.', 'config', 'db.txt'))
conn = redis.StrictRedis(host=dbConfig['host'], port = dbConfig['port'], db = int(dbConfig['db']), decode_responses = True)
kwSet = Public.FileToSet(os.path.join('.', 'dict', 'keyword'))

tt = thulac.thulac(user_dict = os.path.join('.', 'dict', 'stock'), filt = False, seg_only=True)
tt1 = thulac.thulac(user_dict = os.path.join('.', 'dict', 'stock'), filt = False, seg_only=True, model_path='/usr/local/lib/python3.5/site-packages/thulac/models_3/')
tf = thulac.thulac(user_dict = os.path.join('.', 'dict', 'stock'), filt = False, seg_only=False)
tf1 = thulac.thulac(user_dict = os.path.join('.', 'dict', 'stock'), filt = False, seg_only=False, model_path='/usr/local/lib/python3.5/site-packages/thulac/models_3/')
ss0 = '据中电联数据，1-8月全国新增光伏装机达到38.28GW，其中7-8两个月新增装机13.88GW，大幅超过市场预期，其中分布式新增14.43GW，同比增长超过200%'
ss1 = '公司电站系统集成业务快速发展，户用分布式有望爆发式增长，逆变器业务稳定推进，储能发展潜力大，预计17-19年EPS分别为0.62/0.93/1.15元/股，当前价格下，对应PE分别为26.3X/17.5X/14.2X，给予买入评级。'
ss2 = '根据在线空旅网站Routehappy的测算，目前飞机上Wifi已经覆盖了全球航班中超过三分之一(39%)的航程，其中美国的航空公司已有71%的航程实现Wifi全覆盖，而这一比例在非美国的航空公司中仅为13%。'
ss3 = '统计发现，上述6只概念股中，近30日内有4只个股获得机构给予“买入”或“增持”等看好评级，其中，星网锐捷近30日内机构看好评级家数为15家，北纬科技期间机构看好评级家数为5家，蓝色光标期间机构看好评级家数为4家，万集科技期间机构看好评级家数为3家。'
s = ss3
ct = tt.cut(s)
ct1 = tt1.cut(s)
cf = tf.cut(s)
cf1 = tf1.cut(s)
ddd = 0
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
#         conn.delete(key)
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

# keys = conn.keys('http*')
# for key in keys:
#     lk = len(key)
#     if key[lk - 2] == ',':
#         bias = 2
#     elif key[lk - 3] == ',':
#         bias = 3
#     else:
#         continue
#     news = conn.hgetall(key)
#     title = news['title']
#     secTitle = news['secTitle']
#     time = news['time']
#     url = news['url']
#     content = news['content']
#     try:
#         t = os.path.join('textFile', (time.replace(':', '.') + ' ' + title + ' ' + secTitle).replace('/', '_'))
#         if len(t) >= 50:
#             t = t[0 : 50]
#         file = open(t, 'w')
#         file.write(url + '\r\n\n')
#         file.write(content)
#         file.flush()
#     except Exception as e:
#         ddf = 0