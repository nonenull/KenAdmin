# coding=utf-8
import pickle

from django import template
from django.template.defaultfilters import date, safe
from django.urls import reverse, NoReverseMatch

from module.Platform.config import Table as TableHelpText
from utils.convUtil import conv

from entrance.automate.query import FieldsParser
import logging
from ast import literal_eval

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

register = template.Library()


@register.filter
def formatDate(dateStr):
    return date(dateStr, "Y-m-d H:i:s")


@register.filter
def replace(rStr, replaceVar):
    return rStr.replace(
        *literal_eval(replaceVar)
    )


@register.filter
def convUnit(queryset, name):
    """
    根据配置的转换单位进行换算
    :param queryset:
    :param name:
    :return:
    """
    fieldsParser = FieldsParser(queryset)
    value = fieldsParser.getValue(name)

    helpText = fieldsParser.getField(name, key='help_text')
    tableKey = TableHelpText.__name__
    tableInfo = helpText.get(tableKey)
    if tableInfo:
        tableInfo = pickle.loads(tableInfo)
    else:
        tableInfo = TableHelpText()

    unit = tableInfo.unit
    toUnit = tableInfo.toUnit
    if unit and toUnit:
        return '%s %s' % (conv(value, unit, toUnit), toUnit)
    logger.debug('convUnit 没有找到换算单位')
    return value


@register.filter
def generateLineFeed(lists):
    """
    生成换行
    :return:
    """
    html = ''
    p = '<p>%s</p>'
    for i in lists:
        html += p % i
    return safe(html)


@register.filter
def generateBadge(obj, fieldName):
    """
    为数据生成徽章
    :param obj:
    :param fieldName:
    :return:
    """
    item = '<span class="layui-badge %s">%s</span>'
    # choices类格式必须是相应字段的大驼峰
    badgeDict = getattr(obj, fieldName[0].upper() + fieldName[1:]).Badge
    fieldVal = getattr(obj, fieldName)
    fieldDisplayVal = getattr(obj, 'get_%s_display' % fieldName)()
    badge = badgeDict.get(fieldVal)

    html = item % (badge, fieldDisplayVal)
    return safe(html)


@register.filter
def generateUrlVariable(request, name=None):
    """
    :param request: request
    :param name: url 变量名
    :return:
    """
    resolverMatch = request.resolver_match
    urlName = resolverMatch.url_name
    namespace = resolverMatch.namespace
    url = ''
    try:
        url = reverse('{}:{}.{}'.format(namespace, urlName, name))
    except NoReverseMatch:
        try:
            url = reverse('{}:{}.{}'.format(namespace, urlName, name), args=(0,))
        except NoReverseMatch:
            pass
    return url


@register.filter
def getType(var):
    logger.debug("var======= %s", var)
    return str(type(var))


@register.filter
def checkType(var, varType):
    logger.debug("var======= %s", var)
    return isinstance(var, eval(varType))
