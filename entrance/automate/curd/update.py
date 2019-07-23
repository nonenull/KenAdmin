# coding=utf-8
import ast

from django.db.models import DateTimeField, DateField, BooleanField, ManyToOneRel, ManyToManyRel
from django_mysql.models import SetCharField, ListCharField

from entrance.automate.curd.curd import CURD
from apps.Platform.templatetags.formTag import BaseForm
from utils.convUtil import conv, StorageUnit
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


# 改
class Update(CURD):
    def __init__(self, pk, *args, **kwargs):
        self.pk = pk
        super().__init__(*args, **kwargs)
        self.preCheck()

    def preCheck(self):
        """
        此处主要用来检查参数用的
        比如如果字段是 DateTime 类型, 提交了空字符串, 将会引发 ValidationError 异常
        :return:
        """
        logger.debug("self.model==== %s", self.model)
        fields = self.model._meta.fields
        keys = self.condition.keys()
        for field in fields:
            name = field.name
            if name not in keys:
                continue
            nameVal = self.condition.get(name)
            if isinstance(field, (DateTimeField, DateField)) and nameVal == "":
                self.condition[name] = None

            if isinstance(field, BooleanField) and nameVal in ['True', 'False']:
                self.condition[name] = ast.literal_eval(nameVal)

    def handle(self):
        relatedDict = {}
        fields = self.model._meta.get_fields()
        for field in fields:
            name = field.name
            if isinstance(field, ManyToManyRel):
                continue
            # 处理 关联数据的情况
            if isinstance(field, ManyToOneRel):
                relatedHelpText, relatedFormInfo = BaseForm._getFormInfo(field.field.help_text)
                if relatedFormInfo.related:
                    relatedName = field.get_accessor_name()
                    if relatedName not in self.condition:
                        continue
                    relatedNameIds = self.condition.pop(relatedName)
                    if not isinstance(relatedNameIds, list):
                        relatedNameIds = [relatedNameIds]
                    for i in relatedNameIds:
                        if not relatedDict.__contains__(relatedName):
                            relatedDict[relatedName] = []
                        relatedDict[relatedName].append(
                            field.related_model.objects.get(id=i)
                        )
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

            if name in self.condition:
                # 判断指定了 Form JSONType 为list的情况
                if formInfo.jsonType == 'list':
                    self.condition[name] = self.condition[name].split(';')
                if isinstance(field, (SetCharField, ListCharField)):
                    self.condition[name] = self.condition[name].strip(';').replace(';', ',').replace(' ', '')
                    continue
            else:
                continue

        obj = self.model.objects.get(id=self.pk)

        # 添加关联数据
        # {'harddisk_set': [<HardDisk: 固态盘:2000G>, <HardDisk: 固态盘:100G>]}
        if relatedDict:
            logger.debug("relatedDict======= %s", relatedDict)
            for k, v in relatedDict.items():
                relatedObj = getattr(obj, k)
                for i in v:
                    relatedObj.add(i)

        for k, v in self.condition.items():
            setattr(obj, k, v)
            obj.save()
        return obj
