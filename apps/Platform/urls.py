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
from apps.Platform.models import Role
from .views.user import center, setting
from .views.admin import users, roles, perms, logs

app_name = "admin"
RoleModelDict = {'model': Role}

urlpatterns = [
    # 用户管理
    routes.addRoute(r'^users$', users.users, rtype=routes.Type.menu, display='用户管理'),
    routes.addRoute(r'^users/(?P<pk>\d+)/detail$', center.center, rtype=routes.Type.button, display='详情'),
    routes.addRoute(r'^users/(?P<pk>\d+)/edit$', setting.setting, rtype=routes.Type.button, display='编辑'),
    routes.deleteButtonRoute('users', users.batchDelete),
    routes.addRoute(
        '^users/perm$', perms.PermView.as_view(), kwargs={'rType': 'user'}, rtype=routes.Type.panelButton,
        filter='batch-users-perm-button', icon='layui-icon-auz', link=routes.Link.LayerPanel,
        color=routes.BtnColor.Yellow, display='权限设置',
    ),
    routes.addRoute(
        '^users/role$', roles.RolesView.as_view(), rtype=routes.Type.panelButton,
        filter='batch-users-role-button', icon='layui-icon-group', link=routes.Link.LayerPanel,
        color=routes.BtnColor.Yellow, display='角色赋予'
    ),

    routes.addRoute(
        '^users/(?P<pk>\d+)/toggleEnable$', users.toggleEnable, rtype=routes.Type.panelButton,
        filter='users-toggle-enable-button', icon='layui-icon-close',
        color=routes.BtnColor.Yellow, display='禁用/启用'
    ),

    routes.addRoute(
        '^users/add', users.AddView.as_view(), rtype=routes.Type.panelButton,
        filter='users-add-button', icon='layui-icon-username', link=routes.Link.LayerPanel,
        color=routes.BtnColor.Blue, display='新建用户'
    ),

    # 角色管理
    routes.indexPageRoute('roles', roles.roles, display='角色管理'),
    routes.addRoute(
        '^roles/perm$', perms.PermView.as_view(), rtype=routes.Type.panelButton, kwargs={'rType': 'role'},
        filter='batch-roles-perm-button', icon='layui-icon-auz', link=routes.Link.LayerPanel,
        color=routes.BtnColor.Yellow, display='权限设置',
    ),
    routes.deleteButtonRoute('roles', roles.delete),
    routes.editButtonRoute('roles', kwargs=RoleModelDict),
    routes.addButtonRoute('roles', roles.AddView.as_view(), display='新增角色'),

    # 日志审计
    routes.addRoute('^logs$', logs.logs, rtype=routes.Type.menu, display='日志审计'),
]
