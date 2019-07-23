# coding=utf-8
import datetime
import pickle
from collections import OrderedDict, Iterable
from django import template
from django.db.models import ForeignKey, ManyToOneRel, ManyToManyRel
from django.template import loader
from django.template.defaultfilters import truncatechars, safe
from django_mysql.models import JSONField, SetCharField, ListCharField

from apps.Platform.config import Table as HelpTextTable
from apps.Platform.templatetags.baseTag import generateBadge, formatDate
from apps.Platform.templatetags.formTag import FilterForm, Form
from utils.convUtil import conv
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
register = template.Library()


@register.tag
def Td(parser, token):
    split = token.split_contents()
    return TdNode(*split[1:])


class TdNode(template.Node):
    td = "<td %s>%s</td>"

    def __init__(self, queryset, headDict):
        self.querysetVar = template.Variable(queryset)
        self.headDictVar = template.Variable(headDict)
        self.TypeHandleList = OrderedDict({
            'proxy': self._handleProxy,
            'toUnit': self._handleUnit,
            'badge': self._handleBadge,
            'truncatechars': self._handleTruncatechars,
            'lineFeed': self._handleLineFeed,
        })

    def _renderRelatedField(self, name, field: ManyToOneRel):
        values = getattr(self.queryset, name).all()
        tmp = []
        for i in values:
            tmp.append(str(i))
        return self._handleLineFeed(tmp, fieldInfo=None)

    def render(self, context):
        self.queryset = self.querysetVar.resolve(context)
        self.headDict = self.headDictVar.resolve(context)

        html = ''
        # logger.debug('self.headDict==={}\n\n'.format(self.headDict))
        for name, fieldInfo in self.headDict.items():
            html += self.renderItem(name, fieldInfo)
        return safe(html)

    def renderItem(self, name, fieldInfo):
        title = ''
        field = fieldInfo.field
        if isinstance(field, ManyToOneRel):
            value = self._renderRelatedField(name, field)
            return self.td % (title, value)

        try:
            oldValue = getattr(self.queryset, name)
            if name == 'privateIp':
                logger.debug('\n\nprivateIp 处理之前的 value==={} \n\n'.format(oldValue, type(oldValue)))
        except Exception as e:
            if isinstance(field, ForeignKey) and e.__class__ == field.related_model.DoesNotExist:
                logger.warning("删了关联的脏数据 %s %s", self.queryset)
                values = self.queryset.delete()
                return self.td % (title, values)
            else:
                raise e.__class__(e)
        else:
            # logger.debug('原始 value =={}={}'.format(oldValue, type(oldValue)))
            value = self._handleType(
                name,
                oldValue,
                fieldInfo,
            )
            if name == 'privateIp':
                logger.debug('\n\nprivateIp 处理完之后的 value==={} \n\n'.format(value, type(value)))

            # 如果值是日期类型, 则先转化为日期
            if isinstance(oldValue, datetime.datetime):
                value = formatDate(value)
            # 私密字段不完全显示
            if fieldInfo.privacy is True:
                # 如果显示了密码字段, 则部分用**替代
                lenVal = len(value)
                value = value[:2] + "*" * lenVal

            # 当字段设置了超出字符数截断时, 添加一个 title 当提示
            if fieldInfo.truncatechars:
                title = 'title="%s"' % oldValue

            if value == "" or value is None or value == [] or value == set():
                value = "无"

            return self.td % (title, value)

    def _handleType(self, name, value, fieldInfo):
        """
        根据 help_text['table']['type'] 指定的类型, 做相应的处理
        :param value:
        :param head:
        :return:
        """
        fieldInfo.queryset = self.queryset
        # 先初始化一下 处理过 的状态
        isHandled = False
        for key, func in self.TypeHandleList.items():
            # logger.debug("func===", func)
            c = getattr(fieldInfo, key, None)
            if not c:
                continue
            isHandled = True
            value = func(value, fieldInfo)

        if not isHandled:
            field = fieldInfo.field
            choices = field.choices
            if choices:
                choicesClsName = name[0].upper() + name[1:]
                # 如果是带choices属性的字段且 choices类带有Badge属性, 则自动生成 徽章效果
                choicesObj = getattr(self.queryset, choicesClsName)
                if hasattr(choicesObj, "Badge"):
                    value = self._handleBadge(value, fieldInfo)
                elif isinstance(field, JSONField):
                    # 如果是JSONField类型的多选框
                    logger.debug("JSONField类型的多选框======%s", fieldInfo.name)
                    tmp = []
                    if not isinstance(value, list):
                        value = [value]
                    for v in value:
                        for cValue, cTitle in choices:
                            if v == cValue:
                                tmp.append(cTitle)
                    value = ','.join(tmp) or '无'
                    logger.debug('super value========== [%s]', value)
                else:
                    # 如果没有指定badge 且 带choices属性的字段, 则自动调用 get_xxx_display
                    value = getattr(self.queryset, 'get_{}_display'.format(fieldInfo.name))()
            else:
                if isinstance(field, (SetCharField, ListCharField)):
                    # logger.debug("value ======== %s  %s", value, type(value))
                    if value is not None:
                        if not isinstance(value, Iterable):
                            value = [value]
                        value = ';'.join(value)
        return value

    def _handleProxy(self, value, fieldInfo):
        """
        返回代理字段的值
        :param value:
        :param proxy:
        :param kwargs:
        :return:
        """
        proxy = fieldInfo.proxy
        return getattr(self.queryset, proxy)

    def _handleUnit(self, value, fieldInfo):
        toUnit = fieldInfo.toUnit
        return '%s %s' % (conv(value, unit=fieldInfo.unit, toUnit=toUnit), toUnit)

    def _handleBadge(self, value, fieldInfo):
        badgeVal = generateBadge(fieldInfo.queryset, fieldInfo.name)
        return badgeVal

    def _handleTruncatechars(self, value, fieldInfo):
        return truncatechars(value, fieldInfo.truncatechars or 20)

    def _handleLineFeed(self, values, fieldInfo):
        """
        比如有些字段是JSONField 值可能是list, 将其自动换行转成字符串
        :param value: 原始值
        :param fieldInfo: module.Platform.config.Form 对象
        :return:
        """
        html = ''
        p = '<p>%s</p>'
        if isinstance(values, Iterable):
            for i in values:
                if i == '':
                    continue
                html += p % i
        return html or '无'


@register.tag
def Table(parser, token):
    """

    :param parser:
    :param token: [Table, querysetName]
    :return:
    """
    split = token.split_contents()
    querysetName = split[1]
    return TableNode(querysetName)


class TableNode(template.Node):
    def __init__(self, querysetName):
        self.querysetVar = template.Variable(querysetName)

    def render(self, context):
        queryset = self.querysetVar.resolve(context)
        return self.renderTo(context.request, queryset, hasFilter=True)

    def renderTo(self, request, queryset, hasFilter=False):
        nameList, headDict = self.getHeadField(queryset)
        # logger.debug("nameList = ===== %s", nameList)

        if hasFilter:
            filterForm = FilterForm(queryset)
            self._getFilterData(headDict, filterForm)

        return loader.render_to_string('platform/table.html', {
            'querysetList': queryset,
            'headDict': headDict,
            'nameList': nameList,
        }, request=request, using=None)

    def _getFilterData(self, headDict, filterForm):
        """
        生成 filter form 表单原始信息
        FilterForm
        :param headDict:
        :param filterForm: [{字段名: 字段信息}]
        :return:
        """
        filterData = filterForm.getFilterData()
        for name, dates in headDict.items():
            if name not in filterData:
                continue
            filterItem = filterData[name]
            hasChoices = getattr(filterItem, 'choices', None)
            if hasChoices:
                headDict[name].filter = hasChoices
            else:
                headDict[name].filter = getattr(filterItem, 'options', None)

    def _getRelatedFieldInfo(self, field: ManyToOneRel):
        relatedField = field.field
        originalHelpText = relatedField.help_text
        _, tableConf = TableNode._getTableInfo(originalHelpText)
        helpText, formInfo = Form._getFormInfo(originalHelpText)
        if not formInfo.related:
            return None, None

        relatedName = field.get_accessor_name()
        logger.debug('relatedName=========== %s', relatedName)
        # name = field.name
        tableConf.name = relatedName
        tableConf.cname = field.related_model.__cname__
        tableConf.field = field
        return relatedName, tableConf

    @staticmethod
    def _getTableInfo(helpText):
        helpText = isinstance(helpText, dict) and helpText or {}
        tableInfo = helpText.get(HelpTextTable.__name__)
        if tableInfo:
            tableInfo = pickle.loads(tableInfo)
        else:
            tableInfo = HelpTextTable()

        return helpText, tableInfo

    def getHeadField(self, queryset):
        """
        获取表头的字段
        :param queryset:
        :return:
        """
        # id 为默认
        tableName = Table.__name__
        nameList = ['id']
        headDict = {}
        needMoveName = []
        for field in queryset.model._meta.get_fields():
            if isinstance(field, ManyToManyRel):
                continue

            if isinstance(field, ManyToOneRel):
                name, tableConf = self._getRelatedFieldInfo(field)
                if name and tableConf:
                    nameList.append(name)
                    needMoveName.append(name)
                    headDict[name] = tableConf
                continue

            helpText = field.help_text
            if not isinstance(helpText, dict) or tableName not in helpText:
                continue
            tableConf = helpText.get(tableName)
            if tableConf:
                tableConf = pickle.loads(tableConf)
            else:
                tableConf = HelpTextTable()

            name = field.name
            nameList.append(name)
            #
            tableConf.name = name
            tableConf.cname = tableConf.cname or field.verbose_name
            tableConf.field = field
            headDict[name] = tableConf
        # 将 反查外键的数据转移到数据中间的位置
        if needMoveName:
            newIndex = int(len(nameList) / 2)
            logger.debug("new index === %s", newIndex)
            for i in needMoveName:
                index = nameList.index(i)
                nameList.insert(newIndex, nameList.pop(index))
        # 根据 nameList的排序信息, 重新对 headDict 进行排序
        headDictOrder = OrderedDict()
        for i in nameList:
            if i in headDict:
                headDictOrder[i] = headDict.pop(i)
        return nameList, headDictOrder


@register.filter
def toTable(queryset, argsStr=''):
    return loader.render_to_string('platform/table.html', {
        'hosts': queryset
    }, using=None)
