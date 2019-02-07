from django.contrib import admin
from django.urls import path, re_path
from tenant import views

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path('',views.index, name= 'index'),
    re_path('^agent_requests/',views.view_agent_request, name="agent_requests"),
    path('login/',views.do_login, name= 'login'),
]
