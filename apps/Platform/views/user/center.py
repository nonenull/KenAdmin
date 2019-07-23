# coding=utf-8
from django.shortcuts import render
from apps.Platform.models import User, Log

from entrance.automate.perms import checkPerm
import logging

logger = logging.getLogger(__name__)


@checkPerm(check=True)
def center(request, pk):
    if not pk:
        curUser = request.user
    else:
        curUser = User.objects.get(id=pk)

    # 因为要获取的是当前登录信息的上一次，所以应该取倒数第二次
    userLoginLogObj = Log.objects.filter(
        type=Log.Type.Login, userId=curUser.id, status=Log.Status.Success
    ).order_by('-id')

    # 如果只有一条登陆信息， 则取最后一条， 否则应该提取倒数第二条
    lastLoginInfo = {}
    logLen = userLoginLogObj.count()
    if logLen:
        if logLen == 1:
            lastLoginInfo = userLoginLogObj[0]
        else:
            lastLoginInfo = userLoginLogObj[1]

    operationLog = Log.objects.filter(
        userId=curUser.id,
        type=Log.Type.Operation
    ).order_by('-id')[0:20]
    return render(request, 'user/center.html', {
        'userInfo': curUser,
        'lastLoginInfo': lastLoginInfo,
        'operationLog': operationLog,
    })
