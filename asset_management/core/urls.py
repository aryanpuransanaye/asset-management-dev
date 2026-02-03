from django.urls import path
from . import views

urlpatterns = [
    # assets summary total

    path('asset-total/', views.AssetSummaryAPIView.as_view(), name='asset-total-summary')

]
