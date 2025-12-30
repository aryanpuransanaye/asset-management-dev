from django.urls import path
from . import views

urlpatterns = [

    path('data-and-information/list/', views.DataAndInformationListAPIView.as_view(), name='data-and-information-list'),
    
    #for create and delete
    path('data-and-information/', views.DataAndInformationAPIView.as_view(), name='data-and-information'),

    #for detail and update
    path('data-and-information/<int:pk>/', views.DataAndInformationAPIView.as_view(), name='data-and-information'),
    
    path('data-and-information/export/', views.DataAndInformationExport.as_view(), name='data-and-information-export'),

]
