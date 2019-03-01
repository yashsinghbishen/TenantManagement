from django.contrib import admin
from django.urls import path, re_path
from tenant import views

urlpatterns = [
    # index page after login
    re_path('^$',views.agent_index,name='agent_index'),

    # adding tenant details in system
    path('add_tenant/',views.add_tenant,name='add_tenant'),
]
