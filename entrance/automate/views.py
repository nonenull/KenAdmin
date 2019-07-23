# coding=utf-8
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.http import require_POST

from entrance.automate.curd.fs import FS
from entrance.automate.curd.update import Update
from entrance.automate.curd.retrieve import Retrieve
from entrance.automate.curd.add import Add
from entrance.automate.curd.delete import Delete
from entrance.automate.perms import checkPerm, errorPage


@checkPerm()
def index(request, model=None):
    fs = FS(model, request)
    return render(request, 'public/ListLayout.html', {
        "queryset": fs.handle(),
    })


@checkPerm()
def detail(request, pk, model=None):
    try:
        rObj = Retrieve(pk, model, request)
        result = rObj.handle()
        return render(request, 'public/DetailLayout.html', {
            "queryset": result
        })
    except ValueError as e:
        return errorPage(request, e, status=400)


@method_decorator(checkPerm(), name='dispatch')
class EditView(View):
    def get(self, request, pk, model=None):
        try:
            rObj = Retrieve(pk, model, request)
            result = rObj.handle()
            return render(request, 'public/EditLayout.html', {
                "queryset": result
            })
        except ValueError as e:
            return errorPage(request, e, status=400)

    def post(self, request, pk, model=None):
        try:
            updateObj = Update(pk, model, request)
            updateObj.handle()
            return HttpResponse('修改数据完成')
        except ValueError as e:
            return HttpResponse(e, status=400)


@method_decorator(checkPerm(), name='dispatch')
class BatchEditView(View):
    def get(self, request, model=None):
        try:
            rObj = Retrieve(model, request)
            result = rObj.handle()
            return render(request, 'public/BatchEditLayout.html', {
                "queryset": result
            })
        except ValueError as e:
            return errorPage(request, e, status=400)

    def post(self, request, model=None):
        try:
            updateObj = Update(model, request)
            updateObj.handle()
            return HttpResponse('修改数据完成')
        except ValueError as e:
            return HttpResponse(e, status=400)


@method_decorator(checkPerm(), name='dispatch')
class AddView(View):
    def get(self, request, model=None):
        return render(request, "public/AddLayout.html", {
            "model": model
        })

    def post(self, request, model=None):
        batch = Add(model, request)
        result = batch.handleWithLog()
        return HttpResponse("添加成功 %s" % result)


@require_POST
@checkPerm()
def delete(request, model=None):
    batch = Delete(model, request)
    result = batch.handleWithLog()
    return HttpResponse(result)
