from django.urls import path
from . import views

urlpatterns = [
    #list
    path('hardware/list/', views.HardwareListAPIView.as_view(), name='hardware-list'),

    #update or detail
    path('hardware/<int:hardware_id>/', views.HardwareAPIView.as_view(), name='hardware-list'),

    #delete or create
    path('hardware/', views.HardwareAPIView.as_view(), name='hardware-list'),
   

    path('hardware/export/', views.HardwareExportAPIView.as_view(), name='hardware-list'),

]
