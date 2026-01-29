from django.urls import path
from . import views

urlpatterns = [

    #summary
    path('ip-manage/summary/', views.IPManageSummaryAPIView.as_view(), name='ip-manage-summary'),

    #filter
    path('ip-manage/metadata/', views.IPManageMetaDataAPIView.as_view(), name='ip-manage-metadata'),

    #ip list
    path('ip-manage/list/', views.IPListAPIView.as_view(), name='ip-list'),

    #detail and update
    path('ip-manage/<int:ip_id>/', views.IPManageAPIVIEW.as_view(), name='ip-manage'),

    #delete or create
    path('ip-manage/', views.IPManageAPIVIEW.as_view(), name='ip-manage'),

    #####################################################

    path('scan-manualy/<int:ip_id>/', views.ScanAssetInManuallyRange.as_view(), name='scan-manualy'),

    #summary
    path('scanned-asset/<int:ip_id>/summary/', views.AssetInRangeSummaryAPIView.as_view(), name='asset-in-range-summary'),

    #filter
    path('scanned-asset/metadata/', views.AssetInRangeMetaDataAPIView.as_view(), name='asset-in-range-metadata'),

    #asset list
    path('scanned-asset/<int:ip_id>/list/', views.AssetInRangeListAPIView.as_view(), name='asset-in-range-list'),

    #detail and update
    path('scanned-asset/<int:ip_id>/', views.AssetInRagneAPIView.as_view(), name='ip-range-list'),
    #delete
    path('scanned-asset/', views.AssetInRagneAPIView.as_view(), name='ip-range-list'),


    path('scanned-asset/<int:ip_id>/export/', views.AssetInRangeExportAPIView.as_view(), name='ip-range-export'),
]
