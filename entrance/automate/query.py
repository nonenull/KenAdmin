# coding=utf-8
from django.db.models.query import QuerySet
from django.db.models import Model

"""
存放所有跟模型 数据库交互有关的函数
"""


class Related(object):
    """
    逻辑关联
    """

    def __init__(self, lModel, mModel, rModel):
        """
        :param lModel: 关联表(主)
        :param mModel: 中间表
        :param rModel: 关联表
        """
        self.lModel = lModel
        self.mModel = mModel
        self.rModel = rModel

        self.lModelName = self.getModelName(self.lModel)
        self.rModelName = self.getModelName(self.rModel)

        self.lRelatedField = self.getRelatedField(self.lModelName)
        self.rRelatedField = self.getRelatedField(self.rModelName)

    def add(self, objs):
        """
        1. 检查对象或者id是否正确, 是否属于self.rModel
        2. 检查是否已存在, 已存在的不管
        检查没问题后添加关联数据
        支持的参数类型有:
            id
            [id1, id2]
            queryset
            <QuerySet []>
        :param objs:
        :return:
        """
        if isinstance(objs, Model):
            return self._handleQueryset(objs)
        elif isinstance(objs, QuerySet):
            return self._handleQuerysets(objs)
        elif isinstance(objs, (tuple, list)):
            return self._handleIds(objs)
        else:
            return self._handleId(objs)

    def delete(self, objs):
        """
        检查没问题后删除关联数据
        支持的参数类型有:
            id
            [id1, id2]
            queryset
            <QuerySet []>
        :param objs:
        :return:
        """
        if isinstance(objs, Model):
            return self._handleQueryset(objs, delete=True)
        elif isinstance(objs, QuerySet):
            return self._handleQuerysets(objs, delete=True)
        elif isinstance(objs, list):
            return self._handleIds(objs, delete=True)
        else:
            return self._handleId(objs, delete=True)

    def _handleQuerysets(self, querysets, delete=False):
        dataList = []
        for queryset in querysets:
            result = self._handleQueryset(queryset, delete=delete)
            if result:
                dataList.append(result)
        return dataList

    def _handleQueryset(self, queryset, delete=False):
        curModelName = self.getModelName(queryset)
        if self.getModelName(queryset) != self.rModelName:
            raise ValueError('模型数据类型不正确, 必须为:{}, 当前: {}'.format(
                curModelName.title(),
                self.rModelName.title()
            ))

        condition = self._getCondition(queryset.id)
        return self._handle(condition, delete=delete)

    def _handleIds(self, idList, delete=False):
        dataList = []
        for relatedId in idList:
            result = self._handleId(relatedId, delete=delete)
            if result:
                dataList.append(result)
        return dataList

    def _handleId(self, relatedId, delete=False):
        if not self.rModel.objects.filter(id=int(relatedId)).exists():
            raise self.rModel.DoesNotExist('数据不存在, id: {}'.format(relatedId))
        condition = self._getCondition(relatedId)
        return self._handle(condition, delete=delete)

    def _handle(self, condition, delete=False):
        objects = self.mModel.objects
        if not delete:
            # 此处自动过滤已存在的关联数据
            if not objects.filter(**condition).exists():
                return objects.create(**condition)
        else:
            return objects.filter(**condition).delete()

    def _getCondition(self, relatedId):
        return {
            self.lRelatedField: self.lModel.id,
            self.rRelatedField: relatedId,
        }

    @property
    def objects(self):
        relatedIds = self.mModel.objects.filter(**{
            self.lRelatedField: self.lModel.id
        }).values_list(self.rRelatedField, flat=True)
        return self.rModel.objects.filter(id__in=relatedIds)

    def getModelName(self, model):
        return model._meta.model_name.lower()

    def getRelatedField(self, modelName):
        """
        获取中间表的关联字段名
        固定格式: 关联表名 + Id, 如 userId
        :param model:
        :return:
        """
        return '{}Id'.format(modelName)

    def __str__(self):
        return '{} => {}'.format(self.lModelName, self.rModelName)


class FieldsParser(object):
    """
    根据 QuerySet 或者 Model 对象, 获取相应的字段数据, 参数等
    """

    def __init__(self, queryset):
        self.queryset = queryset
        if isinstance(queryset, QuerySet):
            self.fields = queryset.model._meta.fields
        elif isinstance(queryset, Model):
            self.fields = queryset._meta.fields
        else:
            raise ValueError('参数类型不正确, django.db.models.query.QuerySet || django.db.models.Model')

    def getField(self, name, key=None):
        """

        :param name: 字段名
        :param key:  获取字段对象属性
        :return:
        """

        def _getField():
            for i in self.fields:
                if i.name != name:
                    continue
                return i

        field = _getField()
        if key:
            return getattr(field, key)
        return field

    def getValue(self, name):
        if isinstance(self.queryset, Model):
            return getattr(self.queryset, name)
        else:
            return self.queryset.values_list(name)
