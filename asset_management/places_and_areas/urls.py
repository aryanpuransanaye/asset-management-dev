from django.urls import path
from . import views

urlpatterns = [

    #filter
    path('places-and-areas/metadata/', views.PlacesAndAreasMetaDataAPIView.as_view(), name='places-and-areas-metadata'),

    #list
    path('places-and-areas/list/', views.PlacesAndAreasListAPIView.as_view(), name='places-and-areas-list'),

    #update or detail
    path('places-and-areas/<int:place_and_area_id>/', views.PlacesAndAreasAPIView.as_view(), name='places-and-areas'),

    #delete or create
    path('places-and-areas/', views.PlacesAndAreasAPIView.as_view(), name='places-and-areas'),

    path('places-and-areas/export/', views.PlacesAndAreasExportAPIView.as_view(), name='places-and-areas-export'),
]
