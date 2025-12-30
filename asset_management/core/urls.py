from django.urls import path
from .views import FilterOptionsAPIView

urlpatterns = [
    path('general/options/', FilterOptionsAPIView.as_view(), name='filter-options'),
]