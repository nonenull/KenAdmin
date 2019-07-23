# coding=utf-8

def getChildCls(cls):
    clsDict = cls.__dict__
    result = []
    for k, v in clsDict.items():
        if str(k).startswith('__'):
            continue
        result.append(v)
    return result
