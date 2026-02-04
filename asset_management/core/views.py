from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
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
        {"model": DataAndInformation, "label": "تعداد کل داده ها و اطلاعات", "color": "blue", "permission": "data_and_information"},
        {"model": Software, "label": "تعداد کل نرم افزارها", "color": "indigo", "permission": "software"},
        {"model": Services, "label": "تعداد کل سرویس ها", "color": "brown", "permission": "services"},
        {"model": Hardware, "label": "تعداد کل سخت افزار", "color": "red", "permission": "hardware"},
        {"model": PlacesAndArea, "label": "تعداد کل اماکن و محوطه", "color": "purple", "permission": "place_and_areas"},
        {"model": HumanResource, "label": "تعداد کل منابع انسانی", "color": "orange", "permission": "human_resources"},
        {"model": InfrastructureAssets, "label": "تعداد دارایی های زیرساختی", "color": "yellow", "permission": "infrastructure_assets"},
        {"model": IntangibleAsset, "label": "تعداد کل دارایی های نامشهود", "color": "pink", "permission": "intangible_assets"},
        {"model": Supplier, "label": "تعداد کل تامین کننده ها", "color": "gold", "permission": "suppliers"},
    ]

    def get(self, request):

        summary_data = []

        user_permissions = set(request.user.user_permissions.values_list('codename', flat=True))
        for group in request.user.groups.all():
            group_perms = group.permissions.values_list('codename', flat=True)
            user_permissions.update(group_perms)

        for item in self.MODEL_SUMMARY:
                if any(item['permission'] in perm for perm in user_permissions) or request.user.is_staff:
                    queryset = get_accessible_queryset(request, model=item["model"])
                    summary_data.append({
                        "label": item["label"],
                        "value": queryset.count(),
                        "color": item["color"]
                    })

        return Response(summary_data, status=status.HTTP_200_OK)