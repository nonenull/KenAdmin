"""OMS URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from entrance import routes
from .views import platform
from .views.user import center, setting, user
from apps.Platform.views import related, model

app_name = "platform"

urlpatterns = [
    routes.addRoute(r'^$', platform.homepage, name='homepage'),
    #
    routes.addRoute(r'^user/login$', user.LoginView.as_view(), name='login'),
    routes.addRoute(r'^user/logout$', user.logout, name='logout'),
    routes.addRoute(r'^user/(?P<pk>\d+)/center$', center.center, name='center'),
    # settings
    routes.addRoute(r'^user/(?P<pk>\d+)/setting$', setting.setting, name='setting'),
    routes.addRoute(r'^user/(?P<pk>\d+)/setting/edit$', setting.editUser, name='setting.editUser'),
    routes.addRoute(r'^user/(?P<pk>\d+)/setting/changePassword$', setting.changePassword, name='setting.changePassword'),

    # 便捷关联数据增删改查
    routes.addRoute(r'^related/(?P<model>[a-z._]+)/(?P<modelId>\d+)/(?P<relatedModel>[a-z._]+)$', related.related, name="related"),
    routes.addRoute(r'^related/readonly/(?P<model>[a-z._]+)/(?P<modelId>\d+)/(?P<relatedModel>[a-z._]+)$', related.relatedReadOnly, name="related.readonly"),
    routes.addRoute(
        r'^related/add/(?P<model>[a-z._]+)/(?P<modelId>\d+)/(?P<relatedModel>[a-z._]+)$',
        related.AddView.as_view(),
    ),
    routes.addRoute(
        r'^related/edit/(?P<model>[a-z._]+)/(?P<modelId>\d+)/(?P<relatedModel>[a-z._]+)/(?P<relatedModelId>\d+)$',
        related.EditView.as_view(),
    ),
    routes.addRoute(
        r'^related/delete/(?P<model>[a-z._]+)/(?P<modelId>\d+)/(?P<relatedModel>[a-z._]+)$',
        related.delete,
    ),

    # 动态指定模型表增删
    routes.addRoute(
        r'^model/(?P<model>[a-z._]+)/add$',
        model.AddView.as_view(),
        name="model.add"
    ),
    routes.addRoute(
        r'^model/(?P<model>[a-z._]+)/delete$',
        model.delete,
        name="model.delete"
    ),
]
