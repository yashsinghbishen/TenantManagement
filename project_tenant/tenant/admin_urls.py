from django.contrib import admin
from django.urls import path, re_path
from tenant import views

urlpatterns = [
    re_path('^$',views.admin_index, name="admin_index"),
    path('agent_requests/',views.view_agent_request, name="admin_agent_requests"),
    path('agent_active/',views.view_agent_all, name="admin_agent_active"),
    path('agent_request_accept/',views.agent_request_accept, name='admin_agent_request_accept'),
    path('agent_request_reject/',views.agent_request_reject, name='admin_agent_request_reject'),
    path('agent_requests/agent_profile/',views.agent_profile, name='admin_agent_profile'),
    path('agent_action/',views.agent_action, name='admin_agent_action'),
    path('agent_request_search/',views.agent_requests_search, name='admin_agent_requests_search'),
    path('add_master_property/',views.add_master_property,name='admin_add_master_property'),
    path('master_clone_list/',views.create_clone_list,name='admin_create_clone_list'),
    path('add_property/',views.add_property,name='admin_add_property'),
    path('property_clone_list/',views.clone_list,name='admin_show_clone_list'),
]
