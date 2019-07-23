# coding=utf-8
from django.shortcuts import render

from entrance.automate.curd.fs import FS
from entrance.automate.perms import checkPerm
from apps.Platform.models import Log


@checkPerm()
def logs(request):
    fs = FS(Log, request)
    return render(request, 'admin/logs/logs.html', {
        'queryset': fs.handle()
    })
