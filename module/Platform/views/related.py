# coding=utf-8
from django.db.models import ManyToOneRel, ManyToManyRel
from django.http import HttpResponse
from django.shortcuts import render
from django.views import View
from django.apps import apps
from django.views.decorators.http import require_POST

from entrance.automate.curd.fs import FS
from entrance.automate.curd.delete import Delete
from entrance.automate.curd.add import Add
from entrance.automate.curd.retrieve import Retrieve
from entrance.automate.curd.update import Update
from entrance.automate.perms import errorPage
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

modelDict = {}
models = apps.get_models()
for model in models:
    name = str(getattr(model, '_meta')).lower()
    modelDict[name] = model


def getRelatedModelObj(model, relatedModel, modelId):
    if model not in modelDict:
        raise ValueError('模型不存在')
    if relatedModel not in modelDict:
        raise ValueError('关联模型不存在')

    modelCls = modelDict[model]
    relatedModelCls = modelDict[relatedModel]
    modelObj = modelCls.objects.get(id=modelId)

    obj = None

    for field in modelObj._meta.get_fields():
        curRelatedModel = field.related_model
        if not curRelatedModel or curRelatedModel != relatedModelCls:
            continue
        logger.debug("field====%s", field)

        if isinstance(field, (ManyToOneRel, ManyToManyRel)):
            obj = getattr(modelObj, field.get_accessor_name())
        else:
            obj = getattr(modelObj, field.name)

    if not obj:
        raise ValueError('模型间不存在关联')

    return obj.all()


def related(request, model, relatedModel, modelId):
    try:
        relatedData = getRelatedModelObj(model, relatedModel, modelId)
        fs = FS(relatedData, request)
        return render(request, 'related/related.html', {
            "queryset": fs.handle(),
        })
    except ValueError as e:
        return errorPage(request, e, 400)


def relatedReadOnly(request, model, relatedModel, modelId):
    try:
        relatedData = getRelatedModelObj(model, relatedModel, modelId)
        fs = FS(relatedData, request)
        return render(request, 'related/relatedReadOnly.html', {
            "queryset": fs.handle(),
        })
    except ValueError as e:
        return errorPage(request, e, 400)


"""
def relatedWithParam(request, model, relatedModel):
    try:
        modelId = request.GET.get('id')
        return related(request, model, relatedModel, modelId)
    except ValueError as e:
        return errorPage(relatedModel, e, 400)
"""


@require_POST
def delete(request, model, relatedModel, modelId):
    logger.debug("this is related delete")
    try:
        relatedData = getRelatedModelObj(model, relatedModel, modelId)
        batch = Delete(relatedData, request)
        result = batch.handleWithLog()
        return HttpResponse(result)
    except ValueError as e:
        return errorPage(request, e, 400)


"""
def deleteWithParam(request, model, relatedModel):
    modelId = request.GET.get('id')
    return delete(request, model, relatedModel, modelId)
"""


class AddView(View):
    def get(self, request, model, relatedModel, modelId):
        return render(request, "related/add.html", {
            "model": modelDict[relatedModel],
        })

    def post(self, request, model, relatedModel, modelId):
        batch = Add(modelDict[relatedModel], request, unique=True)
        result = batch.handleWithLog()
        return HttpResponse("添加成功 %s" % result)


"""
class AddViewWithParam(View):
    def get(self, request, model, relatedModel):
        modelId = request.GET.get('id')
        addView = AddView.as_view()
        return addView.get(request, model, relatedModel, modelId)

    def post(self, request, model, relatedModel):
        modelId = request.GET.get('id')
        addView = AddView.as_view()
        return addView.post(request, model, relatedModel, modelId)
"""


class EditView(View):
    def get(self, request, model, relatedModel, modelId, relatedModelId):
        try:
            logger.debug("modelDict[relatedModel]=======%s", modelDict[relatedModel])
            rObj = Retrieve(relatedModelId, modelDict[relatedModel], request)
            result = rObj.handle()
            return render(request, 'related/edit.html', {
                "queryset": result
            })
        except ValueError as e:
            return errorPage(request, e, status=400)

    def post(self, request, model, relatedModel, modelId, relatedModelId):
        try:
            updateObj = Update(relatedModelId, modelDict[relatedModel], request)
            updateObj.handle()
            return HttpResponse('修改数据完成')
        except ValueError as e:
            return HttpResponse(e, status=400)
