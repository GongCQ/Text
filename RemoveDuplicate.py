import pymongo as pm
import Public
import os
import datetime as dt

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
    def __init__(self, docInfoList):
        self.docInfoList = docInfoList
        self.shSegDict = [{}, {}, {}, {}]
        for docInfo in docInfoList:
            for i in range(len(self.shSegDict)):
                if docInfo.shSeg[i] not in self.shSegDict[i].keys():
                    self.shSegDict[i][docInfo.shSeg[i]] = []
                self.shSegDict[i][docInfo.shSeg[i]].append(docInfo)
        ccc = 0
        for docInfo in docInfoList:
            print(ccc)
            ccc += 1
            docInfo.notDup = self.IsNotDup(docInfo)

    def IsNotDup(self, docInfo):
        # 找到所有hash片段相等的文档作为候选
        eqShSeg = []
        for i in range(len(self.shSegDict)):
            eqShSeg.extend(self.shSegDict[i][docInfo.shSeg[i]])
        print('cand ' + str(len(eqShSeg)))
        # 在候选中遍历
        for cand in eqShSeg:
            if cand.notDup == True and docInfo.time >= cand.time and \
               HamDist(docInfo.simhash, cand.simhash) <= 3 and \
               cand.id != docInfo.id :
                   cand.slave.extend([docInfo])
                   cand.slave.extend(docInfo.slave)
                   docInfo.slave = []
                   docInfo.notDup = False
                   return False
        docInfo.notDup = True
        return True

    def AddDoc(self, docInfo):
        self.docInfoList.append(docInfo)
        for i in range(len(self.shSegDict)):
            if docInfo.shSeg[i] not in self.shSegDict[i].keys():
                self.shSegDict[i][docInfo.shSeg[i]] = []
            self.shSegDict[i][docInfo.shSeg[i]].append(docInfo)
        docInfo.notDup = self.IsNotDup(docInfo)

def GetDupRem(db, days):
    docs = db.section.find({'time': {'$gte': dt.datetime.now() - dt.timedelta(days=days)}})
    docInfoList = []
    for doc in docs:
        docInfoList.append(DocInfo(doc['_id'], doc['simhash'], doc['time'], notDup=True))
    rem = RemoveDuplicate(docInfoList)
    return rem

dbConfig = Public.GetPara(os.path.join('.', 'config', 'db.txt'))
mc = pm.MongoClient(dbConfig['mongoConn'])
db = mc['text']
d0 = dt.datetime.now()
rem = GetDupRem(db, 7)
d1 = dt.datetime.now()
print(d0)
print(d1)

masterDocList = []
for docInfo in rem.docInfoList:
    if docInfo.notDup:
        masterDocList.append(docInfo)
ddd = 0
