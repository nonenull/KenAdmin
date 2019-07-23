# coding=utf-8
import inspect

"""
存放所有跟堆栈有关的函数
"""


class Stack(object):
    def __init__(self, deepNum=1):
        self.stack = inspect.stack()
        self.frame = self.stack[deepNum][0]

    def getModule(self, name=True):
        mod = inspect.getmodule(self.frame)
        if name and mod:
            return mod.__name__
        else:
            return mod

    def getFuncName(self):
        return self.frame.f_code.co_name

    def getClass(self, name=True):
        selfVar = self.frame.f_locals.get('self')
        if not selfVar:
            return ''
        stackClass = selfVar.__class__
        if name:
            return stackClass.__name__
        else:
            return stackClass

    def __str__(self):
        stackClass = self.getClass()
        if not stackClass:
            return '{}.{}'.format(self.getModule(), self.getFuncName())
        return '{}.{}.{}'.format(self.getModule(), stackClass, self.getFuncName())
