from django.urls import path
from . import views

urlpatterns = [

    #summary
    path('intangible-asset/summary/', views.IntangibleAssetsSummaryAPIView.as_view(), name='intangible-assets-summary'),

    #filter
    path('intangible-asset/metadata/', views.IntangibleAssetsMetaDataAPIView.as_view(), name='intangible-assets-metadata'),

    #list
    path('intangible-asset/list/', views.IntangibleAssetsListAPIView.as_view(), name='intangible-assets-list'),

    #update or detail
    path('intangible-asset/<int:intangible_asset_id>/', views.IntangibleAssetsAPIView.as_view(), name='intangible-assets'),

    #delete or create
    path('intangible-asset/', views.IntangibleAssetsAPIView.as_view(), name='intangible-assets'),

    path('intangible-asset/export/', views.IntangibleAssetsExportAPIView.as_view(), name='intangible-assets-export'),
]
