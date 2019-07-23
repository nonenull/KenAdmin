# coding=utf-8
from django.core.cache import cache
from django_redis import get_redis_connection

import logging

logger = logging.getLogger(__name__)

DefalutExpireTime = 60 * 60 * 24 * 30


def updateCache(key, func, *args, **kwargs):
    value = cache.get(key)
    if not value:
        value = func(*args, **kwargs)
        cache.set(key, value, DefalutExpireTime)
    return value


def delMonitorKeys(dataId):
    """
    删除包含某ID的所有key
    主要用来更新监控缓存
    :param dataId:
    :return:
    """
    r = get_redis_connection('monitor')
    keys = r.keys('*:{}'.format(dataId))
    logger.info("准备删除key: %s", keys)
    for key in keys:
        r.delete(key)
