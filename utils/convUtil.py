# coding=utf-8
from datetime import datetime
import time

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

"""
存放所有跟转换有关的函数
"""

StorageUnit = {
    'conv': 1024,
    'units': ['B', 'KB', 'MB', 'GB', 'TB', 'PB'],
}


def selectUnitDict(unit, toUnit):
    """
    根据提供的 unit 单位类型, 自动判断 获取 相应的 UnitDict 计算对象
    :return:
    """
    for k, v in globals().items():
        if not (k.endswith('Unit') and isinstance(v, dict)):
            continue
        units = v['units']
        if unit in units and toUnit in units:
            return v

    raise ValueError('找不到相应的单位计算对象')


def convs(val: list, unit, toUnit, unitType=None):
    tmp = []
    for i in val:
        tmp.append(
            conv(i, unit, toUnit, unitType=unitType)
        )
    return tmp


def conv(val, unit, toUnit, unitType=None):
    """
    转换函数
    :param val: 值
    :param unit: 当前单位
    :param toUnit: 转换单位
    :param unitType: 换算类型
    :return: 返回转换完的值
    """
    if not unitType:
        unitType = selectUnitDict(unit, toUnit)

    val = int(float(val))
    units = unitType['units']
    curUnitIndex = units.index(unit)
    toUnitIndex = units.index(toUnit)
    # 得到单位差
    unitDifference = toUnitIndex - curUnitIndex
    # 得到 换算单位的差距, 此处unitDifference需要获取绝对值
    unitGap = (unitType['conv'] ** abs(unitDifference))
    return unitDifference > 0 and val / unitGap or val * unitGap


def utcTimeToLocal(utcSt, format='%Y-%m-%dT%H:%MZ'):
    """
        UTC时间转本地时间（+8: 00
    ）"""
    if isinstance(utcSt, str):
        utcSt = datetime.strptime(utcSt, '%Y-%m-%dT%H:%MZ')
    stampNow = time.time()
    localTime = datetime.fromtimestamp(stampNow)
    utcTime = datetime.utcfromtimestamp(stampNow)
    offset = localTime - utcTime
    localSt = utcSt + offset
    return localSt


if __name__ == "__main__":
    utcTime = '2018-11-14T03:55Z'
    a = utcTimeToLocal(utcTime)
    print(a)
