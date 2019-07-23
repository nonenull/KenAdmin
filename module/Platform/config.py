# coding=utf-8
import pickle
import logging

logger = logging.getLogger(__name__)


# 前端 layui badge 徽章标志
# 详情请看: https://www.layui.com/doc/element/badge.html
class Badge:
    # 红色
    Red = 'layui-bg-red'
    # 橙色
    Orange = 'layui-bg-orange'
    # 墨绿
    Green = 'layui-bg-green'
    # 藏青
    Cyan = 'layui-bg-cyan'
    # 蓝色
    Blue = 'layui-bg-blue'
    # 雅黑
    Black = 'layui-bg-black'
    # 银灰
    Gray = 'layui-bg-gray'
    # 黄色
    Yellow = 'layui-bg-yellow'


class HelpText(object):
    cname: str = None  # 强行指定 字段显示名
    proxy = None  # 强行指定代理方法(将使用执行方法获取的值)
    unit: str = None  # 单位
    toUnit: str = None  # 转换单位
    truncatechars: int = None  # 超出字符省略

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def init(self):
        return {
            self.__class__.__name__: pickle.dumps(self)
        }


class Form(HelpText):
    verify: list = []  # 额外指定 layui 的正则表达式
    formType: str = None  # 指定 表单 字段类型
    disabled: bool = None  # 指定 表单 字段 为只读
    required: bool = None  # 手动指定 表单 字段为必填
    relatedCreateRoute: str = None  # 联动相应的路由
    placeholder: str = None  # form 表单 input 或 textarea 默认的提示信息
    jsonType: str = None  # 主要用来表示JSONField字段的类型, 值只有两种, list 和 dict
    batch: bool = None  # 表示本字段能否支持批量编辑
    related: bool = False  # 用来判断是否加载关联数据
    multipleChoice: bool = False  # 用来表示是否生成多选框
    switchChoice: bool = False  # 用来表示是否生成开关


class Filter(HelpText):
    pass


class Table(HelpText):
    sort: str = None  # 列增加 排序功能
    privacy: bool = None  # 隐私字段, 内容将部分用*替换
    lineFeed: bool = None  # 用于 值为list的自动换行
