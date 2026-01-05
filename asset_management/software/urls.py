from django.urls import path
from . import views

urlpatterns = [

    #summary
    path('software/summary/', views.SoftwareSummaryAPIView.as_view(), name='software-summary'),

    #filter
    path('software/metadata/', views.SoftwareMetaDataAPIView.as_view(), name='software-metadata'),


    #list
    path('software/list/', views.SoftwareListAPIView.as_view(), name='software-list'),

    #update or detail
    path('software/<int:software_id>/', views.SoftWareAPIView.as_view(), name='software'),

    #delete or create
    path('software/', views.SoftWareAPIView.as_view(), name='software'),
   

    path('software/export/', views.SoftWareExportAPIView.as_view(), name='software-export'),


]
