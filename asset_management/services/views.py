from rest_framework import permissions
from rest_framework.permissions import IsAuthenticated
from .models import Services
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
from .utils import get_service_config

config = get_service_config()


class ServicesSummaryAPIView(APIView):

    permission_classes = [IsAuthenticated, DynamicSystemPermission]
    base_perm_name = 'services'

    def get(self, request):

        accessible_queryset = get_accessible_queryset(request, model=Services)

        total_services = accessible_queryset.count()
        recent_item = accessible_queryset.order_by('-created_at').first()

        summary_data = [
            {'label': 'تعداد سرویس‌ها', 'value': total_services, 'color': 'blue'},
            {'label': 'جدیدترین', 'value': recent_item.ipaddress if recent_item and recent_item.ipaddress else 'بدون ip آدرس', 'color' : 'pink'}
        ]

        return Response(summary_data, status=status.HTTP_200_OK)


class ServicesMetaDataAPIView(BaseMetaDataAPIView):

    model = Services
    fields_map = {field:field for field in config['filters']}
    search_fields = config['search']

class ServicesListAPIView(APIView):

    permission_classes = [IsAuthenticated, DynamicSystemPermission]
    base_perm_name = 'services'

    def get(self, request):

        services = apply_filters_and_sorting(
            request, 
            config['sorting'], 
            config['filters'], 
            config['search'], 
            session_key='hardware', 
            model=Services
        ).select_related(
            'organization', 
            'sub_organization', 
            'user', 
            'access_level'
        )

        paginator = set_paginator(request, services)
        serializer = serializers.ListSerializer(paginator['data'], many=True)
        columns = serializers.ListSerializer.get_active_columns()
        return Response({
            'results':serializer.data,
            'total_pages': paginator['total_pages'],
            'current_page': paginator['current_page'],
            'total_items': paginator['total_items'],
            'columns': columns
        }, status=status.HTTP_200_OK)


class ServicesAPIView(APIView):

    permission_classes = [IsAuthenticated, DynamicSystemPermission]
    base_perm_name = 'services'

    def get(self, request, service_id=None):

        config_form = serializers.CreateUpdateSerializer.get_form_config()

        if service_id:
            accessible_queryset = get_accessible_queryset(request, model=Services)
            service = get_object_or_404(accessible_queryset, id = service_id)
            serializer = serializers.DetailSerializer(service)
        
        return Response({
            'result':serializer.data if service_id else {},
            'config_form': config_form
            }, status = status.HTTP_200_OK)

    def post(self, request):

        serializer = serializers.CreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user = request.user, access_level = request.user.access_level)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, service_id):

        accessible_queryset = get_accessible_queryset(request, model=Services)
        service = get_object_or_404(accessible_queryset, id=service_id)
        
        serializer = serializers.CreateUpdateSerializer(service, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, *args, **kwargs):
        
        ids_to_delete = request.data.get('ids', [])
        if not ids_to_delete:
            return Response({'errors': 'there is not id to delete'}, status=status.HTTP_400_BAD_REQUEST)
        
        accessible_queryset = get_accessible_queryset(request, model=Services)
        services = accessible_queryset.filter(id__in = ids_to_delete)

        if not services.exists():
            return Response({'errors': "not found anything to delete"}, status=status.HTTP_404_NOT_FOUND)
        
        deleted_count, _ = services.delete()

        return Response({'message': f"{deleted_count} things are deleted"}, status=status.HTTP_200_OK)
    


class ServicesExportAPIView(APIView):
    
    permission_classes = [IsAuthenticated, DynamicSystemPermission]
    base_perm_name = 'services'

    def get(self, request):

        services = apply_filters_and_sorting(
            request, 
            config['sorting'], 
            config['filters'], 
            config['search'], 
            session_key='hardware', 
            model=Services
        ).select_related(
            'organization', 
            'sub_organization', 
            'user', 
            'access_level'
        )

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = 'سرویس ها'

        fields = [field for field in Services._meta.fields if field.name != 'id']

        header = [field.verbose_name for field in fields]
        ws.append(header)
        
        for thing in services:
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
                elif field.name in ['created_at', 'updated_at'] and value:
                    value = jdatetime.datetime.fromgregorian(datetime=value).strftime('%Y/%m/%d %H:%M')

                row.append(value if value else '-')
            ws.append(row)

        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="services.xlsx"'
        ws.sheet_view.rightToLeft = True
        wb.save(response)
        return response