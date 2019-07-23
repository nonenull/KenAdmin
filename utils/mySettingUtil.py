# coding=utf-8


def generateAttrList(cls, attr):
    pass


def getChild(cls):
    return {k: v for k, v in cls.__dict__.items() if not k.startswith('__')}


class MySettingUtil:
    @classmethod
    def child(cls):
        return getChild(cls)
