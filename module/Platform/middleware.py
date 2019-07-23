# coding=utf-8
from django.contrib.auth.models import AnonymousUser

from entrance.mySettings import InternalUsers
from django.utils.deprecation import MiddlewareMixin

import logging

from entrance.urls import debugKey
from utils.quickResponse import QuickResponseError

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class PlatformMiddleware(MiddlewareMixin):
    def process_exception(self, request, exception):
        """
        处理请求错误， 配置一个内置用户， 在生产模式下内置用户依然可以获取调试信息
        :param request:
        :param exception:
        :return:
        """
        logger.exception(exception)
        if isinstance(exception, QuickResponseError):
            exp = exception
        else:
            logger.debug("中间件抓取到一个普通异常")
            exp = QuickResponseError(500, exception=exception)
        exp.request = request

        if request.user.username not in InternalUsers:
            return exp.response()
        else:
            return exp.verboseResponse(request)


def showToolbar(request):
    """
    判断是否需要显示 debug 栏
    """
    if debugKey not in request.path:
        return False
    if not request.user or isinstance(request.user, AnonymousUser):
        return False
    if request.user.isSuperUser or request.user.username in InternalUsers:
        return True

    return False
