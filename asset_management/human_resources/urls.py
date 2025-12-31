from django.urls import path
from . import views

urlpatterns = [

    #filter
    path('human-resource/metadata/', views.HumanResourcesMetaDataAPIView.as_view(), name='human-resources-metadata'),

    #list
    path('human-resource/list/', views.HumanResourcesListAPIView.as_view(), name='human-resources-list'),

    #update or detail
    path('human-resource/<int:human_resource_id>/', views.HumanResourceAPIView.as_view(), name='human-resources'),

    #delete or create
    path('human-resource/', views.HumanResourceAPIView.as_view(), name='human-resources'),

    path('human-resource/export/', views.HumanResourcesExportAPIView.as_view(), name='human-resources-export'),
]
