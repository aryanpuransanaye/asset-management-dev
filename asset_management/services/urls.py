from django.urls import path
from . import views

urlpatterns = [

    #list
    path('services/list/', views.ServicesListAPIView.as_view(), name='services'),

    #update or detail
    path('services/<int:service_id>/', views.ServicesAPIView.as_view(), name='services'),

    #delete or create
    path('services/', views.ServicesAPIView.as_view(), name='services'),

    path('services/export/', views.ServicesExportAPIView.as_view(), name='services'),
]
