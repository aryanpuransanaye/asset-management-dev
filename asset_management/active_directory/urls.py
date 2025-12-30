from django.urls import path
from . import views

urlpatterns = [
    #list
    path('active-directory/list/', views.ActiveDirectoryListAPIView.as_view(), name='active-directory-list'),

    #update or detail
    path('active-directory/<int:active_directory_id>/', views.ActiveDirectoryAPIView.as_view(), name='active-directory'),

    #delete or create
    path('active-directory/', views.ActiveDirectoryAPIView.as_view(), name='active-directory'),

    #test
    path('active-directory-test/<int:active_directory_id>/', views.ActiveDirectoryTestConnectionAPIView.as_view(), name='active-directory-test'),

    #scan
    path('active-directory-scan/<int:active_directory_id>/', views.ActiveDirectoryScannerAPIView.as_view(), name='active-directory-scan'),
]
