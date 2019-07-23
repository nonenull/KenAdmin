# coding=utf-8
from django.db.models import ForeignKey, ManyToOneRel, ManyToManyRel
from django_mysql.models import SetCharField, ListCharField

from entrance.automate.curd.curd import CURD
from module.Platform.templatetags.formTag import BaseForm
from utils.convUtil import conv, StorageUnit
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


# 增加
class Add(CURD):
    def __init__(self, *args, unique=False, **kwargs):
        """
        :param model: 模型类
        :param unique: 添加关联数据的时候, 防止出现重复数据
        :param request: request对象
        :param cleanFields: 新增数据时, 是否先使用验证器验证
        """
        super().__init__(*args, **kwargs)
        self.unique = unique

    def _clearData(self, **kwargs):
        return super()._clearData(skipNullValue=True)

    def handle(self):
        """
        此处在数据入库的时候, 执行 clean_fields 对字段信息进行验证
        :return:
        """

        logger.debug("condition======%s", self.condition)
        relatedDict = {}
        fields = self.model._meta.get_fields()
        for field in fields:
            name = field.name
            if isinstance(field, ManyToManyRel):
                continue

            # 处理 关联数据的情况
            if isinstance(field, ManyToOneRel):
                relatedHelpText, relatedFormInfo = BaseForm._getFormInfo(field.field.help_text)
                relatedName = field.get_accessor_name()
                if relatedFormInfo.related and relatedName in self.condition:
                    relatedNameIds = self.condition.pop(relatedName)
                    if not isinstance(relatedNameIds, list):
                        relatedNameIds = [relatedNameIds]
                    for i in relatedNameIds:
                        logger.debug("relatedNameIds i === %s ", i)
                        if not relatedDict.__contains__(relatedName):
                            relatedDict[relatedName] = []
                        relatedDict[relatedName].append(
                            field.related_model.objects.get(id=i)
                        )
                continue

            # 处理外键表单信息
            if isinstance(field, ForeignKey) and name in self.condition:
                self.condition[field.attname] = self.condition.pop(name)
                continue

            # 处理 表单信息 单位转换
            helpText, formInfo = BaseForm._getFormInfo(field.help_text)
            unitFormName = '{}HiddenUnit'.format(name)
            unit = formInfo.unit
            if unit:
                unitFormName = self.condition.pop(unitFormName)
                toUnit = formInfo.toUnit
                if toUnit and (unitFormName == toUnit):
                    originalValue = self.condition.pop(name)
                    self.condition[name] = conv(originalValue, toUnit, unit, StorageUnit)

            # 判断指定了 Form JSONType 为list的情况
            # 判断 字段类型 为 set list 的情况

            if name in self.condition:
                if formInfo.jsonType == 'list':
                    self.condition[name] = self.condition[name].split(';')
                    continue
                if isinstance(field, (SetCharField, ListCharField)):
                    self.condition[name] = self.condition[name].strip(';').replace(';', ',').replace(' ', '')
                    continue

        if self.unique and self.model.objects.filter(**self.condition).exists():
            raise ValueError('新增的数据已存在')

        logger.debug("self.condition==== %s", self.condition)
        newObj = self.model(
            **self.condition
        )

        if self.cleanFields:
            newObj.clean_fields()
        newObj.save()
        # 添加关联数据
        if relatedDict:
            for k, v in relatedDict.items():
                relatedObj = getattr(newObj, k)
                for i in v:
                    relatedObj.add(i)
        return newObj
