# coding=utf-8
from django_redis import get_redis_connection
from entrance.celery import app
from apps.Platform.models import Log
from utils.api import getIPLocation
import logging

logger = logging.getLogger('tasks')
logger.setLevel(logging.DEBUG)


@app.task
def setLoginStatus(userId, sessionKey):
    """
    设置用户登录状态
    :param users:
    :return:
    """
    if not userId or not sessionKey:
        return
    r = get_redis_connection('default')
    r.set('logined:{}'.format(userId), sessionKey)


@app.task
def resetLoginStatus(*userIds: int):
    """
    重置用户登录状态
    将用户的session缓存删除
    :param users:
    :return:
    """
    for uid in userIds:
        r = get_redis_connection('default')
        sessionId = r.get('logined:{}'.format(uid))
        logger.debug("需要删除的session: %s %s", uid, sessionId)
        if sessionId:
            r.delete(sessionId)


@app.task
def getLoginIPLocation(logId, ip):
    loginArea = getIPLocation(ip)
    try:
        log = Log.objects.get(id=logId)
        log.message["area"] = loginArea
        log.save()
    except Log.DoesNotExist:
        logger.warning("log id: %s 不存在", logId)
    finally:
        return loginArea
