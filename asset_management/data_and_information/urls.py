from django.urls import path
from . import views

urlpatterns = [

    #meta data
    path('data-and-information/metadata/', views.DataInformationMetaDataAPIView.as_view(), name='data-and-information-metadata'),

    #summaty
    path('data-and-information/summary/', views.DataAndInformationSummaryAPIView.as_view(), name='data-and-information-summary'),

    #list
    path('data-and-information/list/', views.DataAndInformationListAPIView.as_view(), name='data-and-information-list'),
    
    #for create and delete
    path('data-and-information/', views.DataAndInformationAPIView.as_view(), name='data-and-information'),

    #for detail and update
    path('data-and-information/<int:data_and_info_id>/', views.DataAndInformationAPIView.as_view(), name='data-and-information'),
    
    path('data-and-information/export/', views.DataAndInformationExport.as_view(), name='data-and-information-export'),

]
