from django.urls import path
from . import views

urlpatterns = [

    #list
    path('supplier/list/', views.SupplierListAPIView.as_view(), name='suppliers-list'),

    #update or detail
    path('supplier/<int:supplier_id>/', views.SupplierAPIView.as_view(), name='suppliers'),

    #delete or create
    path('supplier/', views.SupplierAPIView.as_view(), name='suppliers'),

    path('supplier/export/', views.SupplierExportAPIView.as_view(), name='suppliers-export'),
]
