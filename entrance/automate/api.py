# coding=utf-8
import datetime
import logging

from django.http import JsonResponse

from module.Platform.models import ApiLog

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def getClientIp(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def record(typeName):
    def _record(func):
        def wrapper(request):
            logger.debug("func===%s", func)
            timenow = datetime.datetime.now()
            log = ApiLog()
            log.apiType = typeName
            log.requestIp = getClientIp(request)
            log.requestTime = timenow
            log.request = request.POST.dict()

            try:
                responseText = func(request)
            except Exception as e:
                logger.exception("API %s 执行出现错误: %s", request.path, e)
                responseText = {
                    'code': 500,
                    'error': str(e),
                    'message': None,
                }

            log.response = responseText

            try:
                jsonResponse = JsonResponse(responseText)
            except Exception as e:
                logger.exception("%s生成API结果出现错误: %s", request.path, e)
                responseText = {
                    'code': 500,
                    'error': str(e),
                    'message': None,
                }
                log.response = responseText
                jsonResponse = JsonResponse(responseText)

            log.save()
            logger.debug("!~~~~~~~~~~~~~~~~~~~~~~~~ jsonResponse: %s", jsonResponse)
            return jsonResponse
        return wrapper
    return _record
