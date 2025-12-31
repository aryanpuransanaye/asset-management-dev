from django.urls import path
from . import views

urlpatterns = [

    #filter
    path('infrastructure-asset/metadata/', views.InfrastructureAssetsMetaDataAPIView.as_view(), name='infrastructure-assets-metadata'),
    
    #list
    path('infrastructure-asset/list/', views.InfrastructureAssetsListAPIView.as_view(), name='infrastructure-assets-list'),

    #update or detail
    path('infrastructure-asset/<int:infrastructure_asset_id>/', views.InfrastructureAssetsAPIView.as_view(), name='infrastructure-assets'),

    #delete or create
    path('infrastructure-asset/', views.InfrastructureAssetsAPIView.as_view(), name='infrastructure-assets'),

    path('infrastructure-asset/export/', views.InfrastructureAssetsExportAPIView.as_view(), name='infrastructure-assets-export'),
]
