import pymongo as pm
import Public
import os
import datetime as dt
import hashlib

def SenVec(sentence, parseModel = 2):
    vec = []
    if isinstance(parseModel, int):
        for i in range(len(sentence) - 1):
            vec.append(sentence[i : i + parseModel])
        return vec
    else:
        temp = parseModel.cut(sentence)
        for t in temp:
            vec.append(t[0])
    return vec

def SimHash(senVec, length = 64):
    accum = [0] * length
    simhash = ''
    for word in senVec:
        m16 = hashlib.md5(word.encode('utf-8')).hexdigest()
        m10 = int(int(m16, 16) / (2 ** (128 - length)))
        m2 = bin(m10)[2 : ]
        wordHash = [0] * (length - len(m2))
        wordHash.extend(m2)

        for i in range(len(wordHash)):
            if wordHash[i] == '0':
                accum[i] -= 1
            elif wordHash[i] == '1':
                accum[i] += 1
    for i in range(len(accum)):
        simhash += ('1' if accum[i] > 1 else '0')
    return simhash

def HamDist(s0, s1):
    hd = 0
    for i in range(max(len(s0), len(s1))):
        if s0[i] != s1[i]:
            hd += 1
    return hd

class DocInfo:
    def __init__(self, id, simhash, time, notDup = True):
        self.id = id
        self.simhash = simhash
        self.time = time
        self.notDup = notDup
        self.shSeg = [simhash[0 : 16], simhash[16 : 32], simhash[32 : 48], simhash[48 : 64]]
        self.slave = []


class RemoveDuplicate:
    def __init__(self, docInfoList, initRem = False):
        '''
        构造一个去重器
        :param docInfoList: 初始文档信息list
        :param initRem: 是否对docInfoList中的文档进行去重标记，如果True可能会花较多时间来构造对象，如果False也不会影响新加入的文档的重复性判断
        '''
        self.docInfoList = docInfoList
        self.shSegDict = [{}, {}, {}, {}]
        for docInfo in docInfoList:
            self.AddShSegDict(docInfo)
        if initRem:
            ccc = 0
            for docInfo in docInfoList:
                self.IsNotDup(docInfo)
                print(ccc)
                ccc += 1

    def AddShSegDict(self, docInfo):
        for i in range(len(self.shSegDict)):
            if docInfo.shSeg[i] not in self.shSegDict[i].keys():
                self.shSegDict[i][docInfo.shSeg[i]] = []
            self.shSegDict[i][docInfo.shSeg[i]].append(docInfo)

    def IsNotDup(self, docInfo):
        '''
        判断文档是否不是其他文档的副本
        :param docInfo: 文档信息
        :return: 如果是其他文档副本，则返回找到的一个已存在的与之重复的文档的id，否则返回None
        '''
        # 找到所有hash片段相等的文档作为候选
        eqShSeg = []
        for i in range(len(self.shSegDict)):
            eqShSeg.extend(self.shSegDict[i][docInfo.shSeg[i]])
        # print('cand ' + str(len(eqShSeg)))
        # 在候选中遍历
        for cand in eqShSeg:
            if cand.notDup == True and docInfo.time >= cand.time and \
               HamDist(docInfo.simhash, cand.simhash) <= 3 and \
               cand.id != docInfo.id :
                   cand.slave.extend([docInfo])
                   cand.slave.extend(docInfo.slave)
                   docInfo.slave = []
                   docInfo.notDup = False
                   return cand.id
        docInfo.notDup = True
        return None

    def AddDoc(self, docInfo):
        '''
        添加一个文档并判断其是否不是其他文档的副本
        :param docInfo: 文档信息
        :return: 如果是其他文档副本，则返回找到的一个已存在的与之重复的文档的id，否则返回None
        '''
        self.docInfoList.append(docInfo)
        self.AddShSegDict(docInfo)
        return self.IsNotDup(docInfo)

def GetDupRem(db, days, initRem):
    docs = db.section.find({'time': {'$gte': dt.datetime.now() - dt.timedelta(days=days)}})
    docInfoList = []
    for doc in docs:
        docInfoList.append(DocInfo(doc['_id'], doc['simhash'], doc['time'], notDup=True))
    rem = RemoveDuplicate(docInfoList, initRem)
    return rem


dbConfig = Public.GetPara(os.path.join('.', 'config', 'db.txt'))
mc = pm.MongoClient(dbConfig['mongoConn'])
db = mc['text']
# # 整体扫描去重----------------------------------------
# d0 = dt.datetime.now()
# rem = GetDupRem(db, 120, True)  # 在最近120天范围内去重
#
# docDict = {}
# for doc in rem.docInfoList:
#     docDict[doc.id] = doc
# ccc = 0
# for doc in rem.docInfoList:
#     docSec = db['section'].find_one({'_id': doc.id})
#     if doc.notDup:
#         docSec['masterId'] = ''
#         slaveList = []
#         for slave in doc.slave:
#             slaveList.append(slave.id)
#         docSec['slave'] = slaveList
#         db['section'].save(docSec)
#         for slave in doc.slave:
#             slaveSec = db['section'].find_one({'_id': slave.id})
#             slaveSec['masterId'] = doc.id
#             slaveSec['slave'] = []
#             db['section'].save(slaveSec)
#     print(dt.datetime.now())
#     print(str(ccc) + '/' + str(len(rem.docInfoList)))
#     ccc += 1
# -----------------------------------------------------


# sections = db.section.find({'time': {'$gte': dt.datetime.now() - dt.timedelta(days=90)}})
# secDict = {}
# for sec in sections:
#     if sec['masterId'] == '':
#         secDict[sec['_id']] = sec
ddd = 0
