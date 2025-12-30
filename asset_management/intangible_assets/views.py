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
from django.db.models import Q
from core.utils import apply_filters_and_sorting, get_accessible_queryset
from core.permissions import DynamicSystemPermission


class IntangibleAssetsListAPIView(APIView):

    permission_classes = [IsAuthenticated, DynamicSystemPermission]
    base_perm_name = 'intangible_assets'

    def get(self, request):

        sorting_fields = ['created_at', '-created-at', 'name']
        allowed_filters = ['location', 'organization', 'sub_organization', 'access_level', 'supplier']
        searching_fields = ['name', 'usage', 'owner', 'supplier']
        intangible_assets = apply_filters_and_sorting(request, sorting_fields, allowed_filters, searching_fields, session_key='intangible_assets', model=IntangibleAsset)

        serializer = serializers.ListSerializer(intangible_assets, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)



class IntangibleAssetsAPIView(APIView):

    permission_classes = [IsAuthenticated, DynamicSystemPermission]
    base_perm_name = 'intangible_assets'

    def get(self, request, intangible_asset_id):

        accessible_queryset = get_accessible_queryset(request, model=IntangibleAsset)
        intangible_asset = get_object_or_404(accessible_queryset, id = intangible_asset_id)
        serializer = serializers.DetailSerializer(intangible_asset)

        return Response(serializer.data, status=status.HTTP_200_OK)

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

        filters = request.session.get('places_and_areas_applied_filters', {})
        sorted_by = request.session.get('places_and_areas_sorted_by', '-created_at')
        accessible_queryset = get_accessible_queryset(request, model=IntangibleAsset)
        intangible_assets = accessible_queryset.filter(**filters).order_by(sorted_by)

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = 'درایی های نامشهود'

        fields = IntangibleAsset._meta.fields

        header = [field.verbose_name for field in fields]
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
        ws.sheet_view.rightToLeft = True
        wb.save(response)
        return response