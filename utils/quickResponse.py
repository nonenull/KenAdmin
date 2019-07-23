# coding=utf-8
import sys

from django.db import IntegrityError
from django.http import HttpResponse, JsonResponse
from django.views.debug import technical_500_response
import logging

from entrance.automate.perms import errorPage

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class QuickResponseError(Exception):
    """
    此异常类只要用于发生异常的时候, 直接给 http 返回异常结果
    在中间件捕获此异常类型, 做二次处理
    """

    def __init__(self, status=400, message="无", request=None, exception=None, *args, **kwargs):
        self.status = status
        self.message = message
        self.request = request
        self.exception = exception
        super().__init__(*args)
        self.preInit()
        logger.debug('message=========== %s %s %s %s', self.message, type(self.message), args, kwargs)

    def preInit(self):
        if self.exception:
            self.message = self.exception.args

        if isinstance(self.message, (list, tuple)):
            tmp = ''
            for i in self.message:
                tmp += ' {}'.format(i)
            self.message = tmp
        elif isinstance(self.message, dict):
            tmp = []
            for k, v in self.message.items():
                tmp.append("{}: {}".format(k, v))
            self.message = "\n".join(tmp)

        self.generateHumenMessage()

    def generateHumenMessage(self):
        """
        检查部分异常类型, 将异常信息转为比较好理解的文本
        :return:
        """
        if isinstance(self.exception, IntegrityError) and 'Duplicate entry' in self.message:
            self.message = self.message.replace('Duplicate entry', '值检测到重复, 请修改')

    def response(self):
        if isinstance(self.message, dict):
            return JsonResponse(self.message, status=self.status)
        if self.request.is_ajax():
            return HttpResponse(self.message, status=self.status)
        else:
            return errorPage(self.request, self.message, status=self.status)

    def verboseResponse(self, request):
        return technical_500_response(request, *sys.exc_info())
