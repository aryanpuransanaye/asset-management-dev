from rest_framework import permissions
from rest_framework.permissions import IsAuthenticated
from .models import InfrastructureAssets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from . import serializers
from django.shortcuts import get_object_or_404
import openpyxl, jdatetime
from django.http import HttpResponse
from django.db.models import Q, Count
from core.utils import apply_filters_and_sorting, get_accessible_queryset, set_paginator, BaseMetaDataAPIView
from core.permissions import DynamicSystemPermission
from .utils import get_infrastructure_asset_config


config = get_infrastructure_asset_config()



class InfrastructureAssetsSummaryAPIView(APIView):
    permission_classes = [IsAuthenticated, DynamicSystemPermission]
    base_perm_name = 'infrastructure_assets'

    def get(self, request):

        accessible_queryset = get_accessible_queryset(request, model=InfrastructureAssets)
        total_count = accessible_queryset.count()

        last_infrastructure_assets = accessible_queryset.order_by('-created_at').first()

        inftastructure_assets = accessible_queryset.aggregate(
            total_supplier = Count('supplier', distinct=True),
            total_owner = Count('owner', distinct=True),
        )

        summary_data = {
            {'label': 'تعداد کل', 'value': total_count, 'color': 'blue'},
            {'label': 'جدیدترین دارایی', 'value': last_infrastructure_assets.name if last_infrastructure_assets else 'دارایی ثبت نشده', 'color': 'grey'},
            {'label': 'تعداد تامین کننده', 'value': inftastructure_assets['total_supplier'], 'color': 'green'},
            {'label': 'تعداد مالک', 'value': inftastructure_assets['total_owner'], 'color': 'orange'},
        }

        return Response(summary_data, status=status.HTTP_200_OK)
    
    
class InfrastructureAssetsMetaDataAPIView(BaseMetaDataAPIView):

    model = InfrastructureAssets
    fields_map = {field:field for field in config['filters']}
    search_fields = config['search']


class InfrastructureAssetsListAPIView(APIView):

    permission_classes = [IsAuthenticated, DynamicSystemPermission]
    base_perm_name = 'infrastructure_assets'

    def get(self, request):

        infrastructure_assets = apply_filters_and_sorting(
            request, 
            config['sorting'], 
            config['filters'], 
            config['search'], 
            session_key='hardware', 
            model=InfrastructureAssets
        ).select_related(
            'organization', 
            'sub_organization', 
            'user', 
            'access_level'
        )

        paginator = set_paginator(request, infrastructure_assets)
        serializer = serializers.ListSerializer(paginator['data'], many=True)
        columns = serializers.ListSerializer.get_active_columns()
        return Response({
            'results':serializer.data,
            'total_pages': paginator['total_pages'],
            'current_page': paginator['current_page'],
            'total_items': paginator['total_items'],
            'columns': columns
        }, status=status.HTTP_200_OK)



class InfrastructureAssetsAPIView(APIView):

    permission_classes = [IsAuthenticated, DynamicSystemPermission]
    base_perm_name = 'infrastructure_assets'

    def get(self, request, infrastructure_asset_id):

        config_form = serializers.CreateUpdateSerializer.get_form_config()

        if infrastructure_asset_id:
            accessible_queryset = get_accessible_queryset(request, model=InfrastructureAssets)
            infrastructure_asset = get_object_or_404(accessible_queryset, id = infrastructure_asset_id)
            serializer = serializers.DetailSerializer(infrastructure_asset)

        return Response({
            'result':serializer.data if infrastructure_asset_id else {},
            'config_form': config_form
            }, status = status.HTTP_200_OK)

    def post(self, request):

        serializer = serializers.CreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user = request.user, access_level = request.user.access_level)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, infrastructure_asset_id):

        accessible_queryset = get_accessible_queryset(request, model=InfrastructureAssets)
        infrastructure_asset = get_object_or_404(accessible_queryset, id = infrastructure_asset_id)
        
        serializer = serializers.CreateUpdateSerializer(infrastructure_asset, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, *args, **kwargs):
        
        ids_to_delete = request.data.get('ids', [])
        if not ids_to_delete:
            return Response({'errors': 'there is not id to delete'}, status=status.HTTP_400_BAD_REQUEST)
        
        accessible_queryset = get_accessible_queryset(request, model=InfrastructureAssets)
        infrastructure_assets = accessible_queryset.filter(id__in = ids_to_delete)

        if not infrastructure_assets.exists():
            return Response({'errors': "not found anything to delete"}, status=status.HTTP_404_NOT_FOUND)
        
        deleted_count, _ = infrastructure_assets.delete()

        return Response({'message': f"{deleted_count} things are deleted"}, status=status.HTTP_200_OK)
    


class InfrastructureAssetsExportAPIView(APIView):
    
    permission_classes = [IsAuthenticated, DynamicSystemPermission]
    base_perm_name = 'infrastructure_assets'

    def get(self, request):

        infrastructure_assets = apply_filters_and_sorting(
            request, 
            config['sorting'], 
            config['filters'], 
            config['search'], 
            session_key='hardware', 
            model=InfrastructureAssets
        ).select_related(
            'organization', 
            'sub_organization', 
            'user', 
            'access_level'
        )

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = 'درایی های زیرساختی'
        ws.sheet_view.rightToLeft = True

        fields = InfrastructureAssets._meta.fields

        header = [field.verbose_name for field in fields]
        ws.append(header)
        
        for thing in infrastructure_assets:
            row = []
            for field in fields:
                value = getattr(thing, field.name)

                if field.name == 'user' and value:
                    value = value.username
                elif field.name == 'access_level' and value:
                    value = value.level_name
                elif field.name == 'organization' and value:
                    value = value.organization.name
                elif field.name == 'sub_organization' and value:
                    value = value.sub_organization.name
                elif field.name in ['created_at', 'updated_at'] and value:
                    value = jdatetime.datetime.fromgregorian(datetime=value).strftime('%Y/%m/%d %H:%M')

                row.append(value if value else '-')
            ws.append(row)

        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="infrastructure_asset.xlsx"'
        wb.save(response)
        return response