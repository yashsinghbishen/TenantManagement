"""project_tenant URL Configuration

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
from django.contrib import admin
from django.urls import path, re_path
from tenant import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/',views.do_login, name= 'login'),
    path('agent_requests/',views.view_agent_request, name="agent_requests"),
    re_path('^$',views.index, name= 'index'),
    path('agent_request_accept/',views.agent_request_accept, name='agent_request_accept'),
    path('agent_request_reject/',views.agent_request_reject, name='agent_request_reject'),
    path('agent_profile/',views.agent_profile, name='agent_profile'),
]
