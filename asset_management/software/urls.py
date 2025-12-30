from django.urls import path
from . import views

urlpatterns = [
    #list
    path('software/list/', views.SoftwareListAPIView.as_view(), name='software-list'),

    #update or detail
    path('software/<int:software_id>/', views.SoftWareAPIView.as_view(), name='software-list'),

    #delete or create
    path('software/delete/', views.SoftWareAPIView.as_view(), name='software-list'),
   

    path('software/export/', views.SoftWareExportAPIView.as_view(), name='software-list'),


]
