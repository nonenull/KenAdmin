# coding=utf-8
from entrance.automate.curd.curd import CURD
from module.Platform.models import Log
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Retrieve(CURD):
    def __init__(self, pk, *args, **kwargs):
        self.pk = pk
        super().__init__(*args, **kwargs)

    def handle(self):
        try:
            return self.model.objects.get(id=self.pk)
        except Log.DoesNotExist:
            logger.warning("用户：%s 尝试访问不存在的 %s 数据: %s" % (self.request.user.name, self.model, self.pk))
            raise ValueError('需要查询的数据不存在')
