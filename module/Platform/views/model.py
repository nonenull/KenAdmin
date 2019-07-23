# coding=utf-8
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views import View
import logging

from django.views.decorators.http import require_POST
from django.forms.models import model_to_dict
from entrance.automate.curd.add import Add
from entrance.automate.curd.delete import Delete
from entrance.automate.perms import errorPage
from module.Platform.views.related import modelDict

logger = logging.getLogger(__name__)


class AddView(View):
    def get(self, request, model):
        if model not in modelDict:
            return errorPage(request, "模型不存在", 400)

        return render(request, "model/add.html", {
            "model": modelDict[model]
        })

    def post(self, request, model):
        if model not in modelDict:
            return errorPage(request, "模型不存在", 400)

        batch = Add(modelDict[model], request)
        result = batch.handleWithLog()
        return JsonResponse({'itemId': result.id, 'cname': result.__str__()})


@require_POST
def delete(request, model):
    logger.debug("this is related delete")

    if model not in modelDict:
        return errorPage(request, "模型不存在", 400)

    batch = Delete(modelDict[model], request)
    result = batch.handleWithLog()
    return HttpResponse(result)
