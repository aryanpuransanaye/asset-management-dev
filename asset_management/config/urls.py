import os
from django.conf import settings
from django.views.static import serve
from django.contrib import admin
from django.urls import path, include, re_path
from accounts.views import MyTokenObtainPairView
from django.views.generic import TemplateView

FRONTEND_DIR = os.path.join(settings.BASE_DIR.parent, 'front-end', 'dist')

urlpatterns = [
    
    path('admin/', admin.site.urls),

    #login
    path('api/token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),

    #account managemnet
    path('accounts/', include('accounts.urls')),

    #asset
    path('asset/', include('ip_management.urls')),
    path('asset/', include('data_and_information.urls')),
    path('asset/', include('software.urls')),
    path('asset/', include('services.urls')),
    path('asset/', include('hardware.urls')),
    path('asset/', include('places_and_areas.urls')),
    path('asset/', include('human_resources.urls')),
    path('asset/', include('infrastructure_assets.urls')),
    path('asset/', include('intangible_assets.urls')),
    path('asset/', include('supplier.urls')),

    #organization
    path('', include('organization.urls')),

    #ticket
    path('', include('ticket.urls')),

    #active directory
    path('', include('active_directory.urls')),

    re_path(r'^assets/(?P<path>.*)$', serve, {'document_root': os.path.join(FRONTEND_DIR, 'assets')}),
    
    re_path(r'^.*$', TemplateView.as_view(template_name='index.html')),
]