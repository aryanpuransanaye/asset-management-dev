from rest_framework import permissions
from rest_framework.permissions import IsAuthenticated
from .models import IntangibleAsset
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
from .utils import get_intangible_asset_config

config = get_intangible_asset_config()


class IntangibleAssetsSummaryAPIView(APIView):

    permission_classes = [IsAuthenticated, DynamicSystemPermission]
    base_perm_name = 'intangible_assets'

    def get(self, request):

        accessible_queryset = get_accessible_queryset(request, model=IntangibleAsset)

        total_count = accessible_queryset.count()

        intangible_asset = accessible_queryset.aggregate(
            supplier_count = Count('supplier', distinct=True),
            owner_count = Count('owner', distinct=True),
        )

        last_intangible_asset = accessible_queryset.order_by('-created_at').first()

        summary_data = [
            {'label': 'تعداد کل', 'value': total_count, 'color': 'blue'},
            {'label': 'تعداد تامین کننده', 'value': intangible_asset['supplier_count'], 'color': 'green'},
            {'label': 'تعداد مالک', 'value': intangible_asset['owner_count'], 'color': 'orange'},
            {'label': 'جدیدترین دارایی', 'value': last_intangible_asset.name if last_intangible_asset else 'دارایی ثبت نشده', 'color': 'grey'},
        ]

        return Response(summary_data, status=status.HTTP_200_OK)

class IntangibleAssetsMetaDataAPIView(BaseMetaDataAPIView):

    model = IntangibleAsset
    fields_map = {field:field for field in config}
    search_fields = config['search']


class IntangibleAssetsListAPIView(APIView):

    permission_classes = [IsAuthenticated, DynamicSystemPermission]
    base_perm_name = 'intangible_assets'

    def get(self, request):

        
        intangible_assets = apply_filters_and_sorting(
            request, 
            config['sorting'], 
            config['filters'], 
            config['search'], 
            session_key='hardware', 
            model=IntangibleAsset
        ).select_related(
            'organization', 
            'sub_organization', 
            'user', 
            'access_level'
        )

        paginator = set_paginator(request, intangible_assets)
        serializer = serializers.ListSerializer(paginator['data'], many=True)
        columns = serializers.ListSerializer.get_active_columns()
        return Response({
            'results':serializer.data,
            'total_pages': paginator['total_pages'],
            'current_page': paginator['current_page'],
            'total_items': paginator['total_items'],
            'columns': columns
        }, status=status.HTTP_200_OK)



class IntangibleAssetsAPIView(APIView):

    permission_classes = [IsAuthenticated, DynamicSystemPermission]
    base_perm_name = 'intangible_assets'

    def get(self, request, intangible_asset_id=None):

        config_form = serializers.CreateUpdateSerializer.get_form_config()

        if intangible_asset_id:
            accessible_queryset = get_accessible_queryset(request, model=IntangibleAsset)
            intangible_asset = get_object_or_404(accessible_queryset, id = intangible_asset_id)
            serializer = serializers.DetailSerializer(intangible_asset)

        return Response({
            'result':serializer.data if intangible_asset_id else {},
            'config_form': config_form
            }, status = status.HTTP_200_OK)

    def post(self, request):

        serializer = serializers.CreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user = request.user, access_level = request.user.access_level)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, intangible_asset_id):

        accessible_queryset = get_accessible_queryset(request, model=IntangibleAsset)
        intangible_asset = get_object_or_404(accessible_queryset, id = intangible_asset_id)
        
        serializer = serializers.CreateUpdateSerializer(intangible_asset, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, *args, **kwargs):
        
        ids_to_delete = request.data.get('ids', [])
        if not ids_to_delete:
            return Response({'errors': 'there is not id to delete'}, status=status.HTTP_400_BAD_REQUEST)
        
        accessible_queryset = get_accessible_queryset(request, model=IntangibleAsset)
        intangible_assets = accessible_queryset.filter(id__in = ids_to_delete)

        if not intangible_assets.exists():
            return Response({'errors': "not found anything to delete"}, status=status.HTTP_404_NOT_FOUND)
        
        deleted_count, _ = intangible_assets.delete()

        return Response({'message': f"{deleted_count} things are deleted"}, status=status.HTTP_200_OK)
    


class IntangibleAssetsExportAPIView(APIView):
    
    permission_classes = [IsAuthenticated, DynamicSystemPermission]
    base_perm_name = 'intangible_assets'

    def get(self, request):

        intangible_assets = apply_filters_and_sorting(
            request, 
            config['sorting'], 
            config['filters'], 
            config['search'], 
            session_key='hardware', 
            model=IntangibleAsset
        ).select_related(
            'organization', 
            'sub_organization', 
            'user', 
            'access_level'
        )
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = 'درایی های نامشهود'
        ws.sheet_view.rightToLeft = True

        fields = [field for field in IntangibleAsset._meta.fields if field.name != 'id']

        header = header = [field.verbose_name for field in fields]
        ws.append(header)
        
        for thing in intangible_assets:
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
        response['Content-Disposition'] = 'attachment; filename="intangible_asset.xlsx"'
 
        wb.save(response)
        return response