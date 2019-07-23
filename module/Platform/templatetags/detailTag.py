# coding=utf-8
import ast
import datetime

from django import template
from django.db.models import ManyToOneRel, ManyToManyRel, AutoField, ManyToManyField, ForeignKey, TextField
from django.template.defaultfilters import safe
import logging

from django.urls import reverse

from module.Platform.templatetags.baseTag import formatDate
from module.Platform.templatetags.tableTag import TdNode, TableNode

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
register = template.Library()


@register.filter
def toDetail(queryset):
    detail = Detail(queryset)
    return safe(detail.render())


@register.filter
def toRelated(queryset, readOnly='True'):
    logger.debug("readOnly======%s", readOnly)
    related = Related(queryset, ast.literal_eval(readOnly))
    return safe(related.render())


class Related(object):
    html = """
        <div class="layui-tab layui-tab-brief" lay-filter="relatedTab">
            <ul class="layui-tab-title">
                {head}
            </ul>
            <div class="layui-tab-content">
                {content}
            </div>
            
        </div>
    """

    tabHeadItem = '<li class="{layThis}">{headName}</li>'
    tabHeadNameItem = '<i class="layui-icon layui-icon-bind"></i>'
    tabContentItem = """
        <div class="layui-tab-item {layShow}"><iframe lazySrc="{iframeSrc}" style="height:100%"></iframe></div>
    """
    # 中间关联表 的标志
    relatedTag = '<=>'

    def __init__(self, queryset, readOnly: bool):
        self.queryset = queryset
        self.readOnly = readOnly

    def render(self):
        count = 0
        tmpHead = ''
        tmpContent = ''
        # 只获取的类型
        fieldTypeList = (
            ManyToManyRel,
            ManyToOneRel,
            ManyToManyField,
        )
        # 字段
        fieldList = []
        # 绑定的中间表 字段
        bindFieldList = []
        for field in self.queryset._meta.get_fields():
            if not isinstance(field, fieldTypeList):
                continue

            logger.debug("====field======= %s", field)
            relatedModel = field.related_model
            headName = getattr(relatedModel, '__cname__', None)
            # 没有额外配置 __name__ 值的, 也忽略掉
            if not headName:
                continue
            if self.relatedTag in headName:
                bindFieldList.append(field)
            else:
                fieldList.append(field)

        for field in fieldList + bindFieldList:
            relatedModel = field.related_model
            modelName = str(self.queryset._meta).lower()
            relatedModelName = str(field.related_model._meta).lower()

            # 这里再过滤掉 一个表的外键的自己的情况
            if modelName == relatedModelName:
                continue

            headName = getattr(relatedModel, '__cname__', '')
            headName = headName.replace(self.relatedTag, self.tabHeadNameItem)
            tmpHead += self.tabHeadItem.format(
                layThis=(count == 0) and 'layui-this' or '',
                headName=headName,
            )

            routeName = self.readOnly and 'platform:related.readonly' or 'platform:related'
            tmpContent += self.tabContentItem.format(
                layShow=(count == 0) and 'layui-show' or '',
                iframeSrc=reverse(routeName, kwargs={
                    'model': modelName,
                    'modelId': self.queryset.id,
                    'relatedModel': relatedModelName,
                })
            )

            count += 1

        return self.html.format(
            head=tmpHead,
            content=tmpContent,
        )

    def renderRelated(self, relatedFieldList: list):
        tmp = ''
        for relatedField in relatedFieldList:
            model = str(self.queryset._meta).lower()
            relatedModel = str(relatedField.related_model._meta).lower()
            tmp += self.html.format(
                relatedTableName='',
                iframeSrc=reverse('platform:related', kwargs={
                    'model': model,
                    'modelId': self.queryset.id,
                    'relatedModel': relatedModel,
                }),
            )
        return tmp


class Detail(object):
    html = """
        <div class="text-panel">{html}</div>
    """

    itemHtml = """
        <div class="text-panel-item layui-row layui-col-space15">
            <div class="layui-col-xs3 layui-col-sm3 layui-col-md3">{cname}</div>
            <div class="layui-col-xs9 layui-col-sm9 layui-col-md9">{value}</div>
        </div>
    """

    def __init__(self, queryset):
        self.queryset = queryset
        self.tmpHtml = ''

    def render(self):
        html = self.tmpHtml
        table = TdNode(" ", " ")
        table.queryset = self.queryset

        for field in self.queryset._meta.fields:
            if isinstance(field, (ManyToManyRel, ManyToOneRel)):
                continue

            helpText, fieldInfo = TableNode._getTableInfo(field.help_text)
            fieldInfo.field = field
            name = fieldInfo.name = field.name
            cname = field.verbose_name
            oldValue = getattr(self.queryset, name)
            value = table._handleType(
                name,
                oldValue,
                fieldInfo,
            )
            # 如果值是日期类型, 则先转化为日期
            if isinstance(oldValue, datetime.datetime):
                value = formatDate(value)

            # 私密字段不完全显示
            if fieldInfo.privacy is True:
                # 如果显示了密码字段, 则部分用**替代
                lenVal = len(value)
                value = value[:2] + "*" * lenVal
            if value == "" or value is None or value == []:
                value = "无"

            # 如果字段是 TextField类型, 则加个pre标签, 让它按照原来的格式显示
            if isinstance(field, TextField):
                value = '<pre>{}</pre>'.format(value)

            item = self.itemHtml.format(
                cname=cname or name,
                value=value
            )
            html += item

        return self.html.format(
            html=html
        )
