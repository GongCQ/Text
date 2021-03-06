import os
import News
import datetime as dt
import fileinput

def GetPara(path):
    paraDict = {}
    try:
        file = open(path)
        lines = file.readlines()
        for line in lines:
            try:
                if line[-1] == os.linesep:
                    line = line[0: len(line) - 1]
                strSplit = line.split(',')
                paraDict[strSplit[0]] = strSplit[1]
            except Exception as e:
                continue
    except Exception as e:
        News.WriteLog('Fail to open ' + os.path.join('.', 'config', 'es.txt'))
    finally:
        file.close()

    return paraDict

def SetPara(path, paraDict):
    try:
        file = open(path, 'w')
        for k, v in paraDict.items():
            file.write(k + ',' + v + os.linesep)
            file.flush()
    except Exception as e:
        News.WriteLog('Fail to open ' + os.path.join('.', 'config', 'es.txt'))
    finally:
        file.close()

def SetToFile(set, path):
    file = open(path, 'w')
    empty = True
    for s in set:
        if not empty:
            file.write(os.linesep)
        st = s.strip()
        if st != '':
            file.write(st)
            sn = s.replace(' ', '')
            if sn != st:
                file.write(os.linesep + sn)
            empty = False

def FileToSet(path):
    s = set()
    for line in fileinput.input(path):
        if line == '':
            continue
        if line[-1] == os.linesep:
            line = line[0 : len(line) - 1]
        s.add(line)
    return s

def ValidWord1(word):
    if not ('\u4e00' <= word[0] <= '\u9fff' or '\u4e00' <= word[-1] <= '\u9fff') and \
       not ('\u0041' <= word[0] <= '\u005a' or '\u0041' <= word[-1] <= '\u005a') and \
       not ('\u0061' <= word[0] <= '\u007a' or '\u0061' <= word[-1] <= '\u007a'): # 头尾都不是汉字或字母
        return False
    return True

def ValidWord(word):
    if len(word) <= 1:
        return False
    return ValidWord1(word)