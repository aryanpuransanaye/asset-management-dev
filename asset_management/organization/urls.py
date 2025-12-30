from django.urls import path
from . import views

urlpatterns = [
    #ORGANIZATION

    #list
    path('organization/list/', views.OrganizationListAPIView.as_view(), name='organization-list'),

    #update or detail
    path('organization/<int:organization_id>/', views.OrganizationAPIView.as_view(), name='organization'),

    #delete or create
    path('organization/', views.OrganizationAPIView.as_view(), name='organization'),

    ###SUB ORGANIZATION###

    #list
    path('sub-organization/list/<int:organization_id>/', views.SubOrganizationListAPIView.as_view(), name='sub-organization-list'),

    #update or detail
    path('sub-organization/<int:sub_organization_id>/', views.SubOrganizationAPIView.as_view(), name='sub-organization'),

    #delete or create
    path('sub-organization/', views.SubOrganizationAPIView.as_view(), name='sub-organization'),

    
]
