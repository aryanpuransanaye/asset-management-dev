from rest_framework import permissions
from rest_framework.permissions import IsAuthenticated
from .models import IPManage, DiscoveredAsset
from data_and_information.models import DataAndInformation
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from . import serializers
from django.shortcuts import get_object_or_404
from itertools import chain
import nmap, openpyxl, jdatetime
from django.db.models import Q
from django.http import HttpResponse
from core.utils import apply_filters_and_sorting, get_accessible_queryset, BaseMetaDataAPIView
from core.permissions import DynamicSystemPermission
from hardware.models import Hardware
from software.models import Software
from services.models import Services
from places_and_areas.models import PlacesAndArea
from infrastructure_assets.models import InfrastructureAssets
from intangible_assets.models import IntangibleAsset
from supplier.models import Supplier
from .utils import get_discovered_asset_config, get_ip_manage_config


class IPManageMetaDataAPIView(BaseMetaDataAPIView):

    model = IPManage
    fields_map = {
            'subnet': 'subnet',
            'vlan': 'vlan',
    }
    choices_fields = {}

class IPListAPIView(APIView):

    permission_classes = [IsAuthenticated, DynamicSystemPermission]
    base_perm_name = 'ip_manage'

    def get(self, request):

        config = get_ip_manage_config()
        ips = apply_filters_and_sorting(
            request, 
            config['sorting'], 
            config['filters'], 
            config['search'], 
            session_key='hardware', 
            model=IPManage
        ).select_related(
            'organization', 
            'sub_organization', 
            'user', 
            'access_level'
        )

        serializer = serializers.IPByUserListSerializer(ips, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



#ip added by user
class IPManageAPIVIEW(APIView):

    permission_classes = [IsAuthenticated, DynamicSystemPermission]
    base_perm_name = 'ip_manage'

    def get(self, request, ip_id=None):
        
        config_form = serializers.IpByUserCreateUpdateSerializer.get_form_config()

        if ip_id:
            accessible_queryset = get_accessible_queryset(request, model=IPManage)
            selected_ip = get_object_or_404(accessible_queryset, id=ip_id)
            serializer = serializers.IpByUserDetailSerializer(selected_ip)

        return Response({
            'result':serializer.data if ip_id else {},
            'config_form': config_form
            }, status = status.HTTP_200_OK)

    def post(self, request):

        serializer = serializers.IpByUserCreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, access_level=request.user.access_level)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, ip_id):
        
        accessible_queryset = get_accessible_queryset(request, model=IPManage)
        selected_ip = get_object_or_404(accessible_queryset, id = int(ip_id))

        serializer = serializers.IpByUserCreateUpdateSerializer(selected_ip, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, *args, **kwargs):

        ids_to_delete = request.data.get('ids', [])
        if not ids_to_delete:
            return Response({'errors': 'there is not id to delete'}, status=status.HTTP_400_BAD_REQUEST)
        
        accessible_queryset = get_accessible_queryset(request, model=IPManage)
        ips = accessible_queryset.filter(id__in = ids_to_delete)

        if not ips.exists():
            return Response({'errors': "not found anything to delete"}, status=status.HTTP_404_NOT_FOUND)
        
    
        deleted_count, _ = ips.delete()

        return Response({'message': f"{deleted_count} things are deleted"}, status=status.HTTP_200_OK)
        
    
class ScanAssetInManuallyRange(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, ip_id):
        
        models_with_ip = [
            DiscoveredAsset, DataAndInformation, Software,
            Hardware, Services, PlacesAndArea, InfrastructureAssets,
            IntangibleAsset, Supplier
        ]

        existing_ips = set(
            ip for ip in chain.from_iterable(
                m.objects.values_list('ipaddress', flat=True)
                for m in models_with_ip
            ) if ip
        )

        
        selected_range = get_object_or_404(IPManage, id=ip_id)
        ip_target = f'{selected_range.ipaddress}/{selected_range.subnet}'

        nm = nmap.PortScanner()
        try:
            nm.scan(hosts=ip_target, arguments='-sn -T4')
        except Exception as e:
            return Response({'error': f'اسکن با خطا مواجه شد: {str(e)}'}, status=500)

        alive_hosts = [
            ip for ip in nm.all_hosts()
            if nm[ip]['status']['state'] == 'up' and ip not in existing_ips
        ]

        if not alive_hosts:
            return Response({'message': "آی‌پی جدیدی در این رنج پیدا نشد."}, status=200)
        
        new_assets_data = []

        for ip in alive_hosts:
            try:
                nm.scan(hosts=ip, arguments='-O -T4')
                host = nm[ip]
            except Exception:
                continue

            mac = host.get('addresses', {}).get('mac', '-')
            os_type = '-'
            vendor = '-'

            osinfo = host.get('osmatch', [])
            if osinfo:
                os_type = osinfo[0].get('name', '-')
                osclass = osinfo[0].get('osclass', [])
                if osclass:
                    vendor = osclass[0].get('vendor', '-')

            if mac != '-' and mac in host.get('vendor', {}):
                vendor = host['vendor'][mac]
     
            asset_data = {
                'network_range': selected_range.id,
                'ipaddress': ip,
                'mac': mac,
                'os': os_type,
                'vendor': vendor,
                'access_level': request.user.access_level.id if hasattr(request.user, 'access_level') and request.user.access_level else None,
                'user': request.user.id
            }
            new_assets_data.append(asset_data)

        serializer = serializers.CreateScannedAssetSerializer(data=new_assets_data, many=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': f'تعداد {len(new_assets_data)} دارایی جدید شناسایی و ثبت شد.',
                'detected_ips': alive_hosts
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#asset added by scan

class AssetInRangeMetaDataAPIView(BaseMetaDataAPIView):

    model = DiscoveredAsset
    fields_map = {}
    choices_fields = {'category': 'category'}

class AssetInRangeListAPIView(APIView):

    permission_classes = [IsAuthenticated, DynamicSystemPermission]
    base_perm_name = 'ip_manage'

    def get(self, request, ip_id):

        accessible_queryset = get_accessible_queryset(request, model=IPManage)
        selected_range = get_object_or_404(accessible_queryset, id=ip_id)
        asset_by_range = DiscoveredAsset.objects.filter(network_range = selected_range)

        
        config = get_discovered_asset_config()
        assets = apply_filters_and_sorting(
            request, 
            config['sorting'], 
            config['filters'], 
            config['search'], 
            session_key='hardware', 
            query_set=asset_by_range
        ).select_related(
            'organization', 
            'sub_organization', 
            'user', 
            'access_level'
        )
    
        serializer = serializers.AssetInManualyRangeListSerializer(assets, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    


class AssetInRagneAPIView(APIView):

    permission_classes = [IsAuthenticated, DynamicSystemPermission]
    base_perm_name = 'ip_manage'

    def get(self, request, ip_id):

        accessible_queryset = get_accessible_queryset(request, model=DiscoveredAsset)
        selected_asset = get_object_or_404(accessible_queryset, id= ip_id)
        serializer = serializers.AssetInManualyRangeDetail(selected_asset)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
    def patch(self, request, ip_id):
        
        accessible_queryset = get_accessible_queryset(request, model=DiscoveredAsset)
        selected_asset = get_object_or_404(accessible_queryset, id = ip_id)

        serializer = serializers.AssetInManualyRangeUpdate(selected_asset, data=request.data, partial = True, context={'reqeust': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    
    def delete(self, request, *args, **kwargs):
        
        ids_to_delete = request.data.get('ids', [])
        if not ids_to_delete:
            return Response({'errors': 'there is not id to delete'}, status=status.HTTP_400_BAD_REQUEST)
        
        accessible_queryset = get_accessible_queryset(request, model=DiscoveredAsset)
        assets = accessible_queryset.filter(id__in = ids_to_delete)

        if not assets.exists():
            return Response({'errors': "not found anything to delete"}, status=status.HTTP_404_NOT_FOUND)
        
    
        deleted_count, _ = assets.delete()

        return Response({'message': f"{deleted_count} things are deleted"}, status=status.HTTP_200_OK)

    

class AssetInRangeExportAPIView(APIView):
    
    permission_classes = [IsAuthenticated, DynamicSystemPermission]
    base_perm_name = 'ip_manage'

    def get(self, request, ip_id):

        accessible_queryset = get_accessible_queryset(request, model=IPManage)
        selected_range = get_object_or_404(accessible_queryset, id=ip_id)
        asset_by_range = DiscoveredAsset.objects.filter(network_range = selected_range)

        config = get_discovered_asset_config()
        discovered_assets = apply_filters_and_sorting(
            request, 
            config['sorting'], 
            config['filters'], 
            config['search'], 
            session_key='hardware', 
            query_set=asset_by_range
        ).select_related(
            'organization', 
            'sub_organization', 
            'user', 
            'access_level'
        )

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = 'دارایی های اسکن شد'

        fields = discovered_assets.model._meta.fields

        header = [field.verbose_name for field in fields]
        ws.append(header)
        
        for thing in discovered_assets:
            row = []
            for field in fields:
                value = getattr(thing, field.name)

                if field.name == 'user' and value:
                    value = value.username
                elif field.name == 'access_level' and value:
                    value = value.level_name
                elif field.name == 'category' and value:
                    value = str(thing.get_category_display())
                elif field.name == 'network_range' and value:
                    value = thing.network_range.ipaddress
                elif field.name == 'created_at' and value: 
                    value = jdatetime.datetime.fromgregorian(datetime=value).strftime('%Y/%m/%d %H:%M')
                elif field.name == 'updated_at' and value: 
                    value = jdatetime.datetime.fromgregorian(datetime=value).strftime('%Y/%m/%d %H:%M')

                row.append(value if value else '-')
            ws.append(row)
        
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="ipinrange.xlsx"'
        ws.sheet_view.rightToLeft = True
        wb.save(response)
        return response