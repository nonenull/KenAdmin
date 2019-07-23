# coding=utf-8
import pickle
from django.db.models import AutoField, Q, ForeignKey
from django.db.models.query import QuerySet
from django_mysql.models import JSONField
from module.Platform.config import Filter as FilterHelpText
from utils.convUtil import conv, StorageUnit, convs
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class FS(object):
    """
    Filter and Search
    根据request.GET里面的字段,自动过滤与搜索数据
    返回相应的结果
    """

    def __init__(self, obj, request):
        """
        判断 model类型, 并对数据进行初步处理
        :param obj: 可能是模型类, 或者是queryset
        :param request: request对象
        """
        if isinstance(obj, QuerySet):
            self.queryset = obj
            self.fields = obj.model._meta.fields
        else:
            self.queryset = obj.objects.all().order_by('-id')
            self.fields = obj._meta.fields

        self.getData = request.GET
        # logger.debug("fields====", self.fields)
        self.fieldNameList = [f.name for f in self.fields]
        self._cleanData = self.__cleanData()

    def handle(self):
        if not self._cleanData:
            logger.debug("not filter or search")
            return self.queryset
        searchStr = self._cleanData.get('search')
        if searchStr:
            return self.search(searchStr)
        else:
            return self.filter()

    def search(self, searchStr):
        ignoreFieldList = [AutoField]
        # 外键只匹配这三个字段, 如果有的话
        foreignKeyFieldNameList = ['name', 'cname', 'comment']

        conditions = Q()

        for field in self.fields:
            fieldType = type(field)
            if fieldType in ignoreFieldList:
                continue
            fieldName = field.name
            if fieldType == ForeignKey:
                foreignKeyModelFields = field.related_model._meta.fields
                for foreignKeyModelField in foreignKeyModelFields:
                    foreignKeyFieldName = foreignKeyModelField.name
                    if foreignKeyFieldName not in foreignKeyFieldNameList:
                        continue
                    conditions = conditions | Q(**{'{}__{}__contains'.format(fieldName, foreignKeyFieldName): searchStr})
                continue

            conditions = conditions | Q(**{fieldName + '__contains': searchStr})

        logger.debug("condition ====== %s", conditions)

        return self.queryset.filter(
            conditions
        )

    def filter(self):
        cleanData = self.__cleanData()
        # 此处需要判断 转换单位
        for k, v in cleanData.copy().items():
            realKey = k.split('__')[0]
            logger.debug("realkey ==== %s", realKey)
            for field in self.fields:
                if realKey != field.name:
                    continue
                help_text = field.help_text or {}
                filterKey = FilterHelpText.__name__
                filterInfo = help_text.get(filterKey)
                if filterInfo:
                    filterInfo = pickle.loads(filterInfo)
                else:
                    filterInfo = FilterHelpText()
                # 剔除 没有 filter 标志的 参数
                if not filterInfo:
                    cleanData.pop(k)
                    continue

                # JSONField 字段类型需要修改查询条件, 不支持__in
                if isinstance(field, JSONField):
                    # logger.debug("JSON 字段, 修改 key")
                    oldKey = k
                    conditionKey = '__contains'
                    if isinstance(v, list):
                        k = oldKey.replace('__in', conditionKey)
                        cleanData[k] = cleanData.pop(oldKey)
                    else:
                        k = oldKey + conditionKey
                        cleanData[k] = [cleanData.pop(oldKey)]

                if not filterInfo.toUnit:
                    continue
                # 注意, 此处是将值转换回原来的样子
                unit = filterInfo.toUnit
                toUnit = filterInfo.unit
                if isinstance(v, list):
                    cleanData[k] = convs(v, unit, toUnit, StorageUnit)
                else:
                    cleanData[k] = conv(v, unit, toUnit, StorageUnit)

        logger.debug('clientData === %s', cleanData)
        return self.queryset.filter(
            **cleanData
        )

    def __cleanData(self):
        """
        清洗 request.GET 的数据, 将空值去掉
        :return:
        """
        tmp = {}
        for k, v in self.getData.items():
            if k not in self.fieldNameList and k != 'search':
                continue
            if not v:
                continue
            datas = self.getData.getlist(k)
            if len(datas) == 1:
                tmp[k] = datas[0]
            else:
                tmp[k + '__in'] = datas
        return tmp
