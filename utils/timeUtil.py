# coding=utf-8
from datetime import datetime

import pytz
from dateutil import tz
from django.utils.timezone import localtime

from entrance.settings import TIME_ZONE

utc = pytz.UTC


def isUtcDatetime(datetime: datetime):
    """
    判断 时间是否为 utc 时间
    :return:
    """
    if datetime.tzinfo:
        return True
    return False


def utcTimeToLocal(dt: datetime):
    if isUtcDatetime(dt):
        return localtime(
            dt.astimezone(
                tz=tz.gettz(TIME_ZONE)
            )
        ).replace(tzinfo=None)
    return dt
