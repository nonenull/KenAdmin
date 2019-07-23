# coding=utf-8
import json

from django.http import HttpResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.http import require_POST

from apps.Platform.models import Role, Perm, User_Role
from entrance.automate.perms import checkPerm
from entrance.automate.curd.fs import FS
from entrance.automate.curd.add import Add
from entrance.automate.curd.delete import Delete

import logging

logger = logging.getLogger(__name__)


@checkPerm()
def roles(request):
    fs = FS(Role, request)
    return render(request, 'admin/roles/roles.html', {
        'queryset': fs.handle()
    })


@method_decorator(checkPerm(), name='dispatch')
class RolesView(View):
    def get(self, request):
        roleList = []
        uids = request.GET.getlist('id')
        # 单选的情况下
        if len(uids) == 1:
            # 获取已赋予的角色
            roleList = User_Role.objects.filter(user_id=uids[0]).values_list('role', flat=True)
        roles = Role.objects.all()
        return render(request, 'admin/roles/table.html', {
            'queryset': roles,
            'roleList': json.dumps(list(roleList))
        })

    def post(self, request):
        ids = request.GET.getlist('id')
        roles = request.POST.getlist('role')
        # logger.debug("ids===", ids)
        # logger.debug("menus===", menus)

        for userId in ids:
            createObjList = []
            User_Role.objects.filter(user_id=userId).delete()
            for roleId in roles:
                paramDict = {
                    "user_id": userId,
                    "role_id": roleId
                }
                # logger.debug("添加用户菜单=== ", paramDict)
                createObjList.append(
                    User_Role(**paramDict)
                )
            # logger.debug("添加用户总菜单=== ", createObjList)
            User_Role.objects.bulk_create(createObjList)

        return HttpResponse('角色应用成功')


@checkPerm()
@require_POST
def delete(request):
    batch = Delete(Role, request)
    result = batch.handleWithLog()
    # 删除角色的菜单数据
    obj = Perm.objects.filter(role_id__in=batch.delList)
    obj.delete()
    return HttpResponse(result)


@method_decorator(checkPerm(), name='dispatch')
class AddView(View):
    def get(self, request):
        return render(request, 'public/AddLayout.html', {
            'model': Role
        })

    def post(self, request):
        if Role.objects.filter(
                roleName=request.POST.get('roleName')
        ).exists():
            return HttpResponse('此角色名已存在', status=400)

        addObj = Add(Role, request)
        addObj.handleWithLog()
        return HttpResponse('新增角色完成')
