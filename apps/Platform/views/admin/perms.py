# coding=utf-8
import json

from django.utils.decorators import method_decorator
from django.views import View
from django.http import HttpResponse
from django.shortcuts import render

from apps.Platform.models import User, Perm as PermModel, Role

from entrance.automate.perms import checkPerm, Menus, errorPage
import logging

from apps.Platform.tasks import resetLoginStatus

logger = logging.getLogger(__name__)


@method_decorator(checkPerm(), name='dispatch')
class PermView(View):
    typeModelList = {'user': User, 'role': Role}

    def get(self, request, rType):
        allMenuObj = Menus(request.user)
        allMenu = allMenuObj.toJson(
            allMenuObj.generate(
                allMenuObj.routeList, all=True
            )
        )
        ids = request.GET.getlist('id')
        model = self.typeModelList.get(rType)
        authorizedAllMenu = []
        if len(ids) == 1:
            try:
                obj = model.objects.get(id=ids[0])
                menuObj = Menus(obj)
                authorizedAllMenu = menuObj.authorizedRouteList
            except model.DoesNotExist:
                return errorPage(request, '获取权限信息失败', status=400)

        return render(request, 'admin/perms/perms.html', {
            'allMenu': allMenu,
            'authorizedAllMenu': json.dumps(authorizedAllMenu),
        })

    def post(self, request, rType):
        ids = request.GET.getlist('id')
        menus = request.POST.getlist('tree')
        model = self.typeModelList.get(rType)
        for objId in ids:
            obj = model.objects.get(id=objId)
            createObjList = []
            # 菜单设置前需要初始化(删除原有菜单)
            condition = {rType: obj}
            PermModel.objects.filter(**condition).delete()
            for menuName in menus:
                namespace, name = menuName.split(':')
                condition.update({
                    'name': name,
                    'namespace': namespace,
                })
                createObjList.append(
                    PermModel(**condition)
                )
            # logger.debug("添加用户总菜单=== ", createObjList)
            PermModel.objects.bulk_create(createObjList)
        # 更新权限后, 提出用户登录状态, 让用户重新登录, 获取新权限
        if ids:
            if rType == 'user':
                resetLoginStatus(*ids)
            else:
                roles = model.objects.filter(id__in=ids)
                userIds = []
                for r in roles:
                    userIds += r.user_set.all().values_list('id', flat=True)
                resetLoginStatus(*set(userIds))

        return HttpResponse('权限更新成功')
