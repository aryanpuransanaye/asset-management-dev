from rest_framework import permissions
from rest_framework.permissions import IsAuthenticated
from .models import Hardware
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from . import serializers
from django.shortcuts import get_object_or_404
import openpyxl, jdatetime
from django.http import HttpResponse
from django.db.models import Q
from core.utils import apply_filters_and_sorting, get_accessible_queryset, set_paginator, BaseMetaDataAPIView
from core.permissions import DynamicSystemPermission
from .utils import get_hardware_config


config = get_hardware_config()
class HardwareMetaDataAPIView(BaseMetaDataAPIView):

    model = Hardware
    fields_map = {field:field for field in config['filters']}
    search_fields = config['search']
    

class HardwareListAPIView(APIView):
     
    permission_classes = [IsAuthenticated, DynamicSystemPermission]
    base_perm_name = 'hardware'

    def get(self, request):

        hardwares = apply_filters_and_sorting(
            request, 
            config['sorting'], 
            config['filters'], 
            config['search'], 
            session_key='hardware', 
            model=Hardware
        ).select_related(
            'organization', 
            'sub_organization', 
            'user', 
            'access_level'
        )

        paginator = set_paginator(request, hardwares)
        serializer = serializers.ListSerializer(paginator['data'], many=True)
        columns = serializers.ListSerializer.get_active_columns()
        return Response({
            'results':serializer.data,
            'total_pages': paginator['total_pages'],
            'current_page': paginator['current_page'],
            'total_items': paginator['total_items'],
            'columns': columns
        }, status=status.HTTP_200_OK)

class HardwareAPIView(APIView):

    permission_classes = [IsAuthenticated, DynamicSystemPermission]
    base_perm_name = 'hardware'

    def get(self, request, hardware_id=None):

        config_form = serializers.CreateUpdateSerializer.get_form_config()

        if hardware_id:
            accessible_queryset = get_accessible_queryset(request, model=Hardware)
            hardware = get_object_or_404(accessible_queryset, id = hardware_id)
            serializer = serializers.DetailSerializer(hardware)

        return Response({
            'result':serializer.data if hardware_id else {},
            'config_form': config_form
            }, status = status.HTTP_200_OK)
    
    def post(self, request):
        
        serializer = serializers.CreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user = request.user, access_level = request.user.access_level)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def patch(self, request, hardware_id):

        accessible_queryset = get_accessible_queryset(request, model=Hardware)
        selected_hardware = get_object_or_404(accessible_queryset, id = int(hardware_id))

        serializer = serializers.CreateUpdateSerializer(selected_hardware, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
    def delete(self, request, *args, **kwargs):

        ids_to_delete = request.data.get('ids', [])
        if not ids_to_delete:
            return Response({'errors': 'there is not id to delete'}, status=status.HTTP_400_BAD_REQUEST)
        
        accessible_queryset = get_accessible_queryset(request, model=Hardware)
        hardwares = accessible_queryset.filter(id__in = ids_to_delete)

        if not hardwares.exists():
            return Response({'errors': "not found anything to delete"}, status=status.HTTP_404_NOT_FOUND)
        
    
        deleted_count, _ = hardwares.delete()

        return Response({'message': f"{deleted_count} things are deleted"}, status=status.HTTP_200_OK)
    

class HardwareExportAPIView(APIView):
    
    permission_classes = [IsAuthenticated, DynamicSystemPermission]
    base_perm_name = 'hardware'

    def get(self, request):


        hardwares = apply_filters_and_sorting(
            request, 
            config['sorting'], 
            config['filters'], 
            config['search'], 
            session_key='hardware', 
            model=Hardware
        ).select_related(
            'organization', 
            'sub_organization', 
            'user', 
            'access_level'
        )

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = 'سخت افزار'

        fields = Hardware._meta.fields

        header = [field.verbose_name for field in fields]
        ws.sheet_view.rightToLeft = True
        ws.append(header)
        
        for thing in hardwares:
            row = []
            for field in fields:
                value = getattr(thing, field.name)

                if field.name == 'user' and value:
                        value = value.username
                elif field.name == 'access_level' and value:
                        value = value.level_name
                elif field.name == 'organization' and value:
                        value = value.name
                elif field.name == 'sub_organization' and value:
                        value = value.name
                elif field.name == 'created_at' and value:
                    value = jdatetime.datetime.fromgregorian(datetime=value).strftime('%Y/%m/%d %H:%M')
                elif field.name == 'updated_at' and value:
                    value = jdatetime.datetime.fromgregorian(datetime=value).strftime('%Y/%m/%d %H:%M')

                row.append(value if value else '-')
            ws.append(row)

        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="Hardware.xlsx"'
        wb.save(response)
        return response