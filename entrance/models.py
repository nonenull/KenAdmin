# coding=utf-8
from django.apps import apps


class ModelPro(object):
    def __init__(self, *args, **kwargs):
        self.name = "model PRO"

    def getForeignKey(self):
        pass


ModelList = []


def getAllModels():
    appConfigs = apps.app_configs
    for appName in appConfigs:
        if appName != 'CMDB':
            continue

        app = appConfigs.get(appName)
        print('models===', app)
        models = app.models
        print('models===', models)
        for modelName in models:
            modelObj = models.get(modelName)
            print('model obj==', modelObj)
            if issubclass(modelObj, ModelPro):
                ModelList.append(modelObj)

getAllModels()
