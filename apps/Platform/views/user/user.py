# coding=utf-8
from django.contrib import auth
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from entrance.automate.perms import Menus
from apps.Platform.models import Log, User, Role, User_Role
from apps.Platform.tasks import getLoginIPLocation, setLoginStatus

import logging

from utils.quickResponse import QuickResponseError

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class UserAuth(object):
    def __init__(self, request):
        self.userObj = None
        self._loginStatus = 0

        self._request = request
        self._user = request.user
        self._post = request.POST
        self._meta = request.META

        self._account = self._post.get('username')
        self._passwd = self._post.get('password')

    def checkUser(self):
        """
        验证用户密码正确、用户的启用状态
        :return : user
        """
        activeStatus = User.Status.Active
        user = auth.authenticate(username=self._account, password=self._passwd)
        logger.debug("user=== {}".format(user))
        if not user:
            msg = '用户验证失败'
            logger.warning('%s %s' % (self._account, msg))
            raise ValueError(msg)

        if user.status != activeStatus:
            msg = '用户状态异常: %s' % user.get_status_display()
            logger.warning('%s %s' % (self._account, msg))
            raise ValueError(msg)

        if user.isExpire():
            msg = '用户已经过期'
            logger.warning('%s %s' % (self._account, msg))
            raise ValueError(msg)

        self._user = user
        return user

    def login(self):
        """
        如果账户验证通过，保存登录信息
        :return: Bool
        """
        logger.debug('准备验证账密')
        try:
            self.userObj = self.checkUser()
            self._loginStatus = 1
            logger.debug('通过账密认证，准备登录')
            auth.login(self._request, self.userObj)
            self.addLoginHistory('登录成功')
            return True
        except ValueError as e:
            logger.debug("ValueError=== {}".format(e))
            self.addLoginHistory('验证失败，原因：%s' % e, status=False)
            raise QuickResponseError(403, e)

    @property
    def loginIP(self):
        return self._meta.get('HTTP_X_REAL_IP', '') or self._meta.get('REMOTE_ADDR')

    @property
    def loginAgent(self):
        return self._meta.get('HTTP_USER_AGENT', 'unknown')

    def addLoginHistory(self, loginMsg, status=True):
        """
        增加登录历史记录
        :param loginMsg: 自定义信息
        :return:
        """
        loginLog = Log.objects.create(
            type=Log.Type.Login,
            module=__name__,
            userId=self._user.id,
            method=Log.Method.Create,
            status=status,
            message={"message": loginMsg, "agent": self.loginAgent, "ip": self.loginIP}
        )
        # 异步 获取登录归属地，同步执行影响登录速度
        getLoginIPLocation.delay(loginLog.id, self.loginIP)


class LoginView(View):
    def get(self, request):
        return render(request, "user/login.html", {
            "err": request.GET.get("err", ""),
            "next": request.GET.get("next", "")
        })

    def post(self, request):
        redirectUrl = request.POST.get('next', "")

        try:
            userLogin = UserAuth(request)
            userLogin.login()

            user = request.user
            # 此处需要为用户检查内置角色, 如果缺少, 则补上
            self.checkBuiltInRole(user)

            # 登录成功之后 生成用户的菜单
            menus = Menus(user)
            myMenu, myAllMenu = menus.generateUserMenu(all=True)
            # logger.debug('myMenu===', myMenu)
            # logger.debug('myAllMenu===', myAllMenu)
            request.session['myPermList'] = menus.toJson(menus.authorizedRouteList)
            request.session['myMenu'] = myMenu
            request.session['myAllMenu'] = myAllMenu
            logger.debug('request.session === %s === %s', request.session.session_key, dir(request.session))
            # 保存用户登录状态信息
            setLoginStatus(user.id, request.session.session_key)
            return HttpResponseRedirect(redirectUrl or '/')
        except ValueError as e:
            errText = len(e.args) > 1 and e.args[1] or e.args[0]
            return HttpResponseRedirect('?err=%s' % errText)

    def checkBuiltInRole(self, user):
        """
        为用户检查内置角色, 如果缺少, 则补上
        :return:
        """
        splitStr = '__'
        builtInRole = Role.objects.filter(type=Role.Type.BuiltIn)
        # 先获取没有条件的内置角色, 添加进去
        for i in builtInRole.filter(condition={}):
            User_Role.objects.get_or_create(user=user, role=i)

        # 遍历有条件的内置角色, 符合条件的添加进去
        for role in builtInRole.exclude(condition={}):
            try:
                condition = eval(role.condition)
            except Exception as e:
                logger.warning('角色: {} , 条件{} 转换错误: {}'.format(
                    role, role.condition, e
                ))
                continue
            # 条件可能有多个
            for k, v in condition.items():
                # 可能有复杂条件, 支持 __!= 的方式表示 不等于
                logger.debug("condition key ==== %s", k)
                if splitStr in k:
                    fieldName, operator = k.split(splitStr)
                    fieldVal = getattr(user, fieldName)
                    if fieldVal is None:
                        fieldVal = ''
                    if operator == '!=':
                        logger.debug("add role fieldVal ==== %s", fieldVal)
                        if fieldVal != v:
                            logger.debug("add role fieldVal ==== %s", fieldVal)
                            User_Role.objects.get_or_create(
                                user=user,
                                role=role,
                            )
                    elif operator == '*=':
                        if v in fieldVal:
                            User_Role.objects.get_or_create(
                                user=user,
                                role=role,
                            )
                else:
                    fieldVal = getattr(user, k)
                    if fieldVal == v:
                        User_Role.objects.get_or_create(
                            user=user,
                            role=role,
                        )


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse('platform:login'))
