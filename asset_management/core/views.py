from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
# from . import serializers
# from django.shortcuts import get_object_or_404
# import openpyxl, jdatetime
# from django.http import HttpResponse
# from django.db.models import Q, Count
# from core.utils import apply_filters_and_sorting, get_accessible_queryset, set_paginator, BaseMetaDataAPIView
# from core.permissions import DynamicSystemPermission
# from .utils import get_data_and_information_config

from .utils import get_accessible_queryset
from data_and_information.models import DataAndInformation
from hardware.models import Hardware
from human_resources.models import HumanResource
from infrastructure_assets.models import InfrastructureAssets
from intangible_assets.models import IntangibleAsset
from places_and_areas.models import PlacesAndArea
from services.models import Services
from software.models import Software
from supplier.models import Supplier

class AssetSummaryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    MODEL_SUMMARY = [
        {"model": DataAndInformation, "label": "تعداد کل داده ها و اطلاعات", "color": "blue"},
        {"model": Hardware, "label": "تعداد کل سخت افزار", "color": "red"},
        {"model": HumanResource, "label": "تعداد کل منابع انسانی", "color": "orange"},
        {"model": InfrastructureAssets, "label": "تعداد دارایی های زیرساختی", "color": "yellow"},
        {"model": IntangibleAsset, "label": "تعداد کل دارایی های نامشهود", "color": "pink"},
        {"model": PlacesAndArea, "label": "تعداد کل اماکن و محوطه", "color": "purple"},
        {"model": Services, "label": "تعداد کل سرویس ها", "color": "brown"},
        {"model": Software, "label": "تعداد کل نرم افزارها", "color": "indigo"},
        {"model": Supplier, "label": "تعداد کل تامین کننده ها", "color": "gold"},
    ]

    def get(self, request):
        summary_data = []

        for item in self.MODEL_SUMMARY:
            queryset = get_accessible_queryset(request, model=item["model"])
            summary_data.append({
                "label": item["label"],
                "value": queryset.count(),
                "color": item["color"]
            })

        return Response(summary_data, status=status.HTTP_200_OK)