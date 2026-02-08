from django.conf import settings
from django.contrib import admin
from django.urls import path, include, re_path
from accounts.views import MyTokenObtainPairView
from . import views
from django.views.static import serve

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('accounts/', include('accounts.urls')),
    
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
    
    path('', include('organization.urls')),
    path('', include('ticket.urls')),
    path('', include('active_directory.urls')),
    path('summary/', include('core.urls')),
    
    re_path(r'^_nuxt/(?P<path>.*)$', serve, {'document_root': settings.BASE_DIR / 'frontend_dist' / '_nuxt'}),
    
    re_path(r'^(?P<path>(.*\.png|.*\.jpg|.*\.jpeg|.*\.svg|.*\.ico|.*\.json|.*\.webmanifest))$', 
            serve, {'document_root': settings.BASE_DIR / 'frontend_dist'}),

    re_path(r'^(?!api|admin|media|static|_nuxt).*$', views.serve_frontend),
]

if settings.DEBUG:
    pass