# coding=utf-8
from functools import wraps
from apps.Platform.models import Log


def taskDecorator(func):
    """
    为异步task添加一层装饰器, 加一层日志记录
    :param func:
    :return:
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        logObj = Log()
        logObj.module = '%s.%s' % (func.__module__, func.__name__)
        logObj.type = Log.Type.Tasks
        logObj.method = Log.Method.Create
        try:
            result = func(*args, **kwargs)
            logObj.status = Log.Status.Success
            logObj.message = result or {}
            logObj.save()
            return result
        except Exception as e:
            logObj.status = Log.Status.Fail
            logObj.message = str(e) + str(args) + str(kwargs)
            logObj.save()
            return e

    return wrapper
