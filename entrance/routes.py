# coding=utf-8
import copy
import sys

from django.urls import re_path
from entrance.automate import views as publicViews
from entrance.routersConfig import Type, BtnColor, Link
import logging

logger = logging.getLogger(__name__)


class Routers(object):
    """
    一个路由类
    用于根据配置的路由， 自动生成对应关系， 生成自动菜单
    """
    routeList = []
    routeTag = 0

    def __init__(self, ):
        pass

    def addPath(self, name, kwargs, *args):
        return re_path(*args, name=name, kwargs=kwargs)

    def addRoute(self, **kwargs):
        # logger.debug("router== %s \n" % route)
        self.routeList.append(kwargs)

    @staticmethod
    def getRouters():
        return copy.deepcopy(Routers.routeList)

    @staticmethod
    def checkPanelButton(routerKwargs):
        routerKwargs.setdefault("rtype", Type.title)
        if routerKwargs.get('rtype') == Type.panelButton:
            if not routerKwargs.get('color'):
                routerKwargs.setdefault("color", BtnColor.Blue)
            if not routerKwargs.get('filter'):
                routerKwargs.setdefault("filter", "")
            if not routerKwargs.get('icon'):
                routerKwargs.setdefault("icon", "layui-icon-404")
        return routerKwargs

    @staticmethod
    def getNameSpace(maxDeep=5):
        for i in range(2, maxDeep):
            frame = sys._getframe(i)
            fLocals = frame.f_locals
            if "app_name" in fLocals:
                return fLocals.get("app_name")

        raise ValueError("当前路由缺少 namespace")


class Route(object):
    viewTypeDict = {
        "index": publicViews.index,
        "add": publicViews.AddView.as_view(),
        "edit": publicViews.EditView.as_view(),
        "batchEdit": publicViews.BatchEditView.as_view(),
        "delete": publicViews.delete,
        "detail": publicViews.detail,
    }

    def __init__(self, args, name, kwargs, routerKwargs):
        self.args = list(args)
        self.name = name
        self.kwargs = kwargs
        self.routerKwargs = routerKwargs

    def checkView(self, type):
        """
        没设置view的情况下, 自动根据type类型添加一个默认的
        :return:
        """
        if len(self.args) == 1:
            self.args.append(self.viewTypeDict.get(type))

    def set(self, type, defaultDict):
        if type != 'index':
            urlRex = self.args[0]
            if type not in ['add', 'delete']:
                self.args[0] = '^{}/(?P<pk>\d+)/{}$'.format(urlRex, type)
            else:
                self.args[0] = '^{}/{}$'.format(urlRex, type)
        for k, v in defaultDict.items():
            self.routerKwargs.setdefault(k, v)

        self.checkView(type)
        return addRoute(*self.args, kwargs=self.kwargs, name=self.name, **self.routerKwargs)


routers = Routers()


def addRoute(*args, name=None, kwargs=None, **routerKwargs):
    """
    添加路由
    :param args:    django原有参数
    :param name:    别名,django原有参数
    :param kwargs:  django原有参数
    :param rtype:   菜单类型
    :param parent:  父菜单名
    :param display: 菜单显示名
    :param filter:  生成按钮后添加的my-filter属性名
    :param iccon:   生成按钮图标
    :return: URLPattern 对象
    """

    if len(args) < 2:
        raise ValueError('urls 配置错误: %s' % args)

    url = args[0]

    # 如果route中没有配置别名， 则自动根据/号转换，如 /data/add ==> data.add
    if not name:
        # 过滤掉中间的PK段
        name = url.strip('/^$').replace("/(?P<pk>\\d+)", "").replace('/', '.')

    if 'display' in routerKwargs:
        # 获取路由的 namespace
        if routerKwargs.get('rtype') != Type.include:
            routerKwargs.update({'namespace': routers.getNameSpace()})

            # 类型是panelButton的话, 检查必有参数, 如果没有, 添加默认参数
            routerKwargs = Routers.checkPanelButton(routerKwargs)
        else:
            name = args[1][-1]

        routerKwargs.update({'name': name})
        routers.addRoute(
            **routerKwargs
        )

    return routers.addPath(
        name,
        kwargs,
        *args
    )


def indexPageRoute(*args, name=None, kwargs=None, **routerKwargs):
    """
    便捷添加一个菜单首页路由
    """
    defaultDict = {
        'rtype': Type.menu,
    }
    args = list(args)
    urlReg = args[0]
    args[0] = "^{}$".format(urlReg)
    route = Route(args, name, kwargs, routerKwargs)
    return route.set('index', defaultDict)


def addButtonRoute(*args, name=None, kwargs=None, **routerKwargs):
    """
    便捷添加一个新增按钮的路由
    """

    defaultDict = {
        'display': '新增',
        'filter': 'add-button',
        'icon': 'layui-icon-add-circle',
        'color': BtnColor.Blue,
        'rtype': Type.panelButton,
        'link': Link.LayerPanel,
    }
    route = Route(args, name, kwargs, routerKwargs)
    return route.set('add', defaultDict)


def deleteButtonRoute(*args, name=None, kwargs=None, **routerKwargs):
    """
    便捷添加一个批量删除按钮的路由
    """
    defaultDict = {
        'display': '批量删除',
        'filter': 'batch-delete-button',
        'icon': 'layui-icon-delete',
        'color': BtnColor.Red,
        'rtype': Type.panelButton,

    }
    route = Route(args, name, kwargs, routerKwargs)
    return route.set('delete', defaultDict)


def batchEditButtonRoute(*args, name=None, kwargs=None, **routerKwargs):
    """
    便捷添加一个批量修改按钮的路由
    """
    defaultDict = {
        'display': '批量编辑',
        'filter': 'batch-edit-button',
        'icon': 'layui-icon-edit',
        'color': BtnColor.Yellow,
        'rtype': Type.panelButton,
        'link': Link.LayerPanel,
    }
    route = Route(args, name, kwargs, routerKwargs)
    return route.set('batchEdit', defaultDict)


def detailButtonRoute(*args, name=None, kwargs=None, **routerKwargs):
    defaultDict = {
        'rtype': Type.button,
        'display': '详情',
    }
    route = Route(args, name, kwargs, routerKwargs)
    return route.set('detail', defaultDict)


def editButtonRoute(*args, name=None, kwargs=None, **routerKwargs):
    defaultDict = {
        'rtype': Type.button,
        'display': '编辑',
    }
    route = Route(args, name, kwargs, routerKwargs)
    return route.set('edit', defaultDict)
