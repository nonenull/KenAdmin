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
from django.urls import include, path
import debug_toolbar
import apps.Platform.urls
import apps.Platform.mainUrls
from . import routes

adminAppName = apps.Platform.urls.app_name
platformAppName = apps.Platform.mainUrls.app_name

debugKey = '__debug__'
urlpatterns = [
    path(debugKey, include(debug_toolbar.urls)),
    routes.addRoute(
        r'',
        include(apps.Platform.mainUrls, namespace=platformAppName),
    ),
    routes.addRoute(
        r'{}/'.format(platformAppName),
        include(apps.Platform.urls, namespace=adminAppName),
        rtype=routes.Type.include,
        display="系统设置"
    ),

]
