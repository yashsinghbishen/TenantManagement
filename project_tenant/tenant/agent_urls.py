from django.contrib import admin
from django.urls import path, re_path
from tenant import views

urlpatterns = [
    # index page after login
    re_path('^$',views.agent_index,name='agent_index'),

    # adding tenant details in system
    # path('add_tenant/',views.add_tenant,name='add_tenant'),
    re_path('AddTenant/',views.addTenant,name='addTenant'),
    path('ViewTenants/',views.view_tenants,name='view_tenants'),
    path('tenant_search_list/',views.tenant_search_result,name='tenant_search_result'),
    path('Agent_Properties/',views.allocated_property_list,name='allocated_property_view'),
    re_path(r'^(?P<tid>[\w\-]+)/Tenant_Profile_view/',views.TenantDetails,name='TenantDetails'),
    path('Change_tenant_status/',views.change_tenant_status,name='change_tenant_status'),
    path('get_Tenant_list/',views.get_Tenant_list,name='get_Tenant_list'),
    path('allocate_property/',views.allocate_property,name='allocate_property'),
    path('deallocate_property/',views.deallocate_property,name='deallocate_property'),
    path('add_visit/',views.add_visit,name='add_visit'),
     # to change tenant status for property
    path('tenant_status_change/',views.change_status,name='change_status'),
    path('get_tenant_visit/',views.get_tenant_visit,name='tenant_visit_select'),
    path('get_deactivated_tenant/',views.get_deactivated_tenant,name='get_deactivated_tenant'),
    path('activate_tenant/',views.invoke_tenant),
    path('add_rent/',views.add_rent_collected,name='add_rent'),
    path('get_tenant_visit',views.get_tenant_visit,name='get_tenant_visit'),
    path('check_allocation/',views.check_allocation,name='check_allocation'),
 
    
]
