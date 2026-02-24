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
        {'model': IPManage, 'label': 'تعداد کل ای پی ها', 'color': 'lime', 'permission': 'ip_manage', 'api': 'asset/ip-manage',
            'icon': 'M21 12a9 9 0 0 1-9 9m9-9a9 9 0 0 0-9-9m9 9H3m9 9a9 9 0 0 1-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 0 1 9-9'
        },
        {'model': DataAndInformation, 'label': 'تعداد کل داده ها و اطلاعات', 'color': 'blue', 'permission': 'data_and_information', 'api': 'asset/data-and-information',
            'icon': 'M20.25 6.375c0 2.278-3.694 4.125-8.25 4.125S3.75 8.653 3.75 6.375m16.5 0c0-2.278-3.694-4.125-8.25-4.125S3.75 4.097 3.75 6.375m16.5 0v11.25c0 2.278-3.694 4.125-8.25 4.125s-8.25-1.847-8.25-4.125V6.375m16.5 0v3.75m-16.5-3.75v3.75'
        },
        {'model': Software, 'label': 'تعداد کل نرم افزارها', 'color': 'indigo', 'permission': 'software', 'api': 'asset/software',
            'icon': 'M17.25 6.75 22.5 12l-5.25 5.25m-10.5 0L1.5 12l5.25-5.25m7.5-3-4.5 18'
        },
        {'model': Services, 'label': 'تعداد کل سرویس ها', 'color': 'brown', 'permission': 'services', 'api': 'asset/services',
            'icon': 'M9 12.75 11.25 15 15 9.75m-3-7.036A11.959 11.959 0 0 1 3.598 6 11.99 11.99 0 0 0 3 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751'
        },
        {'model': Hardware, 'label': 'تعداد کل سخت افزار', 'color': 'red', 'permission': 'hardware', 'api': 'asset/hardware',
            'icon': 'M9 17.25v1.007a3 3 0 0 1-.879 2.122L7.5 21h9l-.621-.621A3 3 0 0 1 15 18.257V17.25m6-12V15a2.25 2.25 0 0 1-2.25 2.25H5.25A2.25 2.25 0 0 1 3 15V5.25m18 0A2.25 2.25 0 0 0 18.75 3H5.25A2.25 2.25 0 0 0 3 5.25m18 0V12a2.25 2.25 0 0 1-2.25 2.25H5.25A2.25 2.25 0 0 1 3 12V5.25'
        },
        {'model': PlacesAndArea, 'label': 'تعداد کل اماکن و محوطه', 'color': 'purple', 'permission': 'place_and_areas', 'api': 'asset/places-and-areas',
            'icon': 'M2.25 21h19.5m-18-18v18m10.5-18v18m6-13.5V21M6.75 6.75h.75m-.75 3h.75m-.75 3h.75m3-6h.75m-.75 3h.75m-9-6h9v12H9V3.75zm0 12h.75m-.75 3h.75m3-3h.75m-.75 3h.75M6.75 21v-3.375c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21'
        },
        {'model': HumanResource, 'label': 'تعداد کل منابع انسانی', 'color': 'orange', 'permission': 'human_resources', 'api': 'asset/human-resource',
            'icon': 'M15.75 6a3.75 3.75 0 1 1-7.5 0 3.75 3.75 0 0 1 7.5 0ZM4.501 20.118a7.5 7.5 0 0 1 14.998 0A17.933 17.933 0 0 1 12 21.75c-2.676 0-5.216-.584-7.499-1.632Z'
        },
        {'model': InfrastructureAssets, 'label': 'تعداد دارایی های زیرساختی', 'color': 'yellow', 'permission': 'infrastructure_assets', 'api': 'asset/infrastructure-asset',
           'icon': 'M3 21v-2a4 4 0 0 1 4-4h10a4 4 0 0 1 4 4v2M7 21V9h10v12M12 3v6'
        },
        {'model': IntangibleAsset, 'label': 'تعداد کل دارایی های نامشهود', 'color': 'pink', 'permission': 'intangible_assets', 'api': 'asset/intangible-asset',
            'icon': 'M12 18v-5.25m0 0a6.01 6.01 0 0 0 1.5-4.125 6.01 6.01 0 0 0-1.5-4.125m0 0a6.01 6.01 0 0 0-1.5 4.125 6.01 6.01 0 0 0 1.5 4.125M12 18a6.01 6.01 0 0 1-1.5-4.125 6.01 6.01 0 0 1 1.5-4.125m0 0a6.01 6.01 0 0 1 1.5 4.125 6.01 6.01 0 0 1-1.5 4.125M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z'
        },
        {'model': Supplier, 'label': 'تعداد کل تامین کننده ها', 'color': 'gold', 'permission': 'suppliers', 'api': 'asset/supplier',
            'icon': 'M21 7.5l-9-5.25L3 7.5m18 0l-9 5.25m9-5.25v9l-9 5.25M3 7.5l9 5.25M3 7.5v9l9 5.25m0-9v9'
        },
    ]

    def get(self, request):

        summary_data = []

        user_permissions = set(request.user.user_permissions.values_list('codename', flat=True))
        for group in request.user.groups.all():
            group_perms = group.permissions.values_list('codename', flat=True)
            user_permissions.update(group_perms)
    
        for item in self.MODEL_SUMMARY:
                if any(f'asset_{item['permission']}' in perm for perm in user_permissions) or request.user.is_staff:
                    queryset = get_accessible_queryset(request, model=item['model'])
                    summary_data.append({
                        'label': item['label'],
                        'value': queryset.count(),
                        'icon': item['icon'],
                        'color': item['color'],
                        'api': item['api'],
                        'permission': item['permission']
                    })

        return Response(summary_data, status=status.HTTP_200_OK)