from rest_framework import permissions
from rest_framework.permissions import IsAuthenticated
from .models import IPManage, DiscoveredAsset, ScanHistory
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from . import serializers
from django.shortcuts import get_object_or_404
import openpyxl, jdatetime, ipaddress, threading
from django.db.models import Q, Count
from django.http import HttpResponse
from core.utils import apply_filters_and_sorting, get_accessible_queryset, set_paginator, BaseMetaDataAPIView
from core.permissions import DynamicSystemPermission
from .utils import get_discovered_asset_config, get_ip_manage_config
from .scanning import start_scanning_celery
from django.db.models import OuterRef, Subquery

config_ip_manage = get_ip_manage_config()
config_discovered_asset = get_discovered_asset_config()


class IPManageSummaryAPIView(APIView):

    permission_classes = [IsAuthenticated, DynamicSystemPermission]
    base_perm_name = 'ip_manage'

    def get(self, request):

        accessible_queryset = get_accessible_queryset(request, model=IPManage)

        total_ips = accessible_queryset.count()


        summary_data = [
            {'label': 'تعداد کل آی‌پی‌ها', 'value': total_ips, 'color': 'blue'},
        ]

        return Response(summary_data, status=status.HTTP_200_OK)


class IPManageMetaDataAPIView(BaseMetaDataAPIView):

    model = IPManage
    fields_map = {field:field for field in config_ip_manage['filters']}
    search_fields = config_ip_manage['search']


class IPListAPIView(APIView):

    permission_classes = [IsAuthenticated, DynamicSystemPermission]
    base_perm_name = 'ip_manage'

    def get(self, request):

        ips = apply_filters_and_sorting(
            request, 
            config_ip_manage['sorting'], 
            config_ip_manage['filters'], 
            config_ip_manage['search'], 
            session_key='ipmanage', 
            model=IPManage
        ).select_related('user', 'access_level')

        latest_scan = ScanHistory.objects.filter(network_range=OuterRef('pk')).order_by(
            '-created_at'
        )

        paginator = set_paginator(request, ips)
        serializer = serializers.IPByUserListSerializer(paginator['data'], many=True)
        columns = serializers.IPByUserListSerializer.get_active_columns()
        
        return Response({
            'results':serializer.data,
            'total_pages': paginator['total_pages'],
            'current_page': paginator['current_page'],
            'total_items': paginator['total_items'],
            'columns': columns
        }, status=status.HTTP_200_OK)


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
    base_perm_name = 'can_use_scanners'


    def get(self, request, ip_id):
        scan_record = ScanHistory.objects.filter(network_range_id=ip_id).order_by('-created_at').first()
        if not scan_record:
            return Response({'detail': 'not found'}, status=status.HTTP_404_NOT_FOUND)

        return Response({
            'status': scan_record.status,
            'result_count': scan_record.result_count
        }, status=status.HTTP_200_OK)
    
    
    def delete(self, request, ip_id):
        scan_record = ScanHistory.objects.filter(network_range_id=ip_id).order_by('-created_at').first()
        if not scan_record:
            return Response({'detail': 'not found'}, status=status.HTTP_404_NOT_FOUND)

        if scan_record.status != 'running':
            return Response({'message': 'scan is not running', 'status': scan_record.status}, status=status.HTTP_400_BAD_REQUEST)

        scan_record.status = 'canceled'
        scan_record.error_message = 'Canceled by user'
        scan_record.save()

        return Response({'message': 'اسکن کنسل شد'}, status=status.HTTP_200_OK)
    

    def post(self, request, ip_id):
        # thread = threading.Thread(
        #     target=start_scanning,
        #     args=(ip_id, request.user, request.user.access_level)
        # )
        # thread.start()
        
        latest = ScanHistory.objects.filter(network_range_id=ip_id).order_by('-created_at').first()
        if latest and latest.status == 'running':
            return Response({'message': 'اسکن در حال اجرا است'}, status=status.HTTP_200_OK)

        scan_record = ScanHistory.objects.create(
            network_range_id=ip_id,
            status='running',
            user_id=request.user.id
        )
        # pass the scan_record id so the celery task works on the exact record
        start_scanning_celery.delay(ip_id, request.user.id, request.user.access_level.id, scan_record.id)
        return Response({'message': 'اسکن شروع شد'}, status=status.HTTP_202_ACCEPTED)

#asset added by scan

class AssetInRangeSummaryAPIView(APIView):

    permission_classes = [IsAuthenticated, DynamicSystemPermission]
    base_perm_name = 'ip_manage'

    def get(self, request, ip_id):

        accessible_queryset = get_accessible_queryset(request, model=IPManage)
        selected_range = get_object_or_404(accessible_queryset, id=ip_id)
        asset_by_range = DiscoveredAsset.objects.filter(network_range = selected_range)

        total_assets = asset_by_range.count()
        last_scanned_item = asset_by_range.order_by('-created_at').first()

        assets_by_category = asset_by_range.aggregate(
            assets_category_selected = Count('id', filter=Q(category__isnull=False)),
            assets_category_not_selected = Count('id', filter=Q(category__isnull=True)),
        )

        most_recent_category = asset_by_range.values('category').annotate(
            count=Count('id')
        ).order_by('-count').first()

        network = ipaddress.IPv4Network(f'{selected_range.ipaddress}/{selected_range.subnet}', strict=False)
        total_hosts = max(0, network.num_addresses - 2)
        used_hosts = len(asset_by_range)

        summary_data = [
            {'label': 'تعداد کل دارایی‌ها', 'value': total_assets, 'color': 'blue'},
            {'label': 'جدیدترین دارایی اسکن شده', 'value': last_scanned_item.mac if last_scanned_item else 'دارایی ثبت نشده', 'color': 'grey'},
            {'label': 'دارایی‌ها با دسته‌بندی انتخاب شده', 'value': assets_by_category['assets_category_selected'], 'color': 'green'},
            {'label': 'دارایی‌ها بدون دسته‌بندی', 'value': assets_by_category['assets_category_not_selected'], 'color': 'orange'},
            {'label': 'پر تکرارترین دسته‌بندی', 'value': dict(DiscoveredAsset.CATEGORY_CHOICES).get(most_recent_category['category']) if most_recent_category else 'دسته‌بندی ثبت نشده', 'color': 'red'},
            {'label': 'همه ip ها', 'value': total_hosts, 'color': 'red'},
            {'label': 'ip های استفاده شده', 'value': used_hosts, 'color': 'red'},
        ]
        
        return Response(summary_data, status=status.HTTP_200_OK)
    


class AssetInRangeMetaDataAPIView(BaseMetaDataAPIView):

    model = DiscoveredAsset
    fields_map = {field:field for field in config_discovered_asset['filters']}
    search_fields = config_discovered_asset['search']

class AssetInRangeListAPIView(APIView):

    permission_classes = [IsAuthenticated, DynamicSystemPermission]
    base_perm_name = 'ip_manage'

    def get(self, request, ip_id):

        accessible_queryset = get_accessible_queryset(request, model=IPManage)
        selected_range = get_object_or_404(accessible_queryset, id=ip_id)
        asset_by_range = DiscoveredAsset.objects.filter(network_range = selected_range)

        
        assets = apply_filters_and_sorting(
            request, 
            config_discovered_asset['sorting'], 
            config_discovered_asset['filters'], 
            config_discovered_asset['search'], 
            session_key='scanned_asset', 
            query_set=asset_by_range
        ).select_related('user', 'access_level')

        paginator = set_paginator(request, assets)
        serializer = serializers.AssetInManualyRangeListSerializer(paginator['data'], many=True)

        columns = serializers.AssetInManualyRangeListSerializer.get_active_columns()
        return Response({
            'results':serializer.data,
            'total_pages': paginator['total_pages'],
            'current_page': paginator['current_page'],
            'total_items': paginator['total_items'],
            'columns': columns
        }, status=status.HTTP_200_OK)


class AssetInRagneAPIView(APIView):

    permission_classes = [IsAuthenticated, DynamicSystemPermission]
    base_perm_name = 'ip_manage'

    def get(self, request, ip_id):
        
        config_form = serializers.AssetInManualyRangeUpdate.get_form_config()

        if ip_id:
            accessible_queryset = get_accessible_queryset(request, model=DiscoveredAsset)
            selected_asset = get_object_or_404(accessible_queryset, id= ip_id)
            serializer = serializers.AssetInManualyRangeDetail(selected_asset)

        return Response({
            'result':serializer.data if ip_id else {},
            'config_form': config_form
            }, status = status.HTTP_200_OK)
    
    
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

        discovered_assets = apply_filters_and_sorting(
            request, 
            config_discovered_asset['sorting'], 
            config_discovered_asset['filters'], 
            config_discovered_asset['search'], 
            session_key='hardware', 
            query_set=asset_by_range
        ).select_related('user', 'access_level')

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = 'دارایی های اسکن شد'
        ws.sheet_view.rightToLeft = True

        fields = [field for field in discovered_assets.model._meta.fields if field.name != 'id']
        header = header = [field.verbose_name for field in fields]
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

        wb.save(response)
        return response