# coding=utf-8
import re
from apps.Platform.models import Log
from utils.stack import Stack
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class CURD(object):
    def __init__(self, model, request, cleanFields=True):
        """
        增删改查有关的自动操作类
        :param pk: 主键ID
        :param model: 模型 or queryset
        :param request: 请求reqeust对象
        :param cleanFields: 执行前是否先检查验证器
        :param logging: 是否写日志记录到Log表中
        """
        self.model = model
        self.request = request
        self.regx = re.compile(r'\[\d+\]')
        self.cleanFields = cleanFields
        self.submitData = ((request.method == 'POST') and request.POST or request.GET)
        self.condition = self._clearData()

    def _clearData(self, skipNullValue=False):
        tmp = {}
        for k in self.submitData.keys():
            if k == 'csrfmiddlewaretoken':
                continue
            value = self.submitData.getlist(k)
            regxSearch = re.search(self.regx, k)
            if regxSearch and regxSearch.start() > 0:
                k = k[:regxSearch.start()]
                if k not in tmp:
                    tmp[k] = []
                tmp[k].append(value[0])
            elif len(value) == 1 and '[]' not in k:
                v = value[0]
                if skipNullValue and v == '':
                    continue
                tmp[k] = v
            else:
                tmp[k.rstrip('[]')] = value
        return tmp

    def handle(self):
        raise NotImplementedError("父类 CURD 规定 必须实现 一个handle方法")

    def handleWithLog(self):
        """
        执行逻辑
        执行handle方法后
        根据logging参数执行日志记录
        :return:
        """
        result = self.handle()
        self.generateLog()
        return result

    def generateLog(self):
        stack = Stack(3)
        # logger.debug('stack===', stack)
        # logger.debug('modName===', stack.getModule())
        childClassName = Stack(2).getClass()
        # logger.debug('childClassName===', childClassName)
        nameDict = {
            'Add': Log.Method.Create,
            'Delete': Log.Method.Delete,
            'Update': Log.Method.Update,
            'Retrieve': Log.Method.Retrieve,
        }

        Log.objects.create(
            type=Log.Type.Operation,
            module=stack,
            userId=self.request.user.id,
            method=nameDict.get(childClassName),
            status=Log.Status.Success,
            message=self.condition
        )
