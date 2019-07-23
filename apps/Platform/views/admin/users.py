# coding=utf-8
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.http import require_POST

from apps.Platform.models import User, Perm
from entrance.automate.perms import checkPerm
from entrance.automate.curd.fs import FS
from entrance.automate.curd.delete import Delete
from entrance.automate.curd.add import Add
import logging

logger = logging.getLogger(__name__)


@checkPerm()
def users(request):
    fs = FS(User, request)
    return render(request, 'admin/users/users.html', {
        'queryset': fs.handle()
    })


@checkPerm()
@require_POST
def batchDelete(request):
    batch = Delete(User, request)
    result = batch.handleWithLog()
    # 删除用户的权限数据
    obj = Perm.objects.filter(user_id__in=batch.delList)
    obj.delete()
    return HttpResponse(result)


@checkPerm()
@require_POST
def toggleEnable(request):
    action = request.GET.get('type')
    actionDict = {
        'enable': User.Status.Active,
        'disable': User.Status.UnActive,
    }
    ids = request.POST.getlist('ids')
    status = actionDict.get(action)
    if status:
        User.objects.filter(id__in=ids).update(
            status=status
        )
    return HttpResponse('修改用户状态成功')


@method_decorator(checkPerm(), name='dispatch')
class AddView(View):
    def get(self, request):
        return render(request, 'admin/users/add.html', {
            'model': User
        })

    def post(self, request):
        if User.objects.filter(
                account=request.POST.get('account')
        ).exists():
            return HttpResponse('账户名已存在', status=400)

        addObj = Add(User, request)
        condition = addObj.condition
        password = condition['password']
        encryPassword = make_password(password, None, 'pbkdf2_sha256')
        condition['password'] = encryPassword
        newObj = addObj.model(
            **condition
        )
        newObj.clean_fields()
        newObj.save()
        return HttpResponse('新增用户完成')
