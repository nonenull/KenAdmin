# coding=utf-8
import cx_Oracle
import datetime
from decimal import Decimal


def MySQLConverter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()

    if isinstance(o, Decimal):
        return format(o, '0.2f')

    return str(0)


def OracleConverter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()

    if isinstance(o, cx_Oracle.STRING):
        return o.__str__()

    return str(0)
