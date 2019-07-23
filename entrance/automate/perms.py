# coding=utf-8
import copy
import json
from collections import OrderedDict

from django.contrib.auth.decorators import login_required
from django.db.models import Q, CharField, Value as V
from django.db.models.functions import Concat
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import resolve, reverse, NoReverseMatch

from entrance import routes
from entrance.routersConfig import Type
from apps.Platform.models import Perm, User, User_Role
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def checkPerm(check=False, inherit=None):
    """
    检查用户权限的装饰器
    :param check: 是否检查用户ID, 检查GET参数ID 和 用户ID是否一致
    :param inherit: 继承某个路由的权限
    :return:
    """

    def _checkPerm(func):

        @login_required
        def wrapper(request, *args, **kwargs):
            if request.user.isSuperUser:
                return func(request, *args, **kwargs)

            # 检查用户
            if check and ('id' not in request.GET or str(request.user.id) == request.GET.get('id', '')):
                return func(request, *args, **kwargs)

            # 检查继承情况
            if inherit:
                routeInfo = resolve(reverse(inherit))
            else:
                urlPath = request.path
                routeInfo = resolve(urlPath)

            myPermList = json.loads(request.session.get('myPermList', '{}'))
            for perm in myPermList:
                if routeInfo.url_name == perm.get('name') and routeInfo.namespace == perm.get('namespace'):
                    return func(request, *args, **kwargs)

            return errorPage(request, '您无权访问此页面', status=403)

        return wrapper

    return _checkPerm


def checkDataPerm(model, userField, ownerField=None, skipRole=None, callback=None):
    """
    检查用户的数据权限, 仅允许访问负责的数据

    :param model:  加载的模型
    :param userField: 跟用户关联的字段
    :param ownerField: 负责人字段
    :param skipRole:   忽略角色, 如果用户在此角色中, 不执行过滤
    :return:
    """

    def _checkDataPerm(func):
        def wrapper(request, *args, **kwargs):
            user = request.user
            if user.isSuperUser:
                logger.debug("_checkDataPerm 超级管理员, 无需判断, %s", user)
                return func(request, model, *args, **kwargs)
            elif skipRole and User_Role.objects.filter(role__roleName=skipRole, user=user).exists():
                logger.debug("_checkDataPerm 人员 在 跳过的角色中, 无需判断, 人员: %s 角色: %s", user, skipRole)
                return func(request, model, *args, **kwargs)
            else:
                condition = {
                    userField: request.user
                }
                if ownerField:
                    condition[ownerField] = True
                queryset = model.objects.filter(**condition)
                if callback:
                    callbackResult = callback(request, *args, **kwargs)
                    if callbackResult:
                        queryset = callbackResult
                logger.debug("符合权限的数据: %s", queryset)
                return func(request, queryset, *args, **kwargs)

        return wrapper

    return _checkDataPerm


def errorPage(request, content, status=200, countdown=3, redirect=''):
    """
    错误页面
    :param request: request对象
    :param content: 内容
    :param status:  http状态码
    :param countdown: 倒计时
    :param redirect: 重定向地址
    :return:
    """
    is_ajax = request.is_ajax()
    if not is_ajax:
        return render(request, 'public/ErrorPage.html', {
            'content': content,
            'status': status,
            'countdown': countdown,
            'redirect': redirect,
        })
    return HttpResponse(content, status=status)


class Menus(object):
    """
    根据urls设置的路由，匹配用户菜单权限后生成菜单
    """

    def __init__(self, queryset=None):
        self.queryset = queryset
        # 完整的路由列表
        self.routeList = self.addRoutesUrl(routes.Routers.getRouters())
        # 传入的queryset参数可能是用户或者角色
        if isinstance(queryset, User):
            # 如果不是超管， 则加载用户所属的权限列表
            if not queryset.isSuperUser:
                # 从权限表中获取属于用户的 路由 name 列表, 跟完整的路由列表作比对, 返回完整的用户路由列表
                self.authorizedRouteList = self.filterRouterList(self.routeList, self.getUserRoute())
                # logger.debug('userRouteList=============', self.userRouteList)
            else:
                self.authorizedRouteList = self.routeList
            # logger.debug('getUserRoute============', self.getUserRoute())
        else:
            self.authorizedRouteList = self.filterRouterList(self.routeList, self.getRoleRoute())
            # logger.debug('getRoleRoute============', self.getRoleRoute())

    def generate(self, routeList=None, all=False):
        routeList = routeList or self.authorizedRouteList
        transedData = self.transformData(routeList, all=all)

        def _setChild(parentMenuList, parentName, curMenu):
            """
            遍历父菜单列表, 根据父菜单名, 获取到相应的对象, 并把当前菜单插入到child字段中
            :param parentMenuList:  父菜单列表
            :param parentName:  父菜单名
            :param curMenu: 当前菜单
            :return:
            """
            for parentMenu in parentMenuList:
                # 匹配父菜单name值, 和namespace 一致
                if parentName != parentMenu['name']:
                    continue
                parentMenuNamespace = parentMenu.get("namespace")
                if parentMenuNamespace and parentMenuNamespace != curMenu.get("namespace", 2):
                    continue

                # logger.debug("获取父菜单: ", parentMenu)
                if not parentMenu.__contains__("child"):
                    parentMenu["child"] = [curMenu]
                else:
                    parentMenu["child"].append(curMenu)

        # 根据层级， 从高层往低层遍历， 不断归集
        # 默认数据是反序的, 所以直接遍历即可
        for menuLevel, menuList in transedData.items():
            if menuLevel == 0:
                break
            for menu in menuList[:]:
                nameSplit = menu["name"].split(".")
                # 获取0 到倒数第二个元素
                parentNameList = nameSplit[0:-1]
                if not parentNameList:
                    parentLevelMenuList = transedData[0]
                    _setChild(parentLevelMenuList, menu["namespace"], menu)
                else:
                    parentLevel = len(parentNameList)
                    parentName = ".".join(parentNameList)
                    # 获取 父菜单 所属 level 菜单的数据
                    parentLevelMenuList = transedData[parentLevel]
                    _setChild(parentLevelMenuList, parentName, menu)
                menuList.remove(menu)

        tmp = []
        for menuLevel, menuList in transedData.items():
            tmp += menuList
        return tmp

    def transformData(self, routeList, all=False):
        """
        将原始路由列表进行一个归类转换
        rtype 不等于 title 或 menu 的，排除
        {
          menuLevel (int): menuList (list)
        }
        :param routeList: 原始路由列表
        :param all: True 遍历所有路由, False 只遍历菜单
        :return:
        """

        transedData = {}
        for route in routeList:
            rType = route["rtype"]
            if not all and (rType not in [Type.menu, Type.title, Type.include]):
                continue

            if rType == Type.include:
                level = 0
            else:
                level = self.getMenuLevel(route["name"])

            if not transedData.__contains__(level):
                transedData[level] = [route]
            else:
                transedData[level].append(route)

        def sortDict():
            """
            返回 [反序]的有序列表
            :return:
            """
            keys = sorted(transedData.keys(), reverse=True)
            sortedDict = OrderedDict()
            for key in keys:
                sortedDict[key] = transedData[key]
            return copy.deepcopy(sortedDict)

        return sortDict()

    @staticmethod
    def getMenuLevel(name):
        splitName = name.split(".")
        return len(splitName)

    def generateUserMenu(self, all=False, toJson=True):
        """
        生成菜单
        :param all: 是否生成完整的菜单列表(包含按钮在内)
        :param toJson:
        :return:
        """
        if not all:
            userMenu = self.generate(self.authorizedRouteList)
            return toJson and self.toJson(userMenu) or userMenu
        else:
            userMenu = self.generate(self.authorizedRouteList)
            userAllMenu = self.generate(self.authorizedRouteList, all=True)
            return toJson and (self.toJson(userMenu), self.toJson(userAllMenu)) or (userMenu, userAllMenu)

    def getRoleRoute(self):
        # return Perm.objects.filter(role=self.queryset).values_list("name", flat=True).distinct()
        return Perm.objects.filter(role=self.queryset).annotate(
            fullname=Concat(
                'namespace', V(':'), 'name',
                output_field=CharField()
            )
        ).values_list('fullname', flat=True)

    def getUserRoute(self):
        """
        获取用户权限列表
        获取用户的角色权限列表
        组合起来， 取并集
        :return:
        """
        # uid = self.queryset.id
        logger.debug("getUserRoute self.queryset=== %s", self.queryset)
        logger.debug("getUserRoute ROLE === %s", self.queryset.user_role_set.all())

        userPermList = Perm.objects.filter(
            Q(role__in=self.queryset.user_role_set.all().values_list("role", flat=True)) |
            Q(user=self.queryset)
        ).annotate(
            fullname=Concat(
                'namespace', V(':'), 'name',
                output_field=CharField()
            )
        ).values_list('fullname', flat=True)

        logger.debug('===userPermList.query=== %s', userPermList)
        # logger.debug("当前用户: %s 的所有权限列表集合 %s" % (self.queryset.name, userPermList))
        return userPermList

    @staticmethod
    def filterRouterList(routeList, routePermList):
        """
        过滤数据， 拿 路由列表 跟 用户权限列表作对比，删除在 用户权限列表中不存在的路由项
        :param routeList:   完整的路由列表
        :param routePermList:   用户权限列表
        :return:
        """
        userRoutes = []
        for route in routeList:
            fullname = '{}:{}'.format(route.get("namespace", ''), route.get("name", ''))
            if fullname not in routePermList:
                continue
            userRoutes.append(route)
        return userRoutes

    @staticmethod
    def addRoutesUrl(routeList):
        """
        遍历routeList， 根据name值， 填充一个完整的url
        :param routeList:
        :return:
        """
        for route in routeList:
            if route.get("rtype") in [routes.Type.include, routes.Type.title]:
                route["url"] = "#"
            else:
                namespace = route.get('namespace')
                name = route.get("name")
                if namespace:
                    logger.debug("namespace=== %s", namespace)
                    try:
                        route["url"] = reverse("{}:{}".format(namespace, name))
                    except NoReverseMatch:
                        route["url"] = reverse("{}:{}".format(namespace, name), args=(0,))
                else:
                    logger.debug("no namespace===")
                    try:
                        logger.debug("router==== %s", route)
                        route["url"] = reverse(name)
                    except NoReverseMatch:
                        route["url"] = reverse(name, args=(0,))
        return routeList

    def toJson(self, routeDict):
        return json.dumps(routeDict)
