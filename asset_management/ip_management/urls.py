from django.urls import path
from . import views

urlpatterns = [
    #ip list
    path('ip-manage/list/', views.IPListAPIView.as_view(), name='ip_list'),

    #detail and update
    path('ip-manage/<int:ip_id>/', views.IPManageAPIVIEW.as_view(), name='ip-manage'),
    #delete
    path('ip-manage/', views.IPManageAPIVIEW.as_view(), name='ip-manage'),


    path('scan-manualy/<int:ip_id>/', views.ScanAssetInManuallyRange.as_view(), name='scan-manualy'),

    #asset list
    path('scanned-asset/list/<int:ip_id>/', views.AssetInRangeListAPIView.as_view(), name='asset-in-range-list'),

    #detail and update
    path('scanned-asset/<int:ip_id>/', views.AssetInRagneAPIView.as_view(), name='ip-range-list'),
    #delete
    path('scanned-asset/delete/', views.AssetInRagneAPIView.as_view(), name='ip-range-list'),


    path('ip-range/export/<int:ip_id>/', views.AssetInRangeExportAPIView.as_view(), name='ip-range-export'),
]
