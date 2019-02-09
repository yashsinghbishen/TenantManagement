from django.contrib import admin
from django.urls import path, re_path
from tenant import views

urlpatterns = [
    re_path('^$',views.agent_index,name='agent_index'),
    path('add_tenant/',views.add_tenant,name='add_tenant'),
]
