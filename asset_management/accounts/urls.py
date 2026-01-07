from django.urls import path
from . import views


urlpatterns = [

    path('login/send-otp/', views.LoginStepOneAPIView.as_view(), name='send-otp'),
    path('login/verify-otp/', views.LoginStepTwoAPIView.as_view(), name='verify-otp'),
    path('logout/', views.LogoutUserAPIView.as_view(), name='user-logout'),

    path('user-profile/', views.UserProfileAPIView.as_view(), name='user-profile'),

    path('change-password/', views.ChangePasswordAPIView.as_view(), name='change-password'),
    path('change-password-by-admin/<int:user_id>/', views.ChangeUserPasswordByAdminAPIView.as_view(), name='change-user-password-by-admin'),

    path('change-group/<int:user_id>/', views.UserGroupAssignmentAPIView.as_view(), name='change-user-group'),
    path('change-permissions/<int:user_id>/', views.UserPermissionAssignmentAPIView.as_view(), name='set-user-permissions'),

    path('access-level/', views.AccessLevelAPIView.as_view(), name='access-level'),
    path('access-level/change/<int:access_id>/', views.AccessLevelAPIView.as_view(), name='access-level'),


    path('user-summary/', views.UserSummaryAPIView.as_view(), name='user-summary'),
    path('users-list/', views.UserListAPIView.as_view(), name='user-list'),
    path('user-detail/<int:user_id>/', views.UserDetailAPIView.as_view(), name='user-detail'),
    path('user-detail/', views.UserDetailAPIView.as_view(), name='user-detail'),

    path('permissions-list/', views.PermissionsListAPIView.as_view(), name='permissions-list'),

    path('groups-list/', views.GroupsListAPIView.as_view(), name='groups-list'),
    path('group-detail/<int:group_id>/', views.GroupsDetailAPIView.as_view(), name='group-detail'),
    path('group-detail/', views.GroupsDetailAPIView.as_view(), name='group-detail'),

    path('users/export/', views.ExportUserAPIView.as_view(), name='export-users')
    # path('create-group/', views.GroupsCreateAPIView.as_view(), name='create-group'),

]