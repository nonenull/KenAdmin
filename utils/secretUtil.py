# coding=utf-8
import random


def getRandPassword(digit=12):
    """
    生成一个随机密码
    :param digit: 密码位数
    :return:
    """
    return "".join(random.sample('1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()', digit))
