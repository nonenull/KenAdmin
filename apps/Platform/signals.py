# coding=utf-8
from django.dispatch import Signal

# 定义一个内部系统发消息的信号
sendMessageSighal = Signal(providing_args=[])
