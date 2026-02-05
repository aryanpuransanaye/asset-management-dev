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
from ip_management.models import IPManage

class AssetSummaryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    MODEL_SUMMARY = [
        {'model': IPManage, 'label': 'تعداد کل ای پی ها', 'color': 'lime', 'permission': 'ip_manage', 'api': 'asset/ip-manage'},
        {'model': DataAndInformation, 'label': 'تعداد کل داده ها و اطلاعات', 'color': 'blue', 'permission': 'data_and_information', 'api': 'asset/data-and-information'},
        {'model': Software, 'label': 'تعداد کل نرم افزارها', 'color': 'indigo', 'permission': 'software', 'api': 'asset/software'},
        {'model': Services, 'label': 'تعداد کل سرویس ها', 'color': 'brown', 'permission': 'services', 'api': 'asset/services'},
        {'model': Hardware, 'label': 'تعداد کل سخت افزار', 'color': 'red', 'permission': 'hardware', 'api': 'asset/hardware'},
        {'model': PlacesAndArea, 'label': 'تعداد کل اماکن و محوطه', 'color': 'purple', 'permission': 'place_and_areas', 'api': 'asset/places-and-areas'},
        {'model': HumanResource, 'label': 'تعداد کل منابع انسانی', 'color': 'orange', 'permission': 'human_resources', 'api': 'asset/human-resource'},
        {'model': InfrastructureAssets, 'label': 'تعداد دارایی های زیرساختی', 'color': 'yellow', 'permission': 'infrastructure_assets', 'api': 'asset/infrastructure-asset'},
        {'model': IntangibleAsset, 'label': 'تعداد کل دارایی های نامشهود', 'color': 'pink', 'permission': 'intangible_assets', 'api': 'asset/intangible-asset'},
        {'model': Supplier, 'label': 'تعداد کل تامین کننده ها', 'color': 'gold', 'permission': 'suppliers', 'api': 'asset/supplier'},
    ]

    def get(self, request):

        summary_data = []

        user_permissions = set(request.user.user_permissions.values_list('codename', flat=True))
        for group in request.user.groups.all():
            group_perms = group.permissions.values_list('codename', flat=True)
            user_permissions.update(group_perms)

        for item in self.MODEL_SUMMARY:
                if any(item['permission'] in perm for perm in user_permissions) or request.user.is_staff:
                    queryset = get_accessible_queryset(request, model=item['model'])
                    summary_data.append({
                        'label': item['label'],
                        'value': queryset.count(),
                        'color': item['color'],
                        'api': item['api']
                    })

        return Response(summary_data, status=status.HTTP_200_OK)