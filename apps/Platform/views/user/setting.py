# coding=utf-8
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from apps.Platform.models import User, Log

from entrance.automate.perms import errorPage
from entrance.automate.curd.update import Update
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

@login_required
@require_POST
def changePassword(request, pk):
    """
    修改密码
    :param request:
    :return:
    """
    # userId = request.POST['uid']

    if not request.user.isSuperUser:
        modifyUser = request.user
    else:
        modifyUser = User.objects.get(id=pk)

    oldPasswd = request.POST['oldPassword']
    password = request.POST['password']
    repassword = request.POST['repassword']
    if oldPasswd == password:
        return HttpResponse('请输入和原密码不同的新密码', status=400)

    if password != repassword:
        return HttpResponse('两次新密码输入不一致,请检查', status=400)

    user = auth.authenticate(account=modifyUser.account, password=oldPasswd)
    if user is not None:
        modifyUser.set_password(password)
        modifyUser.save()
        Log.objects.create(
            userId=request.user.id,
            type=Log.Type.Setting,
            method=Log.Method.Update,
            module=__name__,
            message={
                "message": '修改用户 %s 的密码' % modifyUser.name
            }
        )
        return HttpResponse(1)
    else:
        return HttpResponse('输入的原密码验证不正确', status=400)


@login_required
@require_POST
def editUser(request, pk):
    """
    更新用户信息
    :param request:
    :return:
    """
    postData = request.POST.dict()
    postData['id'] = pk

    updateObj = Update(pk, User, request)
    result = updateObj.handle()
    Log.objects.create(
        userId=request.user.id,
        type=Log.Type.Setting,
        method=Log.Method.Update,
        module=__name__,
        message={
            "message": '修改用户' + result.name + '的信息'
        }
    )
    return HttpResponse(result)


@login_required
def setting(request, pk=None):
    logger.debug("request.user.isSuperUser====== %s %s", request.user.isSuperUser, (not request.user.isSuperUser))
    logger.debug("pk====== %s %s %s", pk, request.user.id, (pk != request.user.id))
    if not request.user.isSuperUser and int(pk) != request.user.id:
        return errorPage(request, "访问权限不足", 403)
    curUser = User.objects.get(id=pk)
    return render(request, 'user/setting.html', {
        'userInfo': curUser,
    })
