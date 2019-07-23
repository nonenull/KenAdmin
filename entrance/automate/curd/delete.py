# coding=utf-8
from django.db.models.query import QuerySet
from entrance.automate.curd.curd import CURD
from apps.Platform.models import User
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


# 删
class Delete(CURD):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        """
        :param request: request对象
        :param models:  models类
        """
        self.postData = self.request.POST
        self.delList = self.postData.getlist('ids')

        self.preCheck()

    def preCheck(self):
        """
        检查是否要删除用户, 防止用户把自己给删了
        :return:
        """

        # 防止有二货把自己账号给删了 = =
        requestUserId = str(self.request.user.id)
        if self.model == User and requestUserId in self.delList:
            self.delList.remove(requestUserId)

    def handle(self):
        # logger.debug("self.model======", self.model)
        condition = {"id__in": self.delList}
        if isinstance(self.model, QuerySet):
            obj = self.model.filter(**condition)
        else:
            obj = self.model.objects.filter(**condition)
        logger.debug("obj====== %s", obj)
        deleted, rowsCount = obj.delete()
        return '删除完毕. \n删除行数: {} \n{}'.format(deleted, rowsCount)
